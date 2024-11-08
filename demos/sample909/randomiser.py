# from sv.banks import SVBanks
from sv.banks import SVBank, SVBanks
# from sv.utils.banks import init_banks
from sv.utils.cli.parse import parse_line
from sv.utils.export import export_wav
from sv.utils.naming import random_name

from model import Patches, Track

from datetime import datetime

# import boto3
import cmd
import logging
import os
import random
import re
import sys
import yaml
import zipfile

logging.basicConfig(stream = sys.stdout,
                    level = logging.INFO,
                    format = "%(levelname)s: %(message)s")

Tracks = yaml.safe_load("""
- name: kick
  temperature: 0.5
  density: 0.5
- name: clap
  temperature: 0.25
  density: 0.25
- name: hat
  temperature: 0.75
  density: 0.75
""")

# Terms = yaml.safe_load(open("terms.yaml").read())

Terms = yaml.safe_load(open("/".join(__file__.split("/")[:-1] + ["terms.yaml"])).read())

def timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")

def assert_patches(fn):
    def wrapped(self, *args, **kwargs):
        try:
            if self.patches == []:
                raise RuntimeError("patches not found")
            return fn(self, *args, **kwargs)
        except RuntimeError as error:            
            logging.error(str(error))
    return wrapped

def init_output(fn):
    def wrapped(*args, **kwargs):
        for dir_name in ["tmp/sunvox",
                         "tmp/wav"]:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        return fn(*args, **kwargs)
    return wrapped

def render_patches(levels = {track["name"]: 1
                             for track in Tracks}):
    def decorator(fn):
        def wrapped(self, *args, **kwargs):
            fn(self, *args, **kwargs)
            container = self.patches.render(banks = self.banks,
                                            levels = levels)
            self.commit_name = random_name()
            file_name = f"{timestamp()}-{self.commit_name}"
            logging.info(f"writing to {file_name}")
            container.write_project(f"tmp/sunvox/{file_name}.sunvox")
        return wrapped
    return decorator

class RandomiserCLI(cmd.Cmd):

    prompt = ">>> "
                    
    intro = f"Welcome to the 909 randomiser CLI ;)"

    def __init__(self, banks, pool,
                 tracks = Tracks,
                 tag_mapping = {track["name"]: track["name"]
                                for track in Tracks},
                 terms = Terms,
                 n_patches = 16):
        super().__init__()
        self.banks = banks
        self.pool = pool
        self.tracks = tracks
        self.tag_mapping = dict(tag_mapping)
        self.terms = terms
        self.n_patches = n_patches
        self.patches = []
        self.commit_name = None

    ### tags

    def do_tags(self, _):
        logging.info(yaml.safe_dump(self.tag_mapping,
                             default_flow_style = False))
    
    @parse_line([{"name": "key",
                  "type": "enum",
                  "options": [track["name"] for track in Tracks]},
                 {"name": "value",
                  "type": "enum",
                  "options": list(Terms.keys())}])
    def do_set_tag(self, key, value):
        self.tag_mapping[key] = value
        self.do_tags(None)

    def do_randomise_tags(self, _):
        self.tag_mapping = {key: random.choice(list(self.terms.keys()))
                            for key in self.tag_mapping}
        self.do_tags(None)

    def do_reset_tags(self, _, tag_mapping = {track["name"]: track["name"]
                                              for track in Tracks}):
        self.tag_mapping = tag_mapping
        self.do_tags(None)

    ### patch operations

    @init_output
    @render_patches()
    def do_randomise_patches(self, _):
        self.patches = Patches.randomise(pool = self.pool,
                                         tracks = self.tracks,
                                         tag_mapping = self.tag_mapping,
                                         n = self.n_patches)

    @assert_patches    
    @parse_line([{"name": "key",
                  "type": "enum",
                  "options": [track["name"] for track in Tracks]}])
    @init_output
    @render_patches()
    def do_randomise_track(self, key):
        tracks = {track["name"]: track for track in self.tracks}
        for patch in self.patches[1:]:
            track = Track.randomise(track = tracks[key],
                                    pool = self.pool,
                                    tag_mapping = self.tag_mapping)
            patch.replace_track(track)

        
    @assert_patches
    @parse_line([{"name": "i",
                  "type": "int"}])
    @init_output
    @render_patches()
    def do_clone_col(self, i):
        root = self.patches[i % len(self.patches)]
        self.patches = Patches([root.clone()
                                for i in range(self.n_patches)])

        
    @assert_patches
    @parse_line([{"name": "n",
                  "type": "int"}])
    @init_output
    @render_patches()
    def do_shuffle_samples(self, n):
        for patch in self.patches[1:]:
            for _ in range(n):
                patch.shuffle(attr = "samples",
                              pool = self.pool,
                              tag_mapping = self.tag_mapping)

    @assert_patches
    @parse_line([{"name": "n",
                  "type": "int"}])
    @init_output
    @render_patches()
    def do_shuffle_pattern(self, n):
        for patch in self.patches[1:]:
            for _ in range(n):
                patch.shuffle(attr = "pattern")

    @assert_patches
    @parse_line([{"name": "n",
                  "type": "int"}])
    @init_output
    @render_patches()
    def do_shuffle_seeds(self, n):
        for patch in self.patches[1:]:
            for _ in range(n):
                patch.shuffle(attr = "seeds")

    @assert_patches
    @init_output
    def do_export_wav(self, _, mute_level = 0.01): # TEMP
        def level(track, solo):
            return 1 if (track["name"] == solo or solo == None) else mute_level
        def levels(tracks, solo = None):
            return {track["name"]: level(track, solo) for track in tracks}
        wav_stem = "-".join([tok[:3] for tok in self.commit_name.split("-")])
        zip_name = f"tmp/wav/{self.commit_name}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            wav_config = [(levels(self.tracks), "all")]
            for track in self.tracks:
                wav_config.append((levels(self.tracks, track["name"]),
                                   track["name"][:3]))
            for levels, wav_suffix in wav_config:
                container = self.patches.render(banks = self.banks,
                                                levels = levels)
                project = container.render_project()
                wav_io = export_wav(project = project)
                wav_name = f"{wav_stem}-{wav_suffix}.wav"
                zip_file.writestr(wav_name, wav_io.getvalue())
                
    ### exit
        
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        logging.info("Exiting ..")
        return True

"""
def env_value(key):
    if (key not in os.environ or
        os.environ[key] in ["", None]):
        raise RuntimeError(f"{key} not defined")
    return os.environ[key]
"""
        
if __name__ == "__main__":
    try:
        """
        s3 = boto3.client("s3")
        bucket_name = env_value("SV_BANKS_HOME")               
        init_banks(s3 = s3,
                   bucket_name = bucket_name)        
        """
        bank = SVBank.load_zip("demos/sample909/pico-default.zip")
        banks = SVBanks([bank])
        pool, _ = banks.spawn_pool(tag_mapping = Terms)
        RandomiserCLI(banks = banks,
                      pool = pool).cmdloop()
    except RuntimeError as error:
        logging.error(str(error))
