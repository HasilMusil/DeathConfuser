import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.plugins.plugin_api import PLUGINS
from DeathConfuser.plugins import example_plugin  # noqa: F401


class PluginAPITest(unittest.TestCase):
    def test_registered(self):
        self.assertIn('example', PLUGINS)

if __name__ == '__main__':
    unittest.main()
