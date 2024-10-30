def build_chains(modules):
    # Create a dictionary to easily access each module by its index
    module_dict = {module['index']: module['name'] for module in modules}
    
    # Recursive function to build chains
    def dfs(current_index):
        current_module = module_dict[current_index]
        if not modules[current_index]['links']['in']:
            return [[(current_module, current_index)]]  # Base case: no incoming links
        
        chains = []
        for prev_index in modules[current_index]['links']['in']:
            for chain in dfs(prev_index):
                chains.append(chain + [(current_module, current_index)])
        
        return chains

    # Start from the OUT module, which is index 0
    return dfs(0)


# Given list of modules
modules = [
    {'name': 'OUT', 'index': 0, 'links': {'in': [21, 24, 7, 9, 10, 19], 'out': []}},
    {'name': 'Generator', 'index': 1, 'links': {'in': [], 'out': [3]}},
    {'name': 'Kicker', 'index': 2, 'links': {'in': [], 'out': [4]}},
    {'name': 'Loop', 'index': 3, 'links': {'in': [1, 6], 'out': [5]}},
    {'name': 'Distortion', 'index': 4, 'links': {'in': [2], 'out': [21]}},
    {'name': 'Delay', 'index': 5, 'links': {'in': [3], 'out': [21]}},
    {'name': 'Generator', 'index': 6, 'links': {'in': [], 'out': [3]}},
    {'name': 'SpectraVoice', 'index': 7, 'links': {'in': [], 'out': [0]}},
    {'name': 'FM', 'index': 8, 'links': {'in': [], 'out': [9]}},
    {'name': 'Echo', 'index': 9, 'links': {'in': [8, 11, 14, 12, 16, 23, 27], 'out': [0]}},
    {'name': 'Generator2', 'index': 10, 'links': {'in': [], 'out': [0]}},
    {'name': 'SpectraVoice2', 'index': 11, 'links': {'in': [], 'out': [9]}},
    {'name': 'SpectraVoice', 'index': 12, 'links': {'in': [], 'out': [9]}},
    {'name': 'Generator', 'index': 13, 'links': {'in': [], 'out': [15]}},
    {'name': 'Flanger', 'index': 14, 'links': {'in': [15, 17, 20, 22], 'out': [9]}},
    {'name': 'LFO', 'index': 15, 'links': {'in': [13], 'out': [14]}},
    {'name': 'SpectraVoice', 'index': 16, 'links': {'in': [], 'out': [9]}},
    {'name': 'FM', 'index': 17, 'links': {'in': [], 'out': [14]}},
    {'name': 'Generator', 'index': 18, 'links': {'in': [], 'out': [19]}},
    {'name': 'Delay', 'index': 19, 'links': {'in': [18, 28], 'out': [0]}},
    {'name': 'FM', 'index': 20, 'links': {'in': [], 'out': [14]}},
    {'name': 'Distortion', 'index': 21, 'links': {'in': [5, 4], 'out': [0]}},
    {'name': 'Generator', 'index': 22, 'links': {'in': [], 'out': [14]}},
    {'name': 'FM', 'index': 23, 'links': {'in': [], 'out': [9]}},
    {'name': 'SpectraVoice', 'index': 24, 'links': {'in': [], 'out': [0]}},
    {'name': 'Generator', 'index': 25, 'links': {'in': [], 'out': [26]}},
    {'name': 'Filter', 'index': 26, 'links': {'in': [25], 'out': [27]}},
    {'name': 'Distortion', 'index': 27, 'links': {'in': [26], 'out': [9]}},
    {'name': 'Generator', 'index': 28, 'links': {'in': [], 'out': [19]}}
]

# Get all chains
chains = build_chains(modules)

# Print the resulting chains with index
for chain in chains:
    print(" -> ".join(f"{name}[{index}]" for name, index in chain))
