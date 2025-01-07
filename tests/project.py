from sv.container import SVTrigPatch
from sv.trigs import SVSampleTrig
from sv.project import SVProject

from tests import TestBank

import rv
import rv.api # no idea
import unittest
import yaml

GeneratorModules = yaml.safe_load("""
- name: Generator
  class: rv.modules.analoggenerator.AnalogGenerator
  links:
  - Echo
  colour: [127, 127, 127]
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 256
    delay: 36
    delay_unit: 3 # tick
  links:
    - Output
  colour: [127, 127, 127]
""")

SamplerModules = yaml.safe_load("""
- name: Sampler
  class: sv.sampler.SVSlotSampler
  links:
  - Echo
  root: 62 # C5
  colour: [127, 127, 127]
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 256
    delay: 36
    delay_unit: 3 # tick
  links:
    - Output
  colour: [127, 127, 127]
""")

class ProjectTest(unittest.TestCase):

    def test_sampler(self, modules = SamplerModules):
        bank = TestBank.load_zip("tests/mikey303.zip")
        trig = SVSampleTrig(target = "Sampler",
                            sample = "303 VCO SQR.wav",
                            i = 0)
        patch = SVTrigPatch(trigs = [trig],
                            colour = [128, 128, 128],
                            n_ticks = 16)
        project = SVProject().render_project(patches = [patch],
                                             modules = modules,
                                             bank = bank,
                                             bpm = 120)
        self.assertTrue(isinstance(project, rv.project.Project))        
            
if __name__ == "__main__":
    unittest.main()
