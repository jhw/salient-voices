from sv.algos.euclid import bjorklund

def nine09(n, steps = 16, pulses = 11):
    beats = bjorklund(steps = steps,
                      pulses = pulses)
    for i in range(n):
        j = i % steps
        if beats[j]:
            yield {"i": i}
        
if __name__ == "__main__":
    for beat in nine09(n = 32):
        print (beat)
