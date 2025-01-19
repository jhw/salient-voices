from sv.utils.export import export_wav

import euclid
import perkons

from bank import Bank
from generators import Beat, GhostEcho
from git import Git
from model import Project, Patches, Patch, Tracks, Track
from colours import Colours
from parse import parse_line

from pydub import AudioSegment

import argparse
import cmd
import inspect
import io
import json
import logging
import os
import random
import sys
import yaml
import zipfile

logging.basicConfig(stream = sys.stdout,
                    level = logging.INFO,
                    format = "%(levelname)s: %(message)s")

def random_seed():
    return int(random.random() * 1e8)

def random_euclid_pattern():
    pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"],
                                          random.choice(euclid.TidalPatterns)[:2])}
    return {"mod": "euclid",
            "fn": "bjorklund",
            "args": pattern_kwargs}

def random_perkons_groove():
    groove_fns = [name for name, _ in inspect.getmembers(perkons, inspect.isfunction)]    
    return {"mod": "perkons",
            "fn": random.choice(groove_fns)}


def assert_head(fn):
    def wrapped(self, *args, **kwargs):
        try:
            if self.git.is_empty():
                raise RuntimeError("Please create a commit first")
            return fn(self, *args, **kwargs)
        except RuntimeError as error:            
            logging.warning(str(error))
    return wrapped

def commit_and_render(fn):
    def wrapped(self, *args, **kwargs):
        project = fn(self, *args, **kwargs)
        colours = Colours.randomise(tracks = self.tracks,
                                    patches = project.patches)
        container = project.render(bank = self.bank,
                                   generators = self.generators,
                                   colours = colours,
                                   bpm = self.bpm,
                                   n_ticks = self.n_ticks)
        commit_id = self.git.commit(project)
        if not os.path.exists("tmp/sunvox"):
            os.makedirs("tmp/sunvox")
        container.write_project(f"tmp/sunvox/{commit_id}.sunvox")
    return wrapped

class Tags(dict):

    def __init__(self, tags):
        dict.__init__(self, tags)

    def __str__(self):
        return ", ".join([f"{k}={','.join(v)}" for k, v in self.items()])

class TrackConfig(list):

    def __init__(self, items):
        list.__init__(self, items)

    @property
    def tags(self):
         return Tags({track["name"]: track["tags"] for track in self})
        
    def cross_validate(self, bank):
        tag_groups = bank.tag_groups
        for track in tracks:
            for tag in track["tags"]:
                if tag not in tag_groups:
                    raise RuntimeError(f"tag {tag} not found in pool")
    
