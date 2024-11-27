from rv.readers.reader import read_sunvox_file

if __name__ == "__main__":
    project = read_sunvox_file("../../packages/sunvox-2-1/examples/NightRadio - Mechanical Heart.sunvox")
    with open("tmp/mechanical-heart.sunvox", 'wb') as f:            
        project.write_to(f)
        

