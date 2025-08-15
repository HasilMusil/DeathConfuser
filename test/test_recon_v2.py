import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.recon_v2 import ReconEngineV2


class ReconV2Test(unittest.TestCase):
    def test_run(self):
        recon = ReconEngineV2()
        res = asyncio.run(recon.run(['https://example.org']))
        self.assertTrue(res and res[0].packages)

if __name__ == '__main__':
    unittest.main()
