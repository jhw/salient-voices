from sv.model import SVNoteTrig, SVPatch
from sv.project import SVProject
from sv.utils.banks import single_shot_bank

import rv
import unittest
import yaml

AnalogGeneratorModules = yaml.safe_load("""
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

SingleSlotSamplerModules = yaml.safe_load("""
- name: Sampler
  class: sv.sampler.SVSingleSlotSampler
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

    def test_analog_generator(self, modules = AnalogGeneratorModules):
        try:
            trig = SVNoteTrig(mod = "Generator",
                              note = 56,
                              i = 0)
            patch = SVPatch(trigs = [trig],
                            n_ticks = 16)
            project = SVProject().render_project(patches = [patch],
                                                 modules = modules,
                                                 bpm = 120)
            self.assertTrue(isinstance(project, rv.project.Project))
        except RuntimeError as error:
            self.fail(str(error))

    def test_single_slot_sampler(self, modules = SingleSlotSamplerModules):
        try:
            bank = single_shot_bank(bank_name = "mikey303",
                                    file_path = "tests/utils/303 VCO SQR.wav")
            trig = SVNoteTrig(mod = "Sampler",
                              sample = "mikey303/303 VCO SQR.wav",
                              i = 0)
            patch = SVPatch(trigs = [trig],
                            n_ticks = 16)
            project = SVProject().render_project(patches = [patch],
                                                 modules = modules,
                                                 banks = [bank],
                                                 bpm = 120)
            self.assertTrue(isinstance(project, rv.project.Project))
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()
