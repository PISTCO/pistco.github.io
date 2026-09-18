"""Publish a validated output tree using an ephemeral, repository-scoped App token."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPOSITORY = 'PISTCO/pistco.github.io'
OWNER_ID = '220297881'
STATIC_FILES = {'index.html', '404.html', '.nojekyll', 'assets/styles.css', 'admin/index.html', 'ko/index.html', 'en/index.html'}


def authorized(env):
    return (env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
            and env.get('GITHUB_REPOSITORY') == 'PISTCO/pistco-site-content'
            and env.get('GITHUB_REF') == 'refs/heads/main'
            and env.get('GITHUB_ACTOR_ID') == OWNER_ID
            and env.get('GITHUB_TRIGGERING_ACTOR') == 'PISTCO'
            and env.get('CONFIRM_PUBLICATION') == 'true')


def collect_output(folder):
    files = {}
    for path in folder.rglob('*'):
        if path.is_symlink():
            raise ValueError('Symlink in output')
        if path.is_file():
            rel = path.relative_to(folder).as_posix()
            if rel not in STATIC_FILES and not re.fullmatch(r'assets/media/[a-f0-9]{64}\.webp', rel):
                raise ValueError('Unexpected output file')
            files[rel] = path.read_bytes()
    if not STATIC_FILES.issubset(files):
        raise ValueError('Missing output file')
    return files


def git_sha(payload):
    return hashlib.sha1(b'blob ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()


def tree_changes(existing, files):
    desired = {'docs/' + name: data for name, data in files.items()}
    changes = []
    for path, payload in desired.items():
        if existing.get(path) != git_sha(payload):
            changes.append((path, payload))
    for path in existing:
        if path.startswith('docs/') and path not in desired:
            changes.append((path, None))
    return changes


def main(folder):
    if not authorized(os.environ):
        raise PermissionError('Only the owner may publish a manually confirmed main-branch draft')
    token = os.environ.get('PUBLISH_TOKEN')
    if not token:
        raise PermissionError('Publishing App is not configured')
    files = collect_output(Path(folder))

    def api(method, route, body=None):
        req = Request('https://api.github.com/repos/' + REPOSITORY + route,
                      data=None if body is None else json.dumps(body).encode(), method=method,
                      headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'pistco-site-publisher', 'Content-Type': 'application/json'})
        with urlopen(req, timeout=30) as response:
            return json.load(response)

    head = api('GET', '/git/ref/heads/main')['object']['sha']
    tree_sha = api('GET', '/git/commits/' + head)['tree']['sha']
    tree = api('GET', '/git/trees/' + tree_sha + '?recursive=1')
    if tree.get('truncated'):
        raise ValueError('Repository tree is truncated; refusing partial publication')
    existing = {f['path']: f['sha'] for f in tree['tree'] if f['type'] == 'blob'}
    entries = []
    for path, payload in tree_changes(existing, files):
        sha = None
        if payload is not None:
            sha = api('POST', '/git/blobs', {'encoding': 'base64', 'content': base64.b64encode(payload).decode()})['sha']
        entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': sha})
    published = head
    if entries:
        new_tree = api('POST', '/git/trees', {'base_tree': tree_sha, 'tree': entries})['sha']
        published = api('POST', '/git/commits', {'message': 'Publish approved bilingual portfolio', 'tree': new_tree, 'parents': [head]})['sha']
        # A concurrent update rejects this non-fast-forward change. Never force or retry over it.
        api('PATCH', '/git/refs/heads/main', {'sha': published, 'force': False})
    summary = Path(os.environ['GITHUB_STEP_SUMMARY'])
    with summary.open('a', encoding='utf-8') as stream:
        stream.write(f'## Publication\n- Private draft: `{os.environ["GITHUB_SHA"]}`\n- Engine: `{os.environ.get("ENGINE_SHA", "unknown")}`\n- Public commit: `{published}`\n- Site: https://pistco.github.io/\n')
    expected = {k: v for k, v in files.items() if k != '.nojekyll'}
    for attempt in range(36):
        ready = True
        for name, body in expected.items():
            try:
                with urlopen('https://pistco.github.io/' + name + '?publication=' + published, timeout=20) as response:
                    if response.read() != body:
                        ready = False
                        break
            except (HTTPError, OSError):
                ready = False
                break
        if ready:
            with summary.open('a', encoding='utf-8') as stream:
                stream.write('- Verification: all public files match this publication.\n')
            print('Public site verified. Publication complete.')
            return
        if attempt < 35:
            time.sleep(10)
    raise RuntimeError('Public commit saved, but Pages verification timed out; inspect the public Pages deployment before retrying')


if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1])
    except Exception as error:
        # The exception type is sufficient; HTTP bodies and credentials never enter logs.
        print(f'Publication stopped ({type(error).__name__}). Check permissions, concurrent updates, and Pages status.')
        raise SystemExit(1)
