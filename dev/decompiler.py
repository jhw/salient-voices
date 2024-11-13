import rv.api

from rv.note import Note
from rv.pattern import Pattern, PatternClone
from rv.readers.reader import read_sunvox_file

from collections import OrderedDict

class ModuleChain(list):

    @staticmethod
    def parse_modules(project):
        modules = [{"name": mod.name,
                    "index": mod.index,
                    "links": {"in": mod.in_links,
                              "out": mod.out_links}}
                   for mod in project.modules]
        module_dict = {module['index']: module['name'] for module in modules}    
        def dfs(current_index):
            current_module = module_dict[current_index]
            if not modules[current_index]['links']['in']:
                return [ModuleChain([(current_module, current_index)])]
            chains = []
            for prev_index in modules[current_index]['links']['in']:
                for chain in dfs(prev_index):
                    chains.append(ModuleChain(chain + [(current_module, current_index)]))
            return sorted(chains, key=lambda x: x[0][1])    
        return dfs(0)
    
    def __init__(self, items = []):
        list.__init__(self, items)

    @property
    def names(self):
        return [mod[0] for mod in self
                if mod[0] != "OUT"]

    @property
    def indexes(self):
        return [mod[1] for mod in self
                if mod[1] != 0]

    def __str__(self):
        return "-".join([f"{name[:3].lower()}-{index:02X}"
                         for name, index in zip(self.names, self.indexes)])

def rotate_matrix(matrix, clockwise = True):
    if clockwise:
        return [list(row) for row in zip(*matrix[::-1])]
    else:
        return [list(row) for row in zip(*matrix)][::-1]

"""
RV thinks in terms of lines(rows) primarily and then tracks within those lines
But it's more natural to think in terms of cols here, with each col as a track
Hence rotate pattern data and then rotate it back
"""
    
class Tracks(list):

    @staticmethod
    def from_pattern_data(pattern_data):
        return Tracks(rotate_matrix(pattern_data))
    
    def __init__(self, items = []):
        list.__init__(self, items)

    def filter_by_chain(self, chain):
        mod_indexes, tracks = chain.indexes, []
        for _track in self:
            track = []
            for _note in _track:
                if _note.mod and _note.mod in mod_indexes:
                    track.append(_note)
                else:
                    track.append(Note())
            tracks.append(track)
        return Tracks(tracks)

    def to_pattern_data(self):
        return rotate_matrix(self, clockwise = False)
        
class PatternGroup(list):

    def __init__(self, x, items = []):
        list.__init__(self, items)
        self.x = x
        
    @property
    def mod_indexes(self):
        mod_indexes = set()
        for pattern in self:
            for track in pattern.data:
                for note in track:
                    if note.mod:
                        mod_indexes.add(note.mod.index)
        return sorted(list(mod_indexes))

    """
    - remember RV manages notes in rows (lines) first, then cols (notes-in-track) nested inside that
    """
    
    def clone_patterns(self, chain):
        for i, pat in enumerate(group):
            tracks = Tracks.from_pattern_data(pat.data)
            pat_data = tracks.filter_by_chain(chain).to_pattern_data()
            print(self.x, i, len(tracks), len(pat_data))
         
class PatternGroups(list):

    @staticmethod
    def parse_timeline(project):
        groups = OrderedDict()
        for i, _pattern in enumerate(project.patterns):
            if isinstance(_pattern, PatternClone):
                pattern = project.patterns[_pattern.source]
            elif isinstance(_pattern, Pattern):
                pattern = _pattern
            x = _pattern.x
            groups.setdefault(x, PatternGroup(x))
            groups[x].append(pattern)
        return PatternGroups(list(groups.values()))
    
    def __init__(self, items = {}):
        list.__init__(self, items)

    def filter_by_chain(self, chain,
                        filter_fn = lambda chain, group: chain.indexes[0] in group.mod_indexes):
        return PatternGroups([group for group in self
                              if filter_fn(chain, group)])
        
if __name__ == "__main__":
    project = read_sunvox_file("dev/city-dreams.sunvox")
    chains = ModuleChain.parse_modules(project)
    groups = PatternGroups.parse_timeline(project)
    for chain in chains:
        if chain [0][1] == 25:
            chain_groups = groups.filter_by_chain(chain)
            for group in chain_groups:
                group.clone_patterns(chain)
                        
