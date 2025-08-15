import sys
from pathlib import Path
import unittest
import json

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.callback_manager import CallbackManager


class CallbackManagerTest(unittest.TestCase):
    def test_record_and_save(self):
        tmp_dir = Path('cm_tmp')
        mgr = CallbackManager(tmp_dir)
        mgr.record('target', 'npm', 'h1', 'high', {'k': 'v'})
        path = mgr.save()
        data = json.loads(path.read_text())[0]
        self.assertEqual(data['target'], 'target')
        # cleanup
        for p in tmp_dir.iterdir():
            p.unlink()
        tmp_dir.rmdir()

if __name__ == '__main__':
    unittest.main()
