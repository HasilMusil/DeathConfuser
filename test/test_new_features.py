import sys
from pathlib import Path
import unittest
import asyncio
import json

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DeathConfuser.core import ml
from DeathConfuser.core.recon_v2 import ReconEngineV2
from DeathConfuser.core.listener import Listener
from DeathConfuser.core.artifact_manager import ArtifactManager
from DeathConfuser.core.registry_monitor import RegistryMonitor
from DeathConfuser.core.chain_builder import ChainBuilder
from DeathConfuser.core.updater import Updater
from DeathConfuser.core.scope_filter import ScopeFilter
from DeathConfuser.core.chain_hunter import ChainHunter
from DeathConfuser.plugins.plugin_api import Plugin, load_plugins
from DeathConfuser.sim.fake_registry import FakeRegistry


class MLTest(unittest.TestCase):
    def test_predict_and_classify(self):
        variants = ml.predict_package_variants('pkg_name')
        self.assertIn('pkg-name', variants)
        sev = ml.classify_callback_severity({'error': 'boom'})
        self.assertEqual(sev, 'high')


class ReconV2Test(unittest.IsolatedAsyncioTestCase):
    async def test_run(self):
        tmp = Path('recon_tmp'); tmp.mkdir()
        (tmp / 'index.js').write_text("require('private_pkg')")
        engine = ReconEngineV2()
        pkgs = await engine.run([tmp])
        self.assertIn('private_pkg', pkgs)
        for p in tmp.iterdir(): p.unlink()
        tmp.rmdir()


class ListenerTest(unittest.IsolatedAsyncioTestCase):
    async def test_listener(self):
        listener = Listener()
        base = await listener.start()
        url, token = listener.generate_callback_url(base)
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={'a': 1})
        await listener.stop()
        self.assertTrue(listener.callbacks)


class ArtifactManagerTest(unittest.TestCase):
    def test_save(self):
        mgr = ArtifactManager('art_tmp')
        path = mgr.save_text('a.txt', 'hi')
        self.assertTrue(path.exists())
        path.unlink(); Path('art_tmp').rmdir()


class RegistryMonitorTest(unittest.IsolatedAsyncioTestCase):
    async def test_watch(self):
        reg = FakeRegistry()
        monitor = RegistryMonitor(reg)
        claimed = []
        async def claim(name):
            claimed.append(name)
            await reg.claim(name)
        await monitor.watch(['x'], claim)
        self.assertEqual(claimed, ['x'])


class ChainBuilderTest(unittest.TestCase):
    def test_build(self):
        cb = ChainBuilder()
        steps = cb.build({'vuln': 'pkg takeover'})
        self.assertTrue(any('pkg' in s for s in steps))


class UpdaterTest(unittest.IsolatedAsyncioTestCase):
    async def test_pull(self):
        upd = Updater(Path('.'))
        await upd.pull()


class ScopeFilterTest(unittest.TestCase):
    def test_scope(self):
        sf = ScopeFilter(['example.com'])
        self.assertTrue(sf.in_scope('http://a.example.com'))
        self.assertFalse(sf.in_scope('http://evil.com'))


class ChainHunterTest(unittest.IsolatedAsyncioTestCase):
    async def test_hunt(self):
        tmp = Path('hunt_tmp'); tmp.mkdir()
        (tmp/'a.txt').write_text('package')
        hunter = ChainHunter()
        res = await hunter.hunt([tmp])
        self.assertIn(str(tmp), res)
        for p in tmp.iterdir(): p.unlink(); tmp.rmdir()


class PluginTest(unittest.IsolatedAsyncioTestCase):
    async def test_plugin(self):
        class P(Plugin):
            async def scan(self):
                return ['a']
            async def publish(self):
                return True
        plugins = load_plugins([P])
        self.assertEqual(len(plugins), 1)
        self.assertEqual(await plugins[0].scan(), ['a'])


import aiohttp  # imported at end to avoid slowdown in sync tests

if __name__ == '__main__':
    unittest.main()
