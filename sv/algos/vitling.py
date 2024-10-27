# https://github.com/vitling/acid-banger/blob/main/src/pattern.ts

def fourfloor_kick(rand, n = 16):
    pattern = [0] * n
    for i in range(n):
        if i % 4 == 0:
            pattern[i] = 0.9
        elif i % 2 == 0 and rand.random() < 0.1:
            pattern[i] = 0.6
    return pattern

def electro_kick(rand, n = 16):
    pattern = [0] * n
    for i in range(n):
        if i == 0:
            pattern[i] = 1
        elif i % 2 == 0 and i % 8 != 4 and rand.random() < 0.5:
            pattern[i] = rand.random() * 0.9
        elif rand.random() < 0.05:
            pattern[i] = rand.random() * 0.9
    return pattern

def backbeat_snare(rand, n = 16):
    pattern = [0] * n
    for i in range(n):
        if i % 8 == 4:
            pattern[i] = 1
    return pattern

def skip_snare(rand, n = 16):
    pattern = [0] * n
    for i in range(n):
        if i % 8 in [3, 6]:
            pattern[i] = 0.6 + rand.random() * 0.4
        elif i % 2 == 0 and rand.random() < 0.2:
            pattern[i] = 0.4 + rand.random() * 0.2
        elif rand.random() < 0.1:
            pattern[i] = 0.2 + rand.random() * 0.2
    return pattern

def offbeats_hat(rand, n = 16):
    oh_pattern = [0] * n
    ch_pattern = [0] * n
    for i in range(n):
        if i % 4 == 2:
            oh_pattern[i] = 0.4
        elif rand.random() < 0.3:
            if rand.random() < 0.5:
                ch_pattern[i] = rand.random() * 0.2
            else:
                oh_pattern[i] = rand.random() * 0.2
    return oh_pattern, ch_pattern

def closed_hat(rand, n = 16):
    ch_pattern = [0] * n
    for i in range(n):
        if i % 2 == 0:
            ch_pattern[i] = 0.4
        elif rand.random() < 0.5:
            ch_pattern[i] = rand.random() * 0.3
    return ch_pattern

if __name__ == "__main__":
    pass
