import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.modules.npm import publisher


class PublishParallelTest(unittest.IsolatedAsyncioTestCase):
    async def test_publish_parallel(self):
        async def fake_is_unclaimed(self, name):
            return True
        publisher.Scanner.is_unclaimed = fake_is_unclaimed
        async def fake_identity(self):
            return {"name": "a", "email": "b@example.com", "user_agent": "UA", "version": "1.0.0", "delay": 0}
        publisher.InfraManager.generate_burner_identity = fake_identity
        await publisher.publish_parallel([("pkg1", "{}"), ("pkg2", "{}")], dry_run=True)

if __name__ == '__main__':
    unittest.main()
