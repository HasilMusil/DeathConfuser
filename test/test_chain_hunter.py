import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.chain_hunter import hunt


class ChainHunterTest(unittest.TestCase):
    def test_hunt(self):
        res = asyncio.run(hunt('org'))
        self.assertIn('org-dev', res)

if __name__ == '__main__':
    unittest.main()
