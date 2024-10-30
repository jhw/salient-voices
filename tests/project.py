from sv.banks import SVBank
from sv.model import SVNoteTrig, SVTrigPatch
from sv.project import SVProject

import rv
import unittest
import yaml

GeneratorModules = yaml.safe_load("""
- name: Generator
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

SamplerModules = yaml.safe_load("""
- name: Sampler
  class: sv.sampler.SVSlotSampler
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

class ProjectTest(unittest.TestCase):

    def test_generator(self, modules = GeneratorModules):
        trig = SVNoteTrig(target = "Generator",
                          note = 56,
                          i = 0)
        patch = SVTrigPatch(trigs = [trig],
                            n_ticks = 16)
        project = SVProject().render_project(patches = [patch],
                                             modules = modules,
                                             bpm = 120)
        self.assertTrue(isinstance(project, rv.project.Project))

    def test_sampler(self, modules = SamplerModules):
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        trig = SVNoteTrig(target = "Sampler",
                          sample = "mikey303/303 VCO SQR.wav",
                          i = 0)
        patch = SVTrigPatch(trigs = [trig],
                            n_ticks = 16)
        project = SVProject().render_project(patches = [patch],
                                             modules = modules,
                                             banks = [bank],
                                             bpm = 120)
        self.assertTrue(isinstance(project, rv.project.Project))
            
if __name__ == "__main__":
    unittest.main()
