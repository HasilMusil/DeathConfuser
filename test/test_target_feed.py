import sys
from pathlib import Path
import unittest
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core import target_feed


class TargetFeedTest(unittest.IsolatedAsyncioTestCase):
    async def test_update_targets(self):
        async def fake_fetch(session, url):
            return [{"in_scope": True, "tech": ["npm"], "url": "https://example.com"}]
        target_feed._fetch_json = fake_fetch
        tmp = Path(self._testMethodName + "_targets.txt")
        await target_feed.update_target_file(tmp)
        self.assertTrue(tmp.exists())
        self.assertIn("https://example.com", tmp.read_text())
        tmp.unlink()

if __name__ == '__main__':
    unittest.main()
