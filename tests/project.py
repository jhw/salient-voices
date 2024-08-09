from sv.model import SVNoteTrig, SVPatch
from sv.project import SVProject

import rv
import unittest
import yaml

Modules = yaml.safe_load("""
- name: AnalogGenerator
  class: rv.modules.analoggenerator.AnalogGenerator
  links:
  - Echo
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 256
    delay: 36
    delay_unit: 3 # tick
  links:
    - Output
""")

class RenderTest(unittest.TestCase):

    def test_render(self):
        trig = SVNoteTrig(mod = "AnalogGenerato",
                          note = 56,
                          i = 0)
        patch = SVPatch(trigs = [trig],
                        n_ticks = 16)
        project = SVProject().render_project(patches = [patch],
                                             modules = Modules,
                                             banks = [],
                                             bpm = 120)
        self.assertTrue(isinstance(project, rv.project.Project))

if __name__ == "__main__":
    pass
