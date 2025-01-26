from sv.client.colours import Colours
from sv.client.export import export_wav
from sv.client.git import Git
from sv.client.model import Project
from sv.client.parse import parse_line

from pydub import AudioSegment

import argparse
import cmd
import io
import json
import logging
import os
import random
import sys
import zipfile

logging.basicConfig(stream = sys.stdout,
                    level = logging.INFO,
                    format = "%(levelname)s: %(message)s")

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

def parse_args(config):
    parser = argparse.ArgumentParser(description="SV client")
    for item in config:
        kwargs = {"type": eval(item["type"])}
        if "default" in item:
            kwargs["default"] = item["default"]
        parser.add_argument(f"--{item['name']}", **kwargs)
    args, errors = parser.parse_args(), []
    for item in config:
        if getattr(args, item['name']) == None:
            errors.append(f"please supply {item['name']}")
        else:
            value = getattr(args, item["name"])
            if ("file" in item and item["file"] and
                not os.path.exists(value)):
                errors.append(f"{value} does not exist")
            elif ("options" in item and
                value not in item["options"]):
                errors.append(f"{value} is not a valid options for {item['name']}")
            elif ("min" in item and
                  value < item["min"]):
                errors.append(f"{item['name']} is below min value")
            elif ("max" in item and
                  value > item["max"]):
                errors.append(f"{item['name']} exceeds max value")                
    if errors != []:
        raise RuntimeError(", ".join(errors))
    return args

class ClientCLI(cmd.Cmd):

    prompt = ">>> "

    def __init__(self,):
        super().__init__()
        self.git = Git()

    ### projects
        
    @assert_head
    @commit_and_render
    def do_render_project(self, _):
        return Project(patches = self.git.head.content.patches)

    def do_clean_projects(self, _,
                          directories = ["tmp/sunvox",
                                         "tmp/zip"]):
        while True:
            answer = input(f"Are you sure ?: ")
            if answer == "y":
                for dir_name in directories:
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
    
    ### patches
    
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
    def do_rand_seeds(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    track = random.choice(patch.tracks)
                    key = random.choice(list(track.seeds.keys()))
                    track.seeds[key] = int(random.random() * 1e8)
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

    def _init_meta_export(self, project):
        return {"project": {"bpm": self.bpm,
                            "n_patches": self.n_patches,
                            "n_ticks": self.n_ticks}}
    
    def _init_patches_export(self, project, fade = 3):
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
            meta = self._init_meta_export(project)
            zf.writestr("meta.json", json.dumps(meta,
                                                indent = 2))
            # patches
            patches_wav_io = self._init_patches_export(project)
            zf.writestr(f"{short_name}.wav", patches_wav_io.getvalue())
    
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

    ### exit
        
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        logging.info("Exiting ..")
        return True

if __name__ == "__main__":
    pass


