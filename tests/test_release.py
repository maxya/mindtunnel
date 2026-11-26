"""Release manifest and archive inspection reject unapproved members."""
import tempfile
import unittest
from pathlib import Path
import zipfile

from scripts.verify_release import inspect_wheel, manifest, safe_name, verify_license_metadata


class ReleaseManifest(unittest.TestCase):
    def test_manifest_excludes_private_and_generated_artifacts(self):
        names = manifest()
        for name in names:
            self.assertTrue(safe_name(name))
            self.assertNotIn(name.split('/')[0], ['private','work','.git','.env','dist','build'])
            self.assertNotIn('release-verification',name)
        self.assertIn('examples/transactions.csv',names)
        self.assertIn('schemas/plan-v1.schema.json',names)
        self.assertIn('harness/release-files.txt',names)
        self.assertIn('LICENSE', names)

    def test_license_metadata_requires_spdx_and_file(self):
        valid = b'Metadata-Version: 2.4\nLicense-Expression: MIT\nLicense-File: LICENSE\n'
        verify_license_metadata(valid)
        for invalid in (b'', valid.replace(b'MIT', b'Apache-2.0'), valid.replace(b'LICENSE', b'NOTICE')):
            with self.subTest(metadata=invalid), self.assertRaisesRegex(ValueError, '^invalid_license_metadata$'):
                verify_license_metadata(invalid)

    def test_unknown_archive_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.whl'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('private/secret.txt','SYNTHETIC_CANARY')
            with self.assertRaisesRegex(ValueError,'unexpected_wheel_member'):
                inspect_wheel(path,{'LICENSE':b'MIT License'})
        for name in ['../secret','/private/file','x/../secret','x\\secret','']:
            self.assertFalse(safe_name(name))
