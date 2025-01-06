from pydub import AudioSegment

from datetime import datetime

import copy
import random

PatchSize = 2000

if __name__ == "__main__":
    # src_file = "any-mee.wav"
    # src_file = "sam-emp.wav"
    src_file = "ttl-stc.wav"
    audio = AudioSegment.from_file(f"dev/naive_slicing/{src_file}", format = "wav")
    n_slices, n_slices_subset, n_patches, density = 128, 16, 16, 0.66666
    slice_sz = int(len(audio) / n_slices)
    slices = [audio[i * slice_sz : (i+1) * slice_sz]
              for i in range(n_slices)]
    n_patch_slices = int(PatchSize / slice_sz)
    output = AudioSegment.silent()
    for i in range(n_patches):
        slice_subset = [random.choice(slices) for j in range(n_slices_subset)]
        for j in range(n_patch_slices):
            if random.random() < density:
                slice = copy.deepcopy(random.choice(slice_subset))
            else:
                slice = AudioSegment.silent(slice_sz)                
            output += slice.fade_in(3).fade_out(3)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output.export(f"tmp/naive-slicing-{timestamp}.wav", format = "wav")
    
