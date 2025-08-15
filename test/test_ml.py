import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.core import ml


class MLTest(unittest.TestCase):
    def test_functions(self):
        variants = ml.predict_package_variants('demo')
        self.assertTrue(any('demo' in v for v in variants))
        sev = ml.classify_callback_severity({'message': 'critical exploit detected'})
        self.assertEqual(sev, 'critical')
        tmpl = ml.select_payload_for_stack('python')
        self.assertTrue(tmpl.endswith('.j2'))
        prof = ml.adjust_opsec_behavior({'risk': 'high', 'delay': 1})
        self.assertEqual(prof['behavior'], 'stealth')
        self.assertGreaterEqual(prof['delay'], 5)
        score = ml.score_target_priority('example.org')
        self.assertGreater(score, 0)

if __name__ == '__main__':
    unittest.main()
