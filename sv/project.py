from sv.banks import SVPool, SVBanks
from sv.utils.colours import init_colours

import importlib
import math
import rv
import rv.api # why?

Volume, PatternHeight = 256, 16

def load_class(path):
    try:
        tokens = path.split(".")            
        mod_path, class_name = ".".join(tokens[:-1]), tokens[-1]
        module=importlib.import_module(mod_path)
        return getattr(module, class_name)
    except AttributeError as error:
        raise RuntimeError(str(error))
    except ModuleNotFoundError as error:
        raise RuntimeError(str(error))
    
class SVModule(dict):

    def __init__(self, item = {}):
        dict.__init__(self, item)

    @property
    def links(self):
        links = []
        for link_dest in self["links"]:
            link = [self["name"], link_dest]
            links.append(link)
        return links

class SVModules(list):

    def __init__(self, items = []):
        list.__init__(self, [SVModule(item)
                             for item in items])

    def validate(self):        
        names = [item["name"] for item in self]
        if len(names) != len(set(names)):
            raise RuntimeError("modules names are not unique")
        names.append("Output")
        errors = []
        for item in self:
            for name in item["links"]:
                if name == item["name"]:
                    errors.append(f"{name} can't link to itself")
                else:
                    if name not in names:
                        errors.append(f"unknown link destination {name}")
        if errors != []:
            raise RuntimeError(", ".join(errors))        
                    
    @property
    def links(self):
        links = []
        for item in self:
            links += item.links
        return links

def init_project(fn):
    def wrapped(self, modules, banks = [], *args, **kwargs):
        banks = SVBanks(banks)
        modules = SVModules(modules)
        modules.validate()
        return fn(self,
                  modules = modules,
                  banks = banks,
                  *args, **kwargs)
    return wrapped

def init_modules(fn):
    def wrapped(self,
                project,
                patches,
                modules,
                colours,
                banks):
        mod_names = [mod["name"] for mod in modules]
        for mod in modules:
            mod_class = load_class(mod["class"])
            mod_kwargs = {}
            if mod["class"].lower().endswith("sampler"):
                pool = SVPool()
                for patch in patches:
                    for trig in patch.trigs:
                        if (trig.mod == mod["name"] or
                            (hasattr(trig, "sample_mod") and
                             trig.sample_mod == mod["name"])):
                            pool.add(trig.sample)
                mod_kwargs = {"banks": banks,
                              "pool": pool}
            mod["instance"] = mod_class(**mod_kwargs)
        return fn(self,
                  project = project,
                  patches = patches,
                  modules = modules,
                  colours = colours,
                  banks = banks)
    return wrapped

"""
Project rendering doesn't necessarily have to be class based but there's so much rendering going on it's simplest to encapsulate it all in a class
"""

