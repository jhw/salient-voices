import importlib
import random

def random_seed():
    return int(1e8*random.random())

def Q(seed):
    q = random.Random()
    q.seed(seed)
    return q

def load_class(path):
    tokens = path.split(".")            
    mod_path, class_name = ".".join(tokens[:-1]), tokens[-1]
    module=importlib.import_module(mod_path)
    return getattr(module, class_name)
    
if __name__=="__main__":
    pass
