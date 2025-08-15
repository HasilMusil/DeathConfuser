import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.opsec.infra_manager import InfraManager


class InfraManagerTest(unittest.IsolatedAsyncioTestCase):
    async def test_generate_burner_identity(self):
        mgr = InfraManager()
        ident = await mgr.generate_burner_identity()
        self.assertIn('@', ident['email'])
        self.assertIn('user_agent', ident)

if __name__ == '__main__':
    unittest.main()
