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
        module_dict = {module['index']: module['name'] for module in modules}        
        def dfs(current_index, visited=None):
            if visited is None:
                visited = set()
            if current_index in visited or current_index not in module_dict:
                return []
            visited.add(current_index)
            current_module_name = module_dict[current_index]
            current_module = (current_module_name, current_index)
            if not modules[current_index]['links']['in']:
                return [ModuleChain([current_module])]
            chains = []
            for prev_index in modules[current_index]['links']['in']:
                if prev_index not in module_dict:
                    logging.warning(f"Skipping invalid module index: {prev_index}")
                    continue
                for chain in dfs(prev_index, visited.copy()):
                    chains.append(ModuleChain(chain + [current_module]))
            return sorted(chains, key=lambda x: x[0][1])
        return dfs(0)
    
    def __init__(self, items=[]):
        list.__init__(self, items)
        
if __name__ == "__main__":
    try:
        project = read_sunvox_file("dev/mechanical-heart.sunvox")
        print (ModuleChain.parse_modules(project))
    except RuntimeError as error:
        logging.error(str(error))

                        
