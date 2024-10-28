from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09 import Nine09
from sv.project import load_class
from random import Random

import os
import random
import re
import yaml

MachineConfig = yaml.safe_load(open("demos/909/machines.yaml").read())

BeatGenerator = yaml.safe_load("""
class: sv.instruments.nine09.machines.EuclidSequencer
name: generator
params:
  density: 0.5
  modulation:
    sample:
      step: 4
      threshold: 0.5
    pattern:
      step: 4
      threshold: 0.5
  nsamples: 4
""")

PoolMappingTerms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
""")

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip_file("demos/909/pico-default.zip")
        pool, _ = SVBanks([bank]).spawn_pool(tag_mapping = PoolMappingTerms)
        machine_conf = BeatGenerator
        machine_class = load_class(machine_conf["class"])
        samples = pool.filter_by_tag("hat")
        random.shuffle(samples)
        machine = machine_class(name = machine_conf["name"],
                                params = machine_conf["params"],
                                samples = samples[:machine_conf["params"]["nsamples"]])
        print (machine)
        """
        container = SVContainer(banks = [bank],
                                bpm = 120,
                                n_ticks = 16)
        nine09 = Nine09(container = container,
                        namespace = "909",
                        machine_config = [machine_conf])
        container.add_instrument(nine09)
        """
        """
        rand = {key: Random(int(random.random() * 1e8))
                 for key in "sample|trig|pattern|volume|level".split("|")}
        beats = init_beats(machine)
        nine09.play(generator = beats,
                    rand = rand)
        """
        """
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-909.sunvox", 'wb') as f:
            project.write_to(f)
        """
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
