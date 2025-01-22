from sv.utils.cli.git import Git
from sv.utils.cli.colours import Colours
from sv.utils.cli.model import Project
from sv.utils.cli.parse import parse_line

import cmd
import logging
import os
import sys

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

class BaseCLI(cmd.Cmd):

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


