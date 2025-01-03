import yaml

# https://club.tidalcycles.org/t/week-1-lesson-5-mini-notation-part-3/449

"""
The Euclidean Algorithm Generates Traditional Musical Rhythms by Toussaint
(2,5) : A thirteenth century Persian rhythm called Khafif-e-ramal.
(3,4) : The archetypal pattern of the Cumbia from Colombia, as well as a Calypso rhythm from Trinidad.
(3,5,2) : Another thirteenth century Persian rhythm by the name of Khafif-e-ramal, as well as a Rumanian folk-dance rhythm.
(3,7) : A Ruchenitza rhythm used in a Bulgarian folk-dance.
(3,8) : The Cuban tresillo pattern.
(4,7) : Another Ruchenitza Bulgarian folk-dance rhythm.
(4,9) : The Aksak rhythm of Turkey.
(4,11) : The metric pattern used by Frank Zappa in his piece titled Outside Now.
(5,6) : Yields the York-Samai pattern, a popular Arab rhythm.
(5,7) : The Nawakhat pattern, another popular Arab rhythm.
(5,8) : The Cuban cinquillo pattern.
(5,9) : A popular Arab rhythm called Agsag-Samai.
(5,11) : The metric pattern used by Moussorgsky in Pictures at an Exhibition.
(5,12) : The Venda clapping pattern of a South African children’s song.
(5,16) : The Bossa-Nova rhythm necklace of Brazil.
(7,8) : A typical rhythm played on the Bendir (frame drum).
(7,12) : A common West African bell pattern.
(7,16,14) : A Samba rhythm necklace from Brazil.
(9,16) : A rhythm necklace used in the Central African Republic.
(11,24,14) : A rhythm necklace of the Aka Pygmies of Central Africa.
(13,24,5) : Another rhythm necklace of the Aka Pygmies of the upper Sangha
"""

TidalPatterns = yaml.safe_load("""
- [2, 5]
- [3, 4]
- [3, 5, 2]
- [3, 7]
- [3, 8]
- [4, 7]
- [4, 9]
- [4, 11]
- [5, 6]
- [5, 7]
- [5, 8]
- [5, 9]
- [5, 11]
- [5, 12]
- [5, 16]
- [7, 8]
- [7, 12]
- [7, 16, 14]
- [9, 16]
- [11, 24, 14]
- [13, 24, 5]
""")

# https://raw.githubusercontent.com/brianhouse/bjorklund/master/__init__.py

def wrap_generator(fn):
    def wrapped(steps, pulses):
        pattern = fn(steps, pulses)
        return lambda i: pattern[i % len(pattern)]
    return wrapped

@wrap_generator
def bjorklund(steps, pulses):
    steps = int(steps)
    pulses = int(pulses)
    if pulses > steps:
        raise ValueError    
    pattern = []    
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)
    
    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)         
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)
    
    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    return pattern

if __name__ == "__main__":
    pass
