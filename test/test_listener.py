import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.listener import Listener


class ListenerTest(unittest.TestCase):
    def test_start(self):
        lst = Listener()
        url = asyncio.run(lst.start())
        self.assertIn('http://', url)

if __name__ == '__main__':
    unittest.main()
