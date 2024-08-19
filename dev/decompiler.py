from rv.api import read_sunvox_file
from rv.pattern import Pattern

if __name__ == "__main__":
    proj = read_sunvox_file("dev/nightradio-city-dreams.sunvox")
    for mod in proj.modules:
        print ({"name": mod.name,
                "index": mod.index,
                "links": {"in": mod.in_links,
                          "out": mod.out_links}})
    print ()
    for pattern in proj.patterns:
        if isinstance(pattern, Pattern):
            for lineno, line in enumerate(pattern.data):
                notes = []
                for track_no, note in enumerate(line):
                    print (track_no, repr(note))
            print ()

    
