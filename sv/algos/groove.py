def wolgroove(rand, i, n = 5, var = 0.1, drift = 0.1):
    for j in range(n + 1):
        k = 2 ** (n - j)
        if 0 == i % k:
            sigma = rand.gauss(0, var)
            return 1 - max(0, min(1, j * drift + sigma))