class Euclid09CLI(cmd.Cmd):

    prompt = ">>> "
    intro = "Welcome to the Euclid09 CLI ;)"

    def __init__(self, bank, tracks, generators, bpm, n_patches, n_ticks):
        super().__init__()
        self.bank = bank
        self.tracks = tracks
        self.tags = self.tracks.tags
        self.generators = generators                
        self.bpm = bpm
        self.n_patches = n_patches
        self.n_ticks = n_ticks
        self.git = Git()
        
    @property
    def tick_length(self):
        return int(self.bpm * 1000 / (60 * self.n_ticks))
        
    @property
    def track_pool(self):
        tag_groups = self.bank.tag_groups
        pool = {}
        for name, tags in self.tags.items():
            pool.setdefault(name, [])
            for tag in tags:
                pool[name] += tag_groups[tag]
        return pool
                
    ### tag operations

    def do_show_tags(self, _):
        logging.info(self.tags)

    @parse_line([{"name": "n", "type": "int"}])
    def do_rand_tags(self, n):
        taglist = list(self.bank.tag_groups.keys())
        random.shuffle(taglist)
        tags, j = {}, 0
        for track in self.tracks:
            tags[track["name"]] = []
            for i in range(n):
                tag = taglist[j % len(taglist)]
                tags[track["name"]].append(tag)
                j += 1
        self.tags = Tags(tags)
        logging.info(self.tags)

    def do_reset_tags(self, _):
        self.tags = self.tracks.tags
        logging.info(self.tags)
    
    ### patch operations
    
    @commit_and_render
    def do_rand_project(self, _, n_samples = 2):
        project = Project(patches = Patches())
        for i in range(self.n_patches):
            patch = Patch(tracks = Tracks())
            for _track in self.tracks:
                seeds = {key: random_seed()
                         for key in "fx|vol|beat|sample".split("|")}
                pool = self.track_pool[_track["name"]]
                samples = [random.choice(pool) for i in range(n_samples)]
                track = Track(name = _track["name"],
                              machine = _track["machine"],
                              pattern = random_euclid_pattern(),
                              groove =  random_perkons_groove(),
                              seeds =  seeds,
                              temperature =  _track["temperature"],
                              density = _track["density"],
                              samples = samples)
                patch.tracks.append(track)
            project.patches.append(patch)
        return project

    @assert_head
    @commit_and_render
    def do_render_project(self, _):
        return Project(patches = self.git.head.content.patches)
    
    @assert_head
    @parse_line([{"name": "I", "type": "hexstr"}])
    @commit_and_render
    def do_clone_patches(self, I):
        roots = self.git.head.content.patches
        project = Project()
        for i in range(self.n_patches):
            j = I[i % len(I)]
            patch = roots[j].clone()
            project.patches.append(patch)
        project.freeze_patches(len(I))
        return project    
    
    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_rand_samples(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    track = random.choice(patch.tracks)
                    samples = self.track_pool[track.name]
                    i = int(random.random() > 0.5)
                    track.samples[i] = random.choice(samples)
        return project
    
    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_rand_patterns(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    track = random.choice(patch.tracks)
                    q = 3 * random.random()
                    if q < 1:
                        track.pattern = random_euclid_pattern()
                    elif q < 2:
                        track.groove = random_perkons_groove()
                    else:
                        key = random.choice(list(track.seeds.keys()))
                        track.seeds[key] = random_seed()
        return project

    @assert_head
    @parse_line([{"name": "threshold", "type": "float"}])
    @commit_and_render
    def do_rand_mutes(self, threshold):
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for track in patch.tracks:
                    track.muted = random.random() < threshold
        return project

    @assert_head
    @commit_and_render
    def do_reset_mutes(self, threshold):
        project = self.git.head.content.clone()
        for patch in project.patches:
            for track in patch.tracks:
                track.muted = False
        return project
    
    ### export

    def _init_metadata(self, project):
        samples = project.samples
        return {"project": {"bpm": self.bpm,
                            "n_patches": self.n_patches,
                            "n_ticks": self.n_ticks},
                "samples": samples}
    
    def _init_patches_wav(self, project, fade = 3):
        container = project.render(bank = self.bank,
                                   generators = self.generators,
                                   bpm = self.bpm,
                                   n_ticks = self.n_ticks,
                                   firewall = True) # NB
        sv_project = container.render_project()
        wav_io = export_wav(project = sv_project)
        audio = AudioSegment.from_file(wav_io, format = "wav")
        slice_size = len(audio) / (self.n_patches * 2)
        patches_audio = AudioSegment.silent(duration = 0)
        for i in range(self.n_patches):
            j = 2 * i
            start, end = j * slice_size, (j + 1) * slice_size
            slice_audio = audio[start:end].fade_in(fade).fade_out(fade)
            patches_audio += slice_audio
        patches_io = io.BytesIO()
        patches_audio.export(patches_io, format = "wav")
        patches_io.seek(0)
        return patches_io

    def _init_chain_wav(self, project, n_ticks = 4, fade = 3):
        chain_audio = AudioSegment.silent(duration = 0)
        slice_size = self.tick_length * n_ticks
        for sample in project.samples:
            wav_io = self.bank.get_wav(sample)
            slice_audio = AudioSegment.from_file(wav_io, format = "wav")
            if len(slice_audio) < slice_size:
                chain_audio += slice_audio.fade_out(fade)
                padding_size = slice_size - len(slice_audio)
                chain_audio += AudioSegment.silent(duration = padding_size)
            else:
                chain_audio += slice_audio[:slice_size].fade_out(fade)
        chain_io = io.BytesIO()
        chain_audio.export(chain_io, format = "wav")
        chain_io.seek(0)
        return chain_io
        
    @assert_head
    def do_export_zip(self, _):
        def format_short_name(entry, n=3):
            return "-".join([tok[:n] for tok in entry.split(".")[0].split("-")])        
        if not os.path.exists("tmp/zip"):
            os.makedirs("tmp/zip")
        commit_id = self.git.head.commit_id
        zip_name = f"tmp/zip/{commit_id.slug}-{self.bpm}.zip"
        short_name = format_short_name(commit_id.slug)
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            project = self.git.head.content
            # metadata
            metadata = self._init_metadata(project)
            zf.writestr("meta.json", json.dumps(metadata,
                                                indent = 2))
            # patches
            patches_wav_io = self._init_patches_wav(project)
            zf.writestr(f"{short_name}-pat-{self.n_patches}.wav", patches_wav_io.getvalue())
            # chain
            chain_wav_io = self._init_chain_wav(project)
            zf.writestr(f"{short_name}-cha-{len(project.samples)}.wav", chain_wav_io.getvalue())

    ### git
    
    def do_git_head(self, _):
        if self.git.is_empty():
            logging.warning("Git has no commits")
        else:
            logging.info(f"HEAD is {self.git.head.commit_id}")

    def do_git_log(self, _):
        for commit in self.git.commits:
            logging.info(commit.commit_id)

    def do_git_checkout(self, commit_id):
        self.git.checkout(commit_id)
        
    def do_git_undo(self, _):
        self.git.undo()

    def do_git_redo(self, _):
        self.git.redo()

    ### project management

    def do_clean_projects(self, _):
        while True:
            answer = input(f"Are you sure ?: ")
            if answer == "y":
                for dir_name in ["tmp/sunvox",
                                 "tmp/zip"]:
                    if os.path.exists(dir_name):
                        logging.info(f"cleaning {dir_name}")
                        for filename in os.listdir(dir_name):
                            file_path = os.path.join(dir_name, filename)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                self.git = Git()
                break
            elif answer == "n":
                break
            elif answer == "q":
                return 

    ### exit
        
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        logging.info("Exiting ..")
        return True

def parse_args(default_pattern = ".*",
               default_bpm = 120,
               default_n_ticks = 16,
               default_n_patches = 16,
               default_cutoff = 250): # 2 * 2000 / 16 == two ticks @ 120 bpm
    parser = argparse.ArgumentParser(description="Run Euclid09CLI with specified parameters.")
    parser.add_argument(
        "--pattern",
        type=str,
        default=default_pattern,
        help=f"A string for matching sample paths(default: {default_pattern})."
    )
    parser.add_argument(
        "--bpm",
        type=int,
        default=default_bpm,
        help=f"An integer > 0 specifying the beats per minute (default: {default_bpm})."
    )
    parser.add_argument(
        "--n_ticks",
        type=int,
        default=default_n_ticks,
        help=f"An integer > 0 specifying the number of ticks (default: {default_n_ticks})."
    )
    parser.add_argument(
        "--n_patches",
        type=int,
        default=default_n_patches,
        help=f"An integer > 0 specifying the number of patches (default: {default_n_patches})."
    )
    parser.add_argument(
        "--cutoff",
        type=float,
        default=default_cutoff,
        help=f"A float > 0 specifying the cutoff value (default: {default_cutoff})."
    )  
    args = parser.parse_args()
    if args.bpm <= 0:
        parser.error("bpm must be an integer greater than 0.")
    if args.n_ticks <= 0:
        parser.error("n_ticks must be an integer greater than 0.")
    if args.n_patches <= 0:
        parser.error("n_patches must be an integer greater than 0.")
    if args.cutoff <= 0:
        parser.error("cutoff must be a float greater than 0.")
    return args

def load_yaml(file_name):
    return yaml.safe_load(open("/".join(__file__.split("/")[:-1] + [file_name])).read())

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = Bank.initialise(args.pattern)
        tracks = TrackConfig(load_yaml("tracks.yaml"))
        tracks.cross_validate(bank)
        Euclid09CLI(bank = bank,
                    tracks = tracks,
                    generators = [Beat, GhostEcho],
                    bpm = args.bpm,
                    n_ticks = args.n_ticks,
                    n_patches = args.n_patches).cmdloop()                
    except ValueError as error:
        logging.error(str(error))
    except RuntimeError as error:
        logging.error(str(error))



