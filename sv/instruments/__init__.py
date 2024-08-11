import copy
import yaml

def load_yaml(base_path, file_name):
    return yaml.safe_load(open("/".join(base_path.split("/")[:-1] + [file_name])).read())

def add_to_patch(fn):
    def wrapped(self, *args, **kwargs):
        trigs = fn(self, *args, **kwargs)
        self.container.add_trigs(trigs)
    return wrapped

class InstrumentBase:

    def __init__(self, container, namespace):
        self.container = container
        self.namespace = namespace

    @property
    def modules(self):
        modules = copy.deepcopy(self.Modules)
        for module in modules:
            module["name"] = f"{self.namespace}{module['name']}"
            if "links" in module:
                links = module["links"]
                for i, link in enumerate(links):
                    if link != "Output":
                        links[i] = f"{self.namespace}{link}"
        return modules
        
if __name__ == "__main__":
    pass
