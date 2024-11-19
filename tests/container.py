from sv.instruments.nine09.samples import Nine09
from sv.banks import SVBank
from sv.container import SVContainer
from sv.sampler import SVSampleRef

import unittest

class ContainerTest(unittest.TestCase):

    def test_play(self, seed = 12345):
        bank = SVBank.load_zip("tests/pico-default.zip")
        container = SVContainer(banks = [bank])
        sample = SVSampleRef.parse("pico-default/00 BD.wav")
        nine09 = Nine09(container = container,
                        namespace = "909",
                        samples = [sample])
        container.add_instrument(nine09)
        container.spawn_patch()
        def Four2Floor(self, n, **kwargs):
            for i in range(n):
                if 0 == i % 4:
                    trig_block = self.note()
                    yield i, trig_block
        nine09.render(generator = Four2Floor)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        
if __name__ == "__main__":
    unittest.main()
