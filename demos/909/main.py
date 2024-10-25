from sv.container import Container
from sv.instruments.nine09 import Nine09
from sv.sampler import SVBank, SVBanks
from sv.project import load_class
from random import Random

import os
import random
import re
import yaml

MachineConfig = yaml.safe_load(open("demos/909/machines.yaml").read())

PoolMappingTerms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
""")

def init_beats(machine):
    def beats(self, n, rand):
        pass
    return beats

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip_file("demos/909/pico-default.zip")
        pool, _ = SVBanks([bank]).spawn_pool(tag_mapping = PoolMappingTerms)
        machine_conf = {machine_conf["tag"]:machine_conf
                        for machine_conf in MachineConfig
                        if "tag" in machine_conf}["mid"]
        machine_class = load_class(machine_conf["class"])
        machine = machine_class(name = machine_conf["name"],
                                tag = machine_conf["tag"],
                                params = machine_conf["params"])
        mapping = {machine_conf["tag"]:machine_conf["default"]}
        machine.randomise(pool = pool,
                          mapping = mapping)
        container = Container(banks = [bank],
                              bpm = 120,
                              n_ticks = 16)
        nine09 = Nine09(container = container,
                        namespace = "909",
                        machine_config = [machine_conf])
        container.add_instrument(nine09)
        rand = {key: Random(int(random.random() * 1e8))
                 for key in "sample|trig|pattern|volume|level".split("|")}
        beats = init_beats(machine)
        nine09.play(generator = beats,
                    seeds = seeds)
        """
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-909.sunvox", 'wb') as f:
            project.write_to(f)
        """
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
