import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from DeathConfuser.payloads.builder import PayloadBuilder


class BuilderTest(unittest.TestCase):
    def test_render_template(self):
        builder = PayloadBuilder()
        content = builder.render('npm_package.json.j2', payload_code='echo test')
        self.assertIn('echo test', content)

if __name__ == '__main__':
    unittest.main()
