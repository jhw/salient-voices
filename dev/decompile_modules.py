from rv.api import read_sunvox_file

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

if __name__ == "__main__":
    proj = read_sunvox_file("dev/nightradio-city-dreams.sunvox")
    modules = [{"name": mod.name,
                "index": mod.index,
                "links": {"in": mod.in_links,
                          "out": mod.out_links}}
               for mod in proj.modules]
    chains = build_chains(modules)
    for chain in chains:
        print(" -> ".join(f"{name}[{index}]" for name, index in chain))
