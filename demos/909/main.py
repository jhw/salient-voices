from sv.container import Container
from sv.instruments.nine09 import Nine09
from sv.sampler import SVBank
from random import Random

import os

def beats(self, n, rand):
    pass

def ghost(self, n, rand):
    pass

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip_file("demos/909/pico-default.zip")        
        container = Container(banks = [bank],
                              bpm = 120,
                              n_ticks = 16)
        print(container)
        """
        nine09 = Nine09(container = container,
                        namespace = "909")
        container.add_instrument(nine09)
        rand = Random(seed)
        seeds = {key: int(rand.random() * 1e8)
                 for key in "seq|note|fx".split("|")}
        nine09.play(generator = beats,
                    seeds = seeds)
        nine09.play(generator = ghost,
                    seeds = seeds)
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-909.sunvox", 'wb') as f:
            project.write_to(f)
        """
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
