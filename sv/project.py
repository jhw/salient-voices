import importlib
import random
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
    
class SVColor(list):

    @classmethod
    def randomise(self,
                  offset = 64,
                  contrast = 128,
                  n = 16):
        def randomise(offset):
            return [int(offset + random.random() * (255 - offset))
                    for i in range(3)]
        for i in range(n):
            color = randomise(offset)
            if (max(color) - min(color)) > contrast:
                return SVColor(color)
        return SVColor([127 for i in range(3)])
    
    def __init__(self, rgb = []):
        list.__init__(self, rgb)

class SVOffset:

    def __init__(self, value = 0):
        self.value = value

    def set_value(self, value):
        self.value = value
        
    def inc_value(self, value):
        self.value += value
        
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

    def populate_sample_pool(self, patches, pool):
        for patch in patches:
            for _, group in patch.track_groups.items():
                for _, track in group.items():
                    for trig in track:
                        if (hasattr(trig, "sample") and trig.sample):
                            pool.add(trig.sample)
    
    def init_modules(fn):
        def wrapped(self,
                    project,
                    patches,
                    modules,
                    banks):
            for mod in modules:
                mod_class = load_class(mod["class"])
                mod_kwargs = {}
                if mod["class"].lower().endswith("sampler"):
                    pool = SVPool()
                    self.populate_sample_pool(patches = patches,
                                              pool = pool)
                    mod_kwargs = {"banks": banks,
                                  "pool": pool}
                mod["instance"] = mod_class(**mod_kwargs)
            return fn(self,
                      project = project,
                      patches = patches,
                      modules = modules,
                      banks = banks)
        return wrapped

    @init_modules
    def render_modules(self,                     
                       project,
                       patches,
                       modules,
                       banks):
        rendered_modules = {}
        for i, moditem in enumerate(modules):
            mod, name = moditem["instance"], moditem["name"]
            setattr(mod, "name", name)
            if "defaults" in moditem:
                for key, raw_value in moditem["defaults"].items():
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
            rendered_modules[name] = mod
        output = sorted(project.modules, key = lambda x: -x.index).pop()
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
                       x_offset,
                       y_offset,
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
                                     x = x_offset.value,
                                     y = y_offset.value,
                                     y_size = height,
                                     bg_color = color).set_via_fn(notefn)
        patterns.append(pattern)

    def render_blank(self,
                     patterns,
                     tracks,
                     n_ticks,
                     x_offset,
                     y_offset,
                     color,
                     height = PatternHeight):
        def notefn(self, j, i):
            return rv.note.Note()
        pattern = rv.pattern.Pattern(lines = n_ticks,
                                     tracks = len(tracks),
                                     x = x_offset.value,
                                     y = y_offset.value,
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
                     x_offset,
                     y_offset,
                     color,
                     wash,
                     breaks):
        for i in range(2 if wash else 1):
            self.render_pattern(patterns = patterns,
                                tracks = tracks,
                                n_ticks = n_ticks,
                                modules = modules,
                                controllers = controllers,
                                x_offset = x_offset,
                                y_offset = y_offset,
                                color = color)
            x_offset.inc_value(n_ticks)
        if breaks:
            self.render_blank(patterns = patterns,
                              tracks = tracks,
                              n_ticks = n_ticks,
                              x_offset = x_offset,
                              y_offset = y_offset,
                              color = color)
            x_offset.inc_value(n_ticks)
    
    def render_patches(self,
                       modules,
                       patches,
                       wash,
                       breaks,
                       height = PatternHeight):
        count = 1 + int(wash) + int(breaks)
        controllers = self.render_controllers(modules)
        x_offset, y_offset = SVOffset(), SVOffset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            n_ticks = patch.n_ticks
            color = SVColor.randomise()            
            for _, group in patch.track_groups.items():
                tracks = list(group.values())
                self.render_patch(patterns = patterns,
                                  tracks = tracks,
                                  n_ticks = n_ticks,
                                  modules = modules,
                                  controllers = controllers,
                                  x_offset = x_offset,
                                  y_offset = y_offset,
                                  color = color,
                                  wash = wash,
                                  breaks = breaks)
                x_offset.inc_value(-1 * count * n_ticks)
                y_offset.inc_value(height)
            x_offset.inc_value(count * n_ticks)
            y_offset.set_value(0)
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
    
    @init_project
    def render_project(self,
                       patches,
                       modules,
                       banks, 
                       bpm,
                       wash = False,
                       breaks = False,
                       volume = Volume):
        project = rv.api.Project()
        project.initial_bpm = bpm
        project.global_volume = volume
        project_modules = self.render_modules(project = project,
                                              patches = patches,
                                              modules = modules,
                                              banks = banks)
        project.patterns = self.render_patches(modules = project_modules,
                                               patches = patches,
                                               wash = wash,
                                               breaks = breaks)
        return project

if __name__=="__main__":
    pass
