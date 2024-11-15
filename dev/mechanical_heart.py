import rv.api

from rv.readers.reader import read_sunvox_file

import logging
import sys

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
        print(modules)
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
                    
if __name__ == "__main__":
    try:
        project = read_sunvox_file("dev/mechanical-heart.sunvox")
        ModuleChain.parse_modules(project)
    except RuntimeError as error:
        logging.error(str(error))

                        
