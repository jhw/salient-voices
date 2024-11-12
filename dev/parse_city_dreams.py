import rv.api

from rv.pattern import Pattern, PatternClone
from rv.readers.reader import read_sunvox_file

def filter_module_chains(project):
    modules = [{"name": mod.name,
                "index": mod.index,
                "links": {"in": mod.in_links,
                          "out": mod.out_links}}
               for mod in project.modules]
    module_dict = {module['index']: module['name'] for module in modules}
    def dfs(current_index):
        current_module = module_dict[current_index]
        if not modules[current_index]['links']['in']:
            return [[(current_module, current_index)]]
        chains = []
        for prev_index in modules[current_index]['links']['in']:
            for chain in dfs(prev_index):
                chains.append(chain + [(current_module, current_index)])        
        return sorted(chains, key = lambda x: x[0][1])
    return dfs(0)

class PatternGroup(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    @property
    def mod_indexes(self):
        mod_indexes = set()
        for pattern in self:
            for track in pattern.data:
                for note in track:
                    if note.mod:
                        mod_indexes.add(note.mod.index)
        return sorted(list(mod_indexes))
        
def group_timeline(project):
    groups = {}
    for i, _pattern in enumerate(project.patterns):
        if isinstance(_pattern, PatternClone):
            pattern = project.patterns[_pattern.source]
        elif isinstance(_pattern, Pattern):
            pattern = _pattern
        x = _pattern.x
        groups.setdefault(x, PatternGroup())
        groups[x].append(pattern)
    return groups

if __name__ == "__main__":
    project = read_sunvox_file("dev/city-dreams.sunvox")
    mod_chains = filter_module_chains(project)
    for mod_chain in mod_chains:
        mod_indexes = [i for _, i in mod_chain]
        if 25 in mod_indexes:
            print(mod_chain)
    print()
    groups = group_timeline(project)
    for x, group in groups.items():
        if 25 in group.mod_indexes:
            print (x, group.mod_indexes)

