"""Release manifest and archive inspection reject unapproved members."""
import tempfile
import unittest
from pathlib import Path
import zipfile

from scripts.verify_release import inspect_wheel, manifest, safe_name


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

    def test_unknown_archive_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.whl'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('private/secret.txt','SYNTHETIC_CANARY')
            with self.assertRaisesRegex(ValueError,'unexpected_wheel_member'):
                inspect_wheel(path,{'LICENSE-NOTES.md':b'pending'})
        for name in ['../secret','/private/file','x/../secret','x\\secret','']:
            self.assertFalse(safe_name(name))
