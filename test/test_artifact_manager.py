import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.artifact_manager import ArtifactManager


class ArtifactManagerTest(unittest.TestCase):
    def test_save(self):
        mgr = ArtifactManager('artifacts_test')
        p = mgr.save_text('demo', 'data')
        self.assertTrue(p.exists())
        # cleanup
        for f in p.parent.iterdir():
            f.unlink()
        p.parent.rmdir()

if __name__ == '__main__':
    unittest.main()
