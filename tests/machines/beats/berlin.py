import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.beats.berlin import BerlinMachine, BerlinSound, BerlinWave

import inspect
import json
import random
import unittest

def BassLine(self, n, rand, tpb, groove, temperature,
             root_offset = -4,
             offsets = [0, 0, 0, -2],
             note_density = 0.5,
             quantise = 1,
             **kwargs):
    i = 0
    while True:
        if rand["sound"].random() < temperature:
            self.randomise_sound(rand["sound"])
        note = root_offset + rand["note"].choice(offsets)
        volume = groove(rand = rand["vol"], i = i)
        if (rand["seq"].random() < note_density and
              0 == i % (quantise * tpb)):
            block =  self.note(note = note,
                               volume = volume)
            yield i, block
            i += self.sound.sustain_term # NB
        i += 1
        if i >= n:
            break

def random_sounds(tpb, n,
                  terms = [0.5, 0.5, 0.5, 1, 2],
                  frequencies = ["2000", "3000", "3000", "3000", "5000"],
                  resonances = ["6000", "6800", "7000", "7800"]):
    resonance = random.choice(resonances)
    sounds = []
    for i in range(n):
        sound = BerlinSound(sustain_term = int(random.choice(terms) * tpb),
                            filter_freq = random.choice(frequencies),
                            filter_resonance = resonance)
        sounds.append(sound)
    return sounds
        
def random_groove_fn(tpb, mod = perkons):
    fn_names = [name for name, _ in inspect.getmembers(mod, inspect.isfunction)]
    fn = getattr(mod, random.choice(fn_names))
    def wrapped(i, **kwargs):
        if 0 == i % tpb:
            j = int(i / tpb)
            return fn(j, **kwargs)
        else:
            return 0
    return wrapped
    
def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

class BerlinMachineTest(unittest.TestCase):

    def test_berlin_machine(self,
                            temperature = 0.5,
                            bpm = 120,
                            tpb = 2,
                            n_ticks = 32,
                            n_sounds = 16):
        bank = SVBank.load_zip("sv/machines/beats/berlin/mikey303.zip")
        container = SVContainer(banks = [bank],
                                bpm = bpm,
                                tpb = tpb,
                                n_ticks = n_ticks)
        sounds = random_sounds(tpb = tpb, n = n_sounds)
        machine = BerlinMachine(container = container,
                                namespace = "303",
                                sounds = sounds,
                                colour = random_colour(),
                                wave = BerlinWave.SQR,
                                echo_wet = 8,
                                echo_feedback = 8,
                                echo_delay = int(bpm * 3 * tpb / 10))
        container.add_machine(machine)
        container.spawn_patch(colour = random_colour())
        seeds = {key: int(random.random() * 1e8)
                 for key in "sound|seq|note|fx|vol".split("|")}
        groove_fn = random_groove_fn(tpb)
        env = {"groove": groove_fn,
               "temperature": temperature,
               "tpb": tpb}
        machine.render(generator = BassLine,
                       seeds = seeds,
                       env = env)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/berlin-machine-demo.sunvox")

class BerlinSoundTest(unittest.TestCase):

    def test_to_json_excludes_none_values(self):
        sound = BerlinSound(
            attack="0010",
            decay="0020",
            sustain_level="0700",
            sustain_term=None,  # This should not appear in the JSON output
            release="0400",
            filter_freq=None,  # This should not appear in the JSON output
            filter_resonance="6000"
        )
        json_data = sound.to_json()
        self.assertEqual(json_data, {
            "attack": "0010",
            "decay": "0020",
            "sustain_level": "0700",
            "release": "0400",
            "filter_resonance": "6000"
        })

    def test_from_json_restores_all_values(self):
        json_data = {
            "attack": "0010",
            "decay": "0020",
            "sustain_level": "0700",
            "release": "0400",
            "filter_resonance": "6000"
        }
        sound = BerlinSound.from_json(json_data)
        self.assertEqual(sound.attack, "0010")
        self.assertEqual(sound.decay, "0020")
        self.assertEqual(sound.sustain_level, "0700")
        self.assertEqual(sound.sustain_term, None)  # Default
        self.assertEqual(sound.release, "0400")
        self.assertEqual(sound.filter_freq, "4000")  # Default
        self.assertEqual(sound.filter_resonance, "6000")
        self.assertEqual(sound.slide_up, None)  # Default
        self.assertEqual(sound.slide_down, None)  # Default

    def test_round_trip_serialization(self):
        original_sound = BerlinSound(
            attack="0010",
            decay="0020",
            sustain_level="0700",
            release="0400",
            filter_resonance="6000"
        )
        # Serialize to JSON
        json_data = original_sound.to_json()
        # Deserialize back to a BerlinSound instance
        restored_sound = BerlinSound.from_json(json_data)
        # Assert all attributes are restored correctly
        self.assertEqual(restored_sound.attack, original_sound.attack)
        self.assertEqual(restored_sound.decay, original_sound.decay)
        self.assertEqual(restored_sound.sustain_level, original_sound.sustain_level)
        self.assertEqual(restored_sound.sustain_term, original_sound.sustain_term)
        self.assertEqual(restored_sound.release, original_sound.release)
        self.assertEqual(restored_sound.filter_freq, original_sound.filter_freq)
        self.assertEqual(restored_sound.filter_resonance, original_sound.filter_resonance)
        self.assertEqual(restored_sound.slide_up, original_sound.slide_up)
        self.assertEqual(restored_sound.slide_down, original_sound.slide_down)

    def test_from_json_with_missing_attributes(self):
        json_data = {
            "attack": "0010",
            "decay": "0020"
        }
        sound = BerlinSound.from_json(json_data)
        self.assertEqual(sound.attack, "0010")
        self.assertEqual(sound.decay, "0020")
        self.assertEqual(sound.sustain_level, "0800")  # Default value
        self.assertEqual(sound.sustain_term, None)  # Default
        self.assertEqual(sound.release, "0300")  # Default
        self.assertEqual(sound.filter_freq, "4000")  # Default
        self.assertEqual(sound.filter_resonance, "7000")  # Default
        self.assertEqual(sound.slide_up, None)  # Default
        self.assertEqual(sound.slide_down, None)  # Default

if __name__ == "__main__":
    unittest.main()
