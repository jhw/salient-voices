import math
import random

def random_colour(offset = 64,
                  contrast = 128,
                  n = 32):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

def order_colours(colours):
    def rgb_distance(colour1, colour2):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(colour1, colour2)))
    ordered_colours = [colours.pop(0)]    
    while colours:
        last_colour = ordered_colours[-1]
        furthest_colour = max(colours, key=lambda colour: rgb_distance(colour, last_colour))
        colours.remove(furthest_colour)
        ordered_colours.append(furthest_colour)    
    return ordered_colours

def init_colours(mod_names):
    colours = order_colours([random_colour() for _ in mod_names])        
    return {mod_name: colour
            for mod_name, colour in zip(mod_names, colours)}

if __name__ == "__main__":
    pass
