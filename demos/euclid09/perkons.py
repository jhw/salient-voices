import math

def swing(i, **kwargs):
    return 0.8 if i % 2 == 0 else 1.0

def shifted_swing(i, **kwargs):
    return 0.85 if (i + 1) % 4 < 2 else 1.0

def push(i, **kwargs):
    return 1.0 if i % 4 == 0 else 0.9

def pull(i, **kwargs):
    return 0.9 if i % 4 == 0 else 1.0

def humanise(i, rand, **kwargs):
    return max(0.85, min(1.0, 0.9 + rand.uniform(-0.05, 0.05)))

def dynamic(i, **kwargs):
    return 0.8 + 0.2 * math.sin((i % 16) / 16 * 2 * math.pi)

