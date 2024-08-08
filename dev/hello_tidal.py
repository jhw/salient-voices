import re

class Beat:
    def __init__(self, index, sample):
        self.index = index
        self.sample = sample

    def __repr__(self):
        return f"Beat(index={self.index}, sample='{self.sample}')"

def parse_tidal_syntax(tidal_string):
    beats = []
    current_index = 0
    step = 1

    # Handle basic patterns and repetitions
    def process_pattern(pattern, start_index, step):
        local_index = start_index
        items = re.split(r'\s+', pattern)
        for item in items:
            if item.isdigit():
                local_index += int(item) * step
            elif item.startswith('[') and item.endswith(']'):
                subpattern = item[1:-1]
                subbeats = process_pattern(subpattern, local_index, step / len(re.split(r'\s+', subpattern)))
                local_index += step
                beats.extend(subbeats)
            else:
                beats.append(Beat(local_index, item))
                local_index += step
        return beats

    # Process the main pattern
    process_pattern(tidal_string, current_index, step)
    return beats

# Example usage
tidal_string = "bd bd sn [bd sn]"
beats = parse_tidal_syntax(tidal_string)
print(beats)
