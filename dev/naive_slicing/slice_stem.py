from pydub import AudioSegment

from datetime import datetime

import copy
import random

if __name__ == "__main__":
    audio = AudioSegment.from_file("dev/naive_slicing/any-mee.wav", format = "wav")
    n_slices, patch_size, n_patches = 256, 2000, 16
    slice_size = int(len(audio) / n_slices)
    slices = [audio[i*slice_size:(i+1)*slice_size]
              for i in range(n_slices)]
    n_patch_slices = int(patch_size / slice_size)
    output = AudioSegment.silent()
    for i in range(n_patches):
        slice_subset = [random.choice(slices) for j in range(16)]
        for j in range(n_patch_slices):
            slice = copy.deepcopy(random.choice(slice_subset))
            output += slice.fade_in(3).fade_out(3)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output.export(f"tmp/naive-slicing-{timestamp}.wav", format = "wav")
    
