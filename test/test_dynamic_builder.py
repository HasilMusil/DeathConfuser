import sys
from pathlib import Path
import unittest
import os

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.payloads.dynamic_builders import build_payload


class DynamicBuilderTest(unittest.TestCase):
    def test_build_npm_payload(self):
        os.environ['GITHUB_ACTIONS'] = '1'
        os.environ['MY_SECRET'] = 'x'
        payload = build_payload('npm', 'http://callback')
        self.assertIn('http://callback', payload)
        self.assertIn('GITHUB_ACTIONS', payload)
        self.assertIn('secrets', payload)
        del os.environ['GITHUB_ACTIONS']
        del os.environ['MY_SECRET']

if __name__ == '__main__':
    unittest.main()
