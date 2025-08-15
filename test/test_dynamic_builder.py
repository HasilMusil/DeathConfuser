import sys
from pathlib import Path
import unittest
import os

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.payloads.dynamic_builders import build_payload


class DynamicBuilderTest(unittest.TestCase):
    def test_build_npm_payload(self):
        os.environ['GITHUB_ACTIONS'] = '1'
        payload = build_payload('npm', 'http://callback')
        self.assertIn('http://callback', payload)
        self.assertIn('GITHUB_ACTIONS', payload)
        del os.environ['GITHUB_ACTIONS']

if __name__ == '__main__':
    unittest.main()
