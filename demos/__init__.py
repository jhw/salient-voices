import random

def random_seed():
    return int(random.random() * 1e8)

def unpack_string_list(fn):
    def wrapped(keys):
        return fn(keys.split("|") if isinstance(keys, str) else keys)
    return wrapped

@unpack_string_list
def random_seeds(keys):    
    return {key: random_seed() for key in keys}

def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

if __name__ == "__main__":
    pass
