import demos.beats.detroit09
import demos.beats.tokyo09

import os

if __name__ == "__main__":
    os.system("rm -rf tmp/demos")
    demos.beats.detroit09.main()
    demos.beats.tokyo09.main()
