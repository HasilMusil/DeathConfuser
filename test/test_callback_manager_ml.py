import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.callback_manager import CallbackManager


class CallbackManagerMLTest(unittest.TestCase):
    def test_auto_severity(self):
        mgr = CallbackManager(Path('cm_tmp_ml'))
        mgr.record('t', 'npm', 'h1', data={'message': 'root password leak'})
        self.assertEqual(mgr.events[0].severity, 'critical')
        for p in Path('cm_tmp_ml').iterdir():
            p.unlink()
        Path('cm_tmp_ml').rmdir()

if __name__ == '__main__':
    unittest.main()
