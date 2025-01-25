import demos.bass.berlin03
import demos.beats.euclid09
import demos.beats.tokyo09
import demos.resampler

import os

if __name__ == "__main__":
    os.system("rm tmp/*.sunvox")
    demos.bass.berlin03.main()
    demos.beats.euclid09.main()
    demos.beats.tokyo09.main()
    demos.resampler.main()
