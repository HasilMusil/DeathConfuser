import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.chain_builder import build_chain


class ChainBuilderTest(unittest.TestCase):
    def test_build(self):
        steps = asyncio.run(build_chain({'target': 't', 'package': 'p'}))
        self.assertIn('pivot', ' '.join(steps))

if __name__ == '__main__':
    unittest.main()
