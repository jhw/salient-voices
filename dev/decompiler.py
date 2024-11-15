import rv.api

from rv.note import Note, NOTECMD
from rv.pattern import Pattern, PatternClone
from rv.project import Project
from rv.readers.reader import read_sunvox_file

from collections import OrderedDict

import logging
import os
import re
import sys
import traceback

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

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

    """
    Note cloning a module -
    - detaches it from project
    - resets indexing
    - removes connections
    """

    def is_output(self, item):
        return item[0] == "OUT"
    
    def clone_modules(self, project):
        modules = {mod.index: mod for mod in project.modules}
        return [modules[item[1]].clone() for item in self
                if not self.is_output(item)]
        
    @property
    def names(self):
        return [item[0] for item in self
                if not self.is_output(item)]

    @property
    def indexes(self):
        return [item[1] for item in self
                if not self.is_output(item)]
    
    def __str__(self):
        return "-".join([f"{name[:3].lower()}-{index:02X}"
                         for name, index in zip(self.names, self.indexes)])

"""
RV thinks in terms of lines, and then tracks belonging to a line
But this is fucked up as it means the track data is atomised
Better to rotate so you can work in terms of tracks (cols) and then rotate back on output
"""
    
def rotate_matrix(matrix, clockwise = True):
    if clockwise:
        return [list(row) for row in zip(*matrix[::-1])]
    else:
        return [list(row) for row in zip(*matrix)][::-1]

class Track(list):

    def __init__(self, notes = []):
        list.__init__(self, notes)

    def has_content(self):
        for note in self:
            if not (note == None or
                    (note.note == NOTECMD.EMPTY and
                     note.vel == 0 and
                     note.module == 0 and
                     note.ctl == 0 and
                     note.val == 0 and
                     note.pattern == None) or
                    note.note == NOTECMD.NOTE_OFF):                    
                return True
        return False

class Tracks(list):

    @staticmethod
    def from_pattern_data(pattern_data):
        return Tracks(rotate_matrix(pattern_data))
    
    def __init__(self, items = []):
        list.__init__(self, items)

    """
    Note that module indexes start at 1 not 0 (because Output is 0)
    Nice thing about this routine is that mod.index is never directly references so you don't need a +1 hack anywhere :)
    """
        
    def filter_by_chain(self, chain, modules):
        mod_indexes, tracks = chain.indexes, []
        for _track in self:
            track = Track()
            for _note in _track:
                if _note.mod and _note.mod.index in mod_indexes:
                    mod_index = mod_indexes.index(_note.mod.index)
                    note = _note.clone()
                    note.mod = modules[mod_index]
                    track.append(note)
                elif _note.note in [NOTECMD.NOTE_OFF]:
                    note = _note.clone()
                    track.append(note)
                else:
                    track.append(Note())
            if track.has_content():
                tracks.append(track)
        return Tracks(tracks)

    @property
    def lengths(self):
        lengths = set()
        for track in self:
            lengths.add(len(track))
        return lengths
    
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

    def master_tracks(self, chain, modules):
        master = Tracks()
        for pat in self:
            tracks = Tracks.from_pattern_data(pat.data)
            filtered_tracks = tracks.filter_by_chain(chain, modules)
            if filtered_tracks != []:
                track_lengths = filtered_tracks.lengths
                if len(track_lengths) != 1:
                    raise RuntimeError(f"chain {chain} has multiple track lengths {track_lengths}")
                master += filtered_tracks
        return master
         
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

    def filter_by_chain(self, chain, filter_fn):
        return PatternGroups([group for group in self
                              if filter_fn(chain, group)])

"""
The VCO is typically at the start of the chain; is this module present in a pattern group's list of modules?
"""
    
def DefaultChainFilter(chain, group):
    return chain.indexes[0] in group.mod_indexes
    
def create_patch(project, chain, groups,
                 filter_fn = DefaultChainFilter):
    patch = Project()
    for attr in ["initial_bpm",
                 "global_volume"]:
        setattr(patch, attr, getattr(project, attr))
    chain_modules = chain.clone_modules(project) # excludes Output, indexing
    for mod in reversed(chain_modules):
        patch.attach_module(mod)
    patch_modules = patch.modules # includes Output, indexing
    for i in range(len(chain_modules)):
        patch.connect(patch_modules[i+1], patch_modules[i])
    chain_groups = groups.filter_by_chain(chain, filter_fn)
    patch.patterns, existing, x = [], set(), 0
    for group in chain_groups:
        master = group.master_tracks(chain, chain_modules)
        pat_data = master.to_pattern_data()
        pattern = Pattern(lines = len(pat_data),
                          tracks = len(master),
                          x = x,
                          y = 0)
        pattern.set_via_fn(lambda self, i, j: pat_data[i][j])
        pat_repr = pattern.tabular_repr()
        if pat_repr not in existing:
            patch.patterns.append(pattern)
            x += len(pat_data)
            existing.add(pat_repr)
    return patch

def decompile_project(project_name, project):
    chains = ModuleChain.parse_modules(project)
    groups = PatternGroups.parse_timeline(project)
    for chain in chains:
        patch = create_patch(project = project,
                             chain = chain,
                             groups = groups)
        if patch.patterns != []:
            logging.info(chain)
            file_name = f"tmp/decompiler/{project_name}/{chain}.sunvox"
            dir_name = "/".join(file_name.split("/")[:-1])
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(file_name, 'wb') as f:            
                patch.write_to(f)

def parse_project_name(filename):
    return "-".join([tok.lower() for tok in re.split("\\W", filename.split("/")[-1].split(".")[0]) if tok != ''])
                
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise RuntimeError("please enter path to sunvox file")
        filename = sys.argv[1]
        if not os.path.exists(filename):
            raise RuntimeError("file does not exist")
        if not filename.endswith(".sunvox"):
            raise RuntimeError("file must be a .sunvox file")
        project_name = parse_project_name(filename)
        logging.info(f"--- {project_name} ---")
        project = read_sunvox_file(filename)
        try:
            decompile_project(project_name, project)
        except Exception as e:
            logging.warning(f"{traceback.format_exc()}")
    except RuntimeError as error:
        logging.error(str(error))

                        
