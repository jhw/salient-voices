import rv.api

from rv.pattern import Pattern, PatternClone
from rv.readers.reader import read_sunvox_file

def filter_module_chains(project):
    modules = [{"name": mod.name,
                "index": mod.index,
                "links": {"in": mod.in_links,
                          "out": mod.out_links}}
               for mod in project.modules]
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
        
        return sorted(chains, key = lambda x: x[0][1])
                    
    # Start from the OUT module, which is index 0
    return dfs(0)

def group_patterns_by_time(project):
    groups = {}
    for pattern in project.patterns:
        if isinstance(pattern, Pattern):
            groups.setdefault(pattern.x, [])
            groups[pattern.x].append(pattern)
    return groups

def filter_module_refs(pattern):
    modules = set()
    for track in pattern.data:
        for note in track:
            if note.module:
                modules.add(note.module)
    return modules

if __name__ == "__main__":
    project = read_sunvox_file("dev/city-dreams.sunvox")
    mod_chains = filter_module_chains(project)
    for mod_chain in mod_chains:
        print(mod_chain)
    print()
    pattern_groups = group_patterns_by_time(project)
    for key, values in pattern_groups.items():
        print (key, len(values))
    print()
    for pattern in pattern_groups[384]:
        # print(pattern.tabular_repr())
        mod_indexes = filter_module_refs(pattern)
        print(mod_indexes)

