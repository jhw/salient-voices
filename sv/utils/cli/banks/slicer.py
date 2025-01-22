from pydub import AudioSegment

import io
import math

class SlicerBank(dict):

    def __init__(self, meta, wav_io):
        dict.__init__(self, {})
        self.init_slices(meta, wav_io)

    def init_slices(self, meta, wav_io, fade = 3):
        audio = AudioSegment.from_file(wav_io, format="wav")
        n = int(math.log(meta["n_ticks"], 2))
        for i in range(n+1):
            n_slices = meta["n_patches"] * (2 ** n)
            slice_sz = int(len(audio) / n_slices)
            for j in range(n_slices):
                start, end = j * slice_sz, (i + j) * slice_sz
                slice_audio = audio[start:end].fade_in(fade).fade_out(fade)
                slice_io = io.BytesIO()        
                slice_audio.export(slice_io, format="wav")
                slice_io.seek(0)
                file_name = f"audio/sliced/{(2**i):04}/{(i+j):04}.wav"
                self[file_name] = slice_io

    def list_slices(self, n_ticks, quantise):
        n = int(n_ticks / quantise)
        files = [file_name for file_name in self
                 if file_name.startswith(f"audio/sliced/{n:04}")]
        if files == []:
            raise RuntimeError("no slice files found")
        return files
                
    def get_wav(self, file_name):
        return self[file_name]
