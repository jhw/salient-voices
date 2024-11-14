from rv.readers.reader import read_sunvox_file

if __name__ == "__main__":
    project = read_sunvox_file("dev/vocoder/6-band-vocoder.sunvox")
    player = project.modules[2]
    with open("dev/vocoder/govorit-moskva.ogg", 'wb') as f:
        f.write(player.data)