class SVProject:

    @init_modules
    def render_modules(self,                     
                       project,
                       patches,                       
                       modules,
                       colours, 
                       banks,
                       x_offset = 128,
                       y_offset = 128,
                       x0 = 128,
                       y0 = 256):
        output = project.modules[0]
        setattr(output, "x", x0)
        setattr(output, "y", y0)
        n = int(math.ceil(len(modules) ** 0.5))
        rendered_modules = {}
        for i, mod_item in enumerate(reversed(modules)):
            mod, mod_name = mod_item["instance"], mod_item["name"]
            setattr(mod, "name", mod_name)
            setattr(mod, "color", colours[mod_name])
            x = x0 + int(x_offset * ((i + 1) % n))
            y = y0 + int(y_offset * math.floor((i + 1) / n))
            setattr(mod, "x",  x)
            setattr(mod, "y", y)
            if "defaults" in mod_item:
                for key, raw_value in mod_item["defaults"].items():
                    if isinstance(raw_value, str):
                        try:
                            value = int(raw_value, 16)
                        except ValueError:
                            raise RuntimeError(f"couldn't parse {value} as hex string")
                    elif isinstance(raw_value, int):
                        value = raw_value
                    else:
                        raise RuntimeError(f"fx value of {raw_value} found; must be int or hex string")
                    try:
                        mod.set_raw(key, value)
                    except rv.errors.ControllerValueError as error:
                        raise RuntimeError(str(error))
            project.attach_module(mod)
            rendered_modules[mod_name] = mod
        for src, dest in modules.links:
            project.connect(rendered_modules[src],
                            output if dest == "Output" else rendered_modules[dest])
        return rendered_modules

    def render_pattern(self,
                       patterns,
                       tracks,
                       n_ticks,
                       modules,
                       controllers,
                       x,
                       y,
                       colour,
                       height = PatternHeight):
        trigs = [{note.i: note
                  for note in track}
                 for track in tracks]
        def note_fn(self, j, i):
            return trigs[i][j].render(modules,
                                      controllers) if j in trigs[i] else rv.note.Note()
        pattern = rv.pattern.Pattern(lines = n_ticks,
                                     tracks = len(tracks),
                                     x = x,
                                     y = y,
                                     y_size = height,
                                     bg_color = colour).set_via_fn(note_fn)
        patterns.append(pattern)

    def render_blank(self,
                     patterns,
                     n_ticks,
                     x,
                     y,
                     colour,
                     height = PatternHeight):
        def note_fn(self, j, i):
            return rv.note.Note()
        pattern = rv.pattern.Pattern(lines = n_ticks,
                                     tracks = 1,
                                     x = x,
                                     y = y,
                                     y_size = height,
                                     bg_color = colour).set_via_fn(note_fn)
        patterns.append(pattern)
    
    def render_controllers(self, modules):
        controllers = {}
        for mod in modules.values():
            controllers.setdefault(mod.name, {})
            for controller in mod.controllers.values():
                controllers[mod.name].setdefault(controller.name, {})
                controllers[mod.name][controller.name] = controller.number
        return controllers

    def render_patch(self,
                     patterns,
                     tracks,
                     n_ticks,
                     modules,
                     controllers,
                     x,
                     y,
                     colour):
        if tracks != []:
            self.render_pattern(patterns = patterns,
                                tracks = tracks,
                                n_ticks = n_ticks,
                                modules = modules,
                                controllers = controllers,
                                x = x,
                                y = y,
                                colour = colour)
        else:
            self.render_blank(patterns = patterns,
                              n_ticks = n_ticks,
                              x = x,
                              y = y,
                              colour = colour)
        x += n_ticks

    def render_patches(self,
                       modules,
                       colours,
                       patches,
                       phrase_size = 4,
                       height = PatternHeight):
        x_count = 1
        mod_names = list(modules.keys())
        controllers = self.render_controllers(modules)
        patterns, x, y = [], 0, 0
        track_colours = dict(colours)
        for i, patch in enumerate(patches):
            n_ticks = patch.n_ticks
            if 0 == i % phrase_size:
                track_colours = init_colours(list(modules.keys()))
            for mod_name, group in patch.trig_groups(mod_names).items():
                tracks = list(group.values())
                colour = track_colours[mod_name]
                self.render_patch(patterns = patterns,
                                  tracks = tracks,
                                  n_ticks = n_ticks,
                                  modules = modules,
                                  controllers = controllers,
                                  x = x,
                                  y = y,
                                  colour = colour)
                y += height
            x += x_count * n_ticks
            y = 0
        return patterns      
    
    @init_project
    def render_project(self,
                       patches,
                       modules,
                       banks, 
                       bpm,
                       volume = Volume):
        colours = init_colours([mod["name"] for mod in modules])
        project = rv.api.Project()
        project.initial_bpm = bpm
        project.global_volume = volume
        project_modules = self.render_modules(project = project,
                                              patches = patches,
                                              modules = modules,
                                              colours = colours,
                                              banks = banks)
        project.patterns = self.render_patches(modules = project_modules,
                                               colours = colours,
                                               patches = patches)
        return project

if __name__=="__main__":
    pass
