import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.registry_monitor import monitor
from DeathConfuser.sim.registry import FakeRegistry


class RegistryMonitorTest(unittest.TestCase):
    def test_monitor(self):
        reg = FakeRegistry()
        claimed = asyncio.run(monitor(reg, ['a', 'b']))
        self.assertEqual(claimed, ['a', 'b'])

if __name__ == '__main__':
    unittest.main()
