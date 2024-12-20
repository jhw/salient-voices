from sv.banks import SVBank
from sv.sampler import SVSlotSampler
from sv.sounds import SVSample

from io import BytesIO
from pydub import AudioSegment
from pydub.generators import Sine
from unittest.mock import patch

import rv
import rv.note
import unittest

class SamplerTest(unittest.TestCase):

    def setUp(self):
        self.bank = SVBank.load_zip("tests/mikey303.zip")

    def generate_wav_io(self, duration_ms=1000, freq=440):
        """Generates a valid WAV file-like object with a sine wave."""
        sine_wave = Sine(freq).to_audio_segment(duration=duration_ms)
        wav_io = BytesIO()
        sine_wave.export(wav_io, format="wav")
        wav_io.seek(0)
        return wav_io

    def test_slot_sampler_initialization(self):
        tag_mapping = {"bass": "303"}
        pool = [SVSample.parse(f"mikey303/{name}")
                for name in self.bank.zip_file.namelist()] # TEMP
        sampler = SVSlotSampler(bank=self.bank, pool=pool, root=rv.note.NOTE.C5)
        samples = [sample for sample in sampler.samples if sample]
        self.assertEqual(len(samples), 2)
        self.assertIn(rv.note.NOTE.C5, sampler.note_samples)

    def test_apply_trim(self):
        sampler = SVSlotSampler(bank=self.bank, pool=[], root=rv.note.NOTE.C5)
        wav_io = self.generate_wav_io()
        start, cutoff = 100, 800
        trimmed_wav_io = sampler.apply_trim(wav_io, start=start, cutoff=cutoff)
        trimmed_audio = AudioSegment.from_file(trimmed_wav_io, format="wav")
        self.assertAlmostEqual(len(trimmed_audio), cutoff - start, delta=10)

    def test_apply_reverse(self):
        sampler = SVSlotSampler(bank=self.bank, pool=[], root=rv.note.NOTE.C5)
        wav_io = self.generate_wav_io()
        start, cutoff = 200, 900
        reversed_wav_io = sampler.apply_reverse(wav_io, start=start, cutoff=cutoff)
        reversed_audio = AudioSegment.from_file(reversed_wav_io, format="wav")
        self.assertAlmostEqual(len(reversed_audio), cutoff - start, delta=10)

    def test_apply_retrig(self):
        sampler = SVSlotSampler(bank=self.bank, pool=[], root=rv.note.NOTE.C5)
        wav_io = self.generate_wav_io()
        start, cutoff = 0, 1000
        n_retrigs = 4
        retrigged_wav_io = sampler.apply_retrig(wav_io, start=start, cutoff=cutoff, n_retrigs=n_retrigs)
        retrigged_audio = AudioSegment.from_file(retrigged_wav_io, format="wav")
        expected_duration = (cutoff - start) // n_retrigs * n_retrigs
        self.assertAlmostEqual(len(retrigged_audio), expected_duration, delta=10)

    def test_index_of(self):
        tag_mapping = {"bass": "303"}
        pool = [SVSample.parse(f"mikey303/{name}")
                for name in self.bank.zip_file.namelist()] # TEMP
        sampler = SVSlotSampler(bank=self.bank, pool=pool, root=rv.note.NOTE.C5)
        sample_strings = [str(sample) for sample in pool]
        for i, sample in enumerate(pool):
            self.assertEqual(sampler.index_of(sample), sample_strings.index(str(sample)))

    def test_max_slots_exceeded(self):
        tag_mapping = {"bass": "303"}
        pool = [SVSample.parse(f"mikey303/{name}")
                for name in self.bank.zip_file.namelist()] # TEMP
        with self.assertRaises(RuntimeError) as context:
            SVSlotSampler(bank=self.bank, pool=pool * 100, root=rv.note.NOTE.C5)
        self.assertIn("sampler max slots exceeded", str(context.exception))

    def test_invalid_sample_format(self):
        sampler = SVSlotSampler(bank=self.bank, pool=[], root=rv.note.NOTE.C5)
        with patch("scipy.io.wavfile.read", side_effect=ValueError("File format not understood")):
            wav_io = BytesIO(b"Not a valid WAV file")
            with self.assertRaises(RuntimeError) as context:
                sampler.init_rv_sample(wav_io)
            self.assertIn("Unsupported", str(context.exception))

if __name__ == "__main__":
    unittest.main()
