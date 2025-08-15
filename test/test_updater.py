import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.updater import update_modules


class UpdaterTest(unittest.TestCase):
    def test_update(self):
        res = asyncio.run(update_modules('origin', Path('.')))
        self.assertIsInstance(res, bool)

if __name__ == '__main__':
    unittest.main()
