from sv.banks import SVBank
from sv.container import SVContainer
from sv.instruments.detroit import Detroit
from sv.sampler import SVSampleRef as SVSample

import unittest

class DetroitTest(unittest.TestCase):

    def test_detroit(self):
        bank = SVBank.load_zip("tests/pico-default.zip")
        container = SVContainer(banks = [bank])
        sample = SVSample.parse("pico-default/00 BD.wav")
        detroit = Detroit(container = container,
                          namespace = "909",
                          samples = [sample])
        container.add_instrument(detroit)
        container.spawn_patch()
        def Four2Floor(self, n, **kwargs):
            for i in range(n):
                if 0 == i % 4:
                    trig_block = self.note()
                    yield i, trig_block
        detroit.render(generator = Four2Floor)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
