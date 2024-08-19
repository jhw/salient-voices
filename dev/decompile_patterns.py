
from rv.api import read_sunvox_file
from rv.pattern import Pattern

if __name__ == "__main__":
    proj = read_sunvox_file("dev/nightradio-city-dreams.sunvox")
    count = 0
    for pattern in proj.patterns:
        if isinstance(pattern, Pattern):
            x, y = pattern.x, pattern.y
            count += 1 
            for line_no, line in enumerate(pattern.data):
                for track_no, note in enumerate(line):
                    if note.module != 0:
                        # note.pattern = None
                        # print ((x, y, track_no, line_no), repr(note))
                        pass
    print (count)
