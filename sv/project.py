import importlib
import random
import rv
import rv.api # why?

Volume, Height = 256, 64

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

    def mutate(self,
               contrast = 32):
        values = range(-contrast, contrast)
        return SVColor([min(255, max(0, rgb + random.choice(values)))
                        for rgb in self])
                    
class SVOffset:

    def __init__(self):
        self.value = 0
        self.count = 0

    def increment(self, value):
        self.value += value
        self.count += 1
        
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
            for track in patch.tracks:
                for trig in track:
                    if (hasattr(trig, "sample") and trig.sample):
                        pool.add(trig.sample)
    
    def init_module_classes(fn):
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

    @init_module_classes
    def init_modules(self,                     
                     project,
                     patches,
                     modules,
                     banks):
        modules_ = {}
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
            modules_[name] = mod
        output = sorted(project.modules, key = lambda x: -x.index).pop()
        for src, dest in modules.links:
            project.connect(modules_[src],
                         output if dest == "Output" else modules_[dest])
        return modules_

    def attach_pattern(fn):
        def wrapped(*args, **kwargs):
            rv_pattern = fn(*args, **kwargs)
            kwargs["patterns"].append(rv_pattern)
            kwargs["offset"].increment(kwargs["patch"].n_ticks)
        return wrapped
    
    @attach_pattern
    def init_pattern(self,
                     patterns,
                     modules,
                     controllers,
                     patch,
                     offset,
                     color,
                     height = Height):
        trigs = [{note.i: note
                  for note in track}
                 for track in patch.tracks]
        def notefn(self, j, i):
            return trigs[i][j].render(modules,
                                      controllers) if j in trigs[i] else rv.note.Note()
        return rv.pattern.Pattern(lines = patch.n_ticks,
                                  tracks = len(patch.tracks),
                                  x = offset.value,
                                  y_size = height,
                                  bg_color = color).set_via_fn(notefn)

    @attach_pattern
    def init_blank(self,
                   patterns,
                   patch,
                   offset,
                   color,
                   height = Height):
        def notefn(self, j, i):
            return RVNote()
        return rv.pattern.Pattern(lines = patch.n_ticks,
                                  tracks = len(patch.tracks),
                                  x = offset.value,
                                  y_size = height,
                                  bg_color = color).set_via_fn(notefn)
    
    def init_controllers(self, modules):
        controllers = {}
        for mod in modules.values():
            controllers.setdefault(mod.name, {})
            for controller in mod.controllers.values():
                controllers[mod.name].setdefault(controller.name, {})
                controllers[mod.name][controller.name] = controller.number
        return controllers

    def init_patterns(self,
                      modules,
                      patches,
                      wash = False,
                      breaks = False):
        controllers = self.init_controllers(modules)
        offset = SVOffset()
        patterns, color = [], None
        for i, patch in enumerate(patches):
            color = SVColor.randomise() if 0 == i % 4 else color.mutate()
            for i in range(2 if wash else 1):
                self.init_pattern(patterns = patterns,
                                  modules = modules,
                                  controllers = controllers,
                                  patch = patch,
                                  offset = offset,
                                  color = color)
            if breaks:
                self.init_blank(patterns = patterns,
                                patch = patch,
                                offset = offset,
                                color = color)
        return patterns

    def init_render_args(fn):
        def wrapped(self, modules, banks, *args, **kwargs):
            banks = SVBanks({bank.name: bank for bank in banks})            
            modules = SVModConfigItems(modules)
            modules.validate()
            return fn(self,
                      modules = modules,
                      banks = banks,
                      *args, **kwargs)
        return wrapped
    
    @init_render_args
    def render(self,
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
        project_modules = self.init_modules(project = project,
                                            patches = patches,
                                            modules = modules,
                                            banks = banks)
        project.patterns = self.init_patterns(modules = project_modules,
                                              patches = patches,
                                              wash = wash,
                                              breaks = breaks)
        return project

if __name__=="__main__":
    pass
