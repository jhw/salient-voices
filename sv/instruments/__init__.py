import copy
import yaml

def load_yaml(base_path, file_name):
    return yaml.safe_load(open("/".join(base_path.split("/")[:-1] + [file_name])).read())

class InstrumentBase:

    def __init__(self, container, namespace):
        self.container = container
        self.namespace = namespace

    def play(self, generator, n):
        for trigs in generator(self, n):
            self.container.add_trigs(trigs)
        
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
