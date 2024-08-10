import random
import yaml

def load_yaml(file_name):
    return yaml.safe_load(open("/".join(__file__.split("/")[:-1] + [file_name])).read())

Nouns      = load_yaml("nouns.yaml")
Adjectives = load_yaml("adjectives.yaml")
                          
def random_name(nouns = Nouns,
                adjectives = Adjectives):
    return "%s-%s" % (random.choice(adjectives),
                      random.choice(nouns))

if __name__ == "__main__":
    pass
