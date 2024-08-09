import importlib
import math
import random
import rv
import rv.api # why?

"""
https://stackoverflow.com/questions/32131668/from-where-can-i-get-list-of-all-color-patterns-used-by-google-charts
"""

Colours = [(51, 102, 204), (220, 57, 18), (255, 153, 0), (16, 150, 24), (153, 0, 153), (0, 153, 198), (221, 68, 119), (102, 170, 0), (184, 46, 46), (49, 99, 149), (153, 68, 153), (34, 170, 153), (170, 170, 17), (102, 51, 204), (230, 115, 0), (139, 7, 7), (101, 16, 103), (50, 146, 98), (85, 116, 166), (59, 62, 172), (183, 115, 34), (22, 214, 32), (185, 19, 131), (244, 53, 158), (156, 89, 53), (169, 196, 19), (42, 119, 141), (102, 141, 28), (190, 164, 19), (12, 89, 34), (116, 52, 17)]

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
    
class SVModConfigItem(dict):

    def __init__(self, item = {}):
        dict.__init__(self, item)

    @property
    def links(self):
        links = []
        for link_dest in self["links"]:
            link = [self["name"], link_dest]
            links.append(link)
        return links

class SVModConfigItems(list):

    def __init__(self, items = []):
        list.__init__(self, [SVModConfigItem(item)
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

class SVBanks(dict):

    def __init__(self, item = []):
        dict.__init__(self, item)

    def get_wav_file(self, sample):
        bank_name, file_path = sample.split("/")
        if bank_name not in self:
            raise RuntimeError(f"bank {bank_name} not found")
        file_paths = self[bank_name].zip_file.namelist()
        if file_path not in file_paths:
            raise RuntimeError(f"path {file_path} not found in bank {bank_name}")
        return self[bank_name].zip_file.open(file_path, 'r')

class SVPool(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    def add(self, sample):
        if sample not in self:
            self.append(sample)
    
class SVProject:

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
                        patch.update_pool(pool = pool,
                                          mod_names = mod_names)
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

    @init_modules
    def render_modules(self,                     
                       project,
                       patches,                       
                       modules,
                       colours, 
                       banks,
                       x_offset = -128,
                       y_offset = -128,
                       x0 = 512,
                       y0 = 512):
        output = project.modules[0]
        """
        setattr(output, "x", 0)
        setattr(output, "y", 0)
        """
        n = int(math.ceil(len(modules) ** 0.5))
        rendered_modules = {}
        for i, mod_item in enumerate(modules):
            mod, mod_name = mod_item["instance"], mod_item["name"]
            setattr(mod, "name", mod_name)
            setattr(mod, "color", colours[mod_name])
            x = x0 + int(x_offset * (n - (i % n) - 1))
            y = y0 + int(y_offset * (n - math.floor(i / n) - 2))
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
                       color,
                       height = PatternHeight):
        trigs = [{note.i: note
                  for note in track}
                 for track in tracks]
        def notefn(self, j, i):
            return trigs[i][j].render(modules,
                                      controllers) if j in trigs[i] else rv.note.Note()
        pattern = rv.pattern.Pattern(lines = n_ticks,
                                     tracks = len(tracks),
                                     x = x,
                                     y = y,
                                     y_size = height,
                                     bg_color = color).set_via_fn(notefn)
        patterns.append(pattern)

    def render_blank(self,
                     patterns,
                     n_ticks,
                     x,
                     y,
                     color,
                     height = PatternHeight):
        def notefn(self, j, i):
            return rv.note.Note()
        pattern = rv.pattern.Pattern(lines = n_ticks,
                                     tracks = 1,
                                     x = x,
                                     y = y,
                                     y_size = height,
                                     bg_color = color).set_via_fn(notefn)
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
                     color,
                     wash,
                     breaks):
        for i in range(2 if wash else 1):
            if tracks != []:
                self.render_pattern(patterns = patterns,
                                    tracks = tracks,
                                    n_ticks = n_ticks,
                                    modules = modules,
                                    controllers = controllers,
                                    x = x,
                                    y = y,
                                    color = color)
            else:
                self.render_blank(patterns = patterns,
                                  n_ticks = n_ticks,
                                  x = x,
                                  y = y,
                                  color = color)
            x += n_ticks
        if breaks:
            self.render_blank(patterns = patterns,
                              n_ticks = n_ticks,
                              x = x,
                              y = y,
                              color = color)
            x += n_ticks
    
    def render_patches(self,
                       modules,
                       colours,
                       patches,
                       wash,
                       breaks,
                       height = PatternHeight):
        x_count = 1 + int(wash) + int(breaks)
        mod_names = list(modules.keys())
        controllers = self.render_controllers(modules)
        patterns, x, y = [], 0, 0
        for i, patch in enumerate(patches):
            n_ticks = patch.n_ticks
            for mod_name, group in patch.trig_groups(mod_names).items():
                tracks = list(group.values())
                color = colours[mod_name]
                self.render_patch(patterns = patterns,
                                  tracks = tracks,
                                  n_ticks = n_ticks,
                                  modules = modules,
                                  controllers = controllers,
                                  x = x,
                                  y = y,
                                  color = color,
                                  wash = wash,
                                  breaks = breaks)
                y += height
            x += x_count * n_ticks
            y = 0
        return patterns
    
    def init_project(fn):
        def wrapped(self, modules, banks, *args, **kwargs):
            banks = SVBanks({bank.name: bank for bank in banks})            
            modules = SVModConfigItems(modules)
            modules.validate()
            return fn(self,
                      modules = modules,
                      banks = banks,
                      *args, **kwargs)
        return wrapped

    def init_colours(self, modules, colours = Colours):
        mod_colours = {}
        for mod in modules:
            if colours == {}:
                raise RuntimeError("colour choices exhausted")
            colour = random.choice(colours)
            colours.remove(colour)
            mod_colours[mod["name"]] = colour
        return mod_colours

    @init_project
    def render_project(self,
                       patches,
                       modules,
                       banks, 
                       bpm,
                       colours = Colours,
                       wash = False,
                       breaks = False,
                       volume = Volume):
        project = rv.api.Project()
        project.initial_bpm = bpm
        project.global_volume = volume
        colours = self.init_colours(modules)
        project_modules = self.render_modules(project = project,
                                              patches = patches,
                                              modules = modules,
                                              colours = colours,
                                              banks = banks)
        project.patterns = self.render_patches(modules = project_modules,
                                               colours = colours,
                                               patches = patches,
                                               wash = wash,
                                               breaks = breaks)
        return project

if __name__=="__main__":
    pass
