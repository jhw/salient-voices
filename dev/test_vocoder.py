from rv.readers.reader import read_sunvox_file

if __name__ == "__main__":
    project = read_sunvox_file("dev/6-band-vocoder.sunvox")
    player = project.modules[2]
    with open("dev/govorit-moskva.ogg", 'wb') as f:
        f.write(player.data)
