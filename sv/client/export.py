"""
- rv/tools/export.py
"""

from sunvox.slot import Slot
from sunvox.buffered import BufferedProcess
from sunvox.buffered import float32, int16
from io import BytesIO
import numpy as np
from scipy.io import wavfile

def export_wav(project,
               data_type = int16, # int16, float32
               channels = 2, # 1, 2
               freq = 44100): # 44100, 48000
    p = BufferedProcess(freq = freq,
                          size = freq,
                          channels = channels,
                          data_type = data_type)
    slot = Slot(project, process = p)
    length = slot.get_song_length_frames()
    output = np.zeros((length, 2), data_type)
    position = 0
    slot.play_from_beginning()
    while position < length:
        buffer = p.fill_buffer()
        end_pos = min(position+freq, length)
        copy_size = end_pos-position
        output[position:end_pos] = buffer[:copy_size]
        position = end_pos
    buf = BytesIO()
    wavfile.write(buf, freq, output)
    p.deinit()
    p.kill()
    buf.seek(0)
    return buf

if __name__ == "__main__":
    pass
