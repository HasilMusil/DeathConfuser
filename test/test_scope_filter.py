import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core.scope_filter import filter_targets


class ScopeFilterTest(unittest.TestCase):
    def test_filter(self):
        res = filter_targets(['a.com', 'b.gov'], ['.gov'])
        self.assertEqual(res, ['a.com'])

if __name__ == '__main__':
    unittest.main()
