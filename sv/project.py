from rv.modules.multisynth import MultiSynth

from sv.bank import SVPool
from sv.trigs import SVSampleTrig, controller_value

import importlib
import math
import rv

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

def does_class_extend(cls, base_class):
    try:
        return issubclass(cls, base_class)
    except TypeError:
        return False
    
class SVModule(dict):

    def __init__(self, item = {}):
        dict.__init__(self, item)

    @property
    def is_sampler(self):
        return does_class_extend(load_class(self["class"]),
                                 rv.modules.sampler.Sampler)

    def init_sample_pool(self, patches):
        pool = SVPool()
        for patch in patches:
            for trig in patch.trigs:
                if (isinstance(trig, SVSampleTrig) and 
                    trig.mod == self["name"]):
                    pool.add(trig.note_adjusted_sample)
        return pool
    
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
    def wrapped(self, modules, bank = None, *args, **kwargs):
        modules = SVModules(modules)
        modules.validate()
        return fn(self,
                  modules = modules,
                  bank = bank,
                  *args, **kwargs)
    return wrapped

def init_modules(fn):
    def wrapped(self,
                patches,
                modules,
                bank,
                **kwargs):
        for mod in modules:
            mod_class = load_class(mod["class"])
            mod_kwargs = {}
            if mod.is_sampler:
                pool = mod.init_sample_pool(patches)
                mod_kwargs = {"bank": bank,
                              "pool": pool,
                              "root": mod["root"]}
            mod["instance"] = mod_class(**mod_kwargs)
            # START sunvox-2.0-file-format TEMP CODE
            if isinstance(mod["instance"], MultiSynth):
                mod["instance"].out_port_mode = MultiSynth.OutPortMode.all_or_random1
            # END sunvox-2.0-file-format TEMP CODE
        return fn(self,
                  patches = patches,
                  modules = modules,
                  bank = bank,
                  **kwargs)
    return wrapped

"""
Project rendering doesn't necessarily have to be class based but there's so much rendering going on it's simplest to encapsulate it all in a class
"""

class SVProject:

    @init_modules
    def render_modules(self,                     
                       project,
                       modules,
                       **kwargs):
        output = project.modules[0]
        n = int(math.ceil(len(modules) ** 0.5))
        rendered_modules = {}
        for i, mod_item in enumerate(reversed(modules)):
            mod, mod_name, mod_colour = mod_item["instance"], mod_item["name"], mod_item["colour"]
            setattr(mod, "name", mod_name)
            setattr(mod, "color", mod_colour)
            if "defaults" in mod_item:
                for key, raw_value in mod_item["defaults"].items():
                    value = controller_value(raw_value)
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
                       patches,
                       phrase_size = 4,
                       height = PatternHeight):
        x_count = 1
        mod_names = list(modules.keys())
        controllers = self.render_controllers(modules)
        patterns, x, y = [], 0, 0
        for i, patch in enumerate(patches):
            n_ticks = patch.n_ticks
            for mod_name, group in patch.trig_groups(mod_names).items():
                tracks = list(group.values())
                self.render_patch(patterns = patterns,
                                  tracks = tracks,
                                  n_ticks = n_ticks,
                                  modules = modules,
                                  controllers = controllers,
                                  x = x,
                                  y = y,
                                  colour = patch.colour)
                y += height
            x += x_count * n_ticks
            y = 0
        return patterns      
    
    @init_project
    def render_project(self,
                       patches,
                       modules,
                       bpm,
                       bank = None,
                       volume = Volume):
        project = rv.api.Project()
        project.initial_bpm = bpm
        project.global_volume = volume
        project_modules = self.render_modules(project = project,
                                              patches = patches,
                                              modules = modules,
                                              bank = bank)
        project.layout() # NB
        project.patterns = self.render_patches(modules = project_modules,
                                               patches = patches)
        return project

if __name__=="__main__":
    pass
