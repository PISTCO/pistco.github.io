"""Regression checks for the private/public boundary, rendering, and publishing gate."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

import build
import publish


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.draft = self.root / 'draft'
        (self.draft / 'content').mkdir(parents=True)
        (self.draft / 'media').mkdir()
        local = {k: 'Test ' + k for k in build.PROFILE_FIELDS}
        self.profile = {'name': 'PISTCO', 'github': 'https://github.com/PISTCO', 'locales': {'ko': local.copy(), 'en': local.copy()}}
        self.project = {'id': 'test-project', 'order': 1, 'example': True, 'image': None, 'url': None, 'locales': {lang: {'title': 'Example', 'description': 'Test description', 'alt': ''} for lang in ('ko', 'en')}}
        self.projects = [self.project]

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        for name, value in [('profile', self.profile), ('projects', self.projects)]:
            (self.draft / 'content' / (name + '.json')).write_text(json.dumps(value), encoding='utf-8')

    def render(self):
        self.save()
        out = self.root / 'output'
        build.build(self.draft, out)
        return out

    def image(self, filename='test.png', fmt='PNG'):
        path = self.draft / 'media' / filename
        Image.new('RGB', (12, 10), 'blue').save(path, format=fmt)
        self.project['image'] = 'media/' + filename
        for content in self.project['locales'].values():
            content['alt'] = 'Example image'
        return path

    def test_private_files_and_unused_images_never_export(self):
        (self.draft / 'PRIVATE_CHECK.txt').write_text('NEVER-PUBLIC')
        (self.draft / 'media/unused.svg').write_text('<script>NEVER-PUBLIC</script>')
        out = self.render()
        files = publish.collect_output(out)
        self.assertEqual(set(files), publish.STATIC_FILES)
        self.assertNotIn(b'NEVER-PUBLIC', b''.join(files.values()))

    def test_html_is_text_not_executable(self):
        self.project['locales']['ko']['title'] = '<script>alert(1)</script>'
        result = (self.render() / 'ko/index.html').read_text(encoding='utf-8')
        self.assertIn('&lt;script&gt;', result)
        self.assertNotIn('<script>', result)

    def test_dangerous_and_credential_urls_rejected(self):
        for url in ('javascript:alert(1)', 'data:text/html,test', 'http://example.com', 'https://a:b@example.com', 'https://example.com\\evil', 'https://example.com\n'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                build.https_url(url)

    def test_missing_translation_rejected(self):
        del self.project['locales']['en']
        with self.assertRaises(ValueError):
            self.render()
        self.assertFalse((self.root / 'output').exists())

    def test_path_escape_rejected(self):
        for name in ('../secret.png', '/secret.png', 'media/../secret.png', 'media\\test.png', 'C:/secret.png'):
            with self.subTest(path=name), self.assertRaises(ValueError):
                build.safe_file(self.draft, name)

    def test_symlink_rejected(self):
        target = self.root / 'secret.png'
        Image.new('RGB', (1, 1)).save(target)
        link = self.draft / 'media/link.png'
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest('OS does not permit this process to create a symlink')
        with self.assertRaises(ValueError):
            build.safe_file(self.draft, 'media/link.png')

    def test_fake_image_rejected(self):
        path = self.image()
        path.write_text('<html><script>alert(1)</script></html>')
        with self.assertRaises(Exception):
            self.render()
        self.assertFalse((self.root / 'output').exists())

    def test_format_mismatch_and_oversize_rejected(self):
        path = self.image('wrong.png', 'JPEG')
        with self.assertRaises(ValueError):
            build.normalized_image(path)
        path.write_bytes(b'x' * (build.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            build.normalized_image(path)

    def test_images_reencoded_without_metadata(self):
        path = self.image('photo.jpg', 'JPEG')
        exif = Image.Exif()
        exif[270] = 'PRIVATE-EXIF-MARKER'
        Image.new('RGB', (12, 10), 'blue').save(path, exif=exif)
        out = self.render()
        images = list((out / 'assets/media').glob('*.webp'))
        self.assertEqual(len(images), 1)
        with Image.open(images[0]) as result:
            self.assertFalse(result.getexif())
        self.assertNotIn(b'PRIVATE-EXIF-MARKER', images[0].read_bytes())

    def test_duplicate_ids_orders_missing_image_rejected(self):
        self.projects.append(copy.deepcopy(self.project))
        with self.assertRaises(ValueError):
            self.render()
        self.projects.pop()
        self.project['image'] = 'media/missing.png'
        for locale in self.project['locales'].values():
            locale['alt'] = 'Missing'
        with self.assertRaises(ValueError):
            self.render()

    def test_existing_output_never_overwritten(self):
        self.save()
        out = self.root / 'output'
        out.mkdir()
        (out / 'keep.txt').write_text('keep')
        with self.assertRaises(ValueError):
            build.build(self.draft, out)
        self.assertEqual((out / 'keep.txt').read_text(), 'keep')

    def test_publication_output_allowlist(self):
        out = self.render()
        (out / 'private.json').write_text('SECRET')
        with self.assertRaises(ValueError):
            publish.collect_output(out)

    def test_owner_manual_main_and_confirmation_all_required(self):
        env = {'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REPOSITORY': 'PISTCO/pistco-site-content', 'GITHUB_REF': 'refs/heads/main', 'GITHUB_ACTOR_ID': '220297881', 'GITHUB_TRIGGERING_ACTOR': 'PISTCO', 'CONFIRM_PUBLICATION': 'true'}
        self.assertTrue(publish.authorized(env))
        for field in env:
            denied = dict(env, **{field: 'not-authorized'})
            self.assertFalse(publish.authorized(denied), field)

    def test_publication_preserves_non_site_files_and_removes_old_media(self):
        changes = publish.tree_changes({'README.md': 'a', '.github/workflows/test.yml': 'b', 'docs/old.png': 'c', 'docs/index.html': publish.git_sha(b'old')}, {'index.html': b'new'})
        self.assertEqual(changes, [('docs/index.html', b'new'), ('docs/old.png', None)])


if __name__ == '__main__':
    unittest.main()
