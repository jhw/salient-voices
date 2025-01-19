from sv.utils.naming import random_name

from datetime import datetime

import logging
import re

class CommitId:

    @staticmethod
    def randomise():
        return CommitId(slug=random_name(),
                        timestamp=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"))

    @staticmethod
    def from_filename(filename):
        tokens = filename.split(".")[0].split("-")
        return CommitId(slug="-".join(tokens[-2:]),
                        timestamp="-".join(tokens[:6]))

    def __init__(self, slug, timestamp):
        self.slug = slug
        self.timestamp = timestamp

    @property
    def short_name(self):
        def format_slug(text, n=3):
            clean_text = text[0] + re.sub("a|e|i|o|u", "", text[1:])
            return clean_text[:n] if len(clean_text) >= n else text[:n]
        return "-".join([format_slug(tok) for tok in self.slug.split("-")])

    def __str__(self):
        return f"{self.timestamp}-{self.slug}"

class Commit:

    def __init__(self, commit_id, content):
        self.commit_id = commit_id
        self.content = content

class Git:

    def __init__(self):
        self.commits = []
        self.head_index = -1
        self.redo_stack = []

    def is_empty(self):
        return self.head_index == -1

    @property
    def head(self):
        return self.commits[self.head_index] if not self.is_empty() else None

    def commit(self, content):
        new_commit = Commit(commit_id=CommitId.randomise(), content=content)
        self.commits = self.commits[:self.head_index + 1]
        self.commits.append(new_commit)
        self.head_index += 1
        self.redo_stack.clear()
        logging.info(f"HEAD is {new_commit.commit_id}")
        return new_commit.commit_id

    def checkout(self, commit_id_str):
        for commit in self.commits:
            if str(commit.commit_id) == commit_id_str:
                new_commit = Commit(commit_id=CommitId.randomise(),
                                    content=commit.content.clone())
                self.commits = self.commits[:self.head_index + 1]
                self.commits.append(new_commit)
                self.head_index += 1
                self.redo_stack.clear()
                logging.info(f"Checked out to new commit at HEAD: {new_commit.commit_id}")
                return new_commit.commit_id

        # Log a warning if the commit is not found
        logging.warning(f"Commit {commit_id_str} not found.")
    
    def undo(self):
        if self.head_index > 0:
            self.redo_stack.append(self.commits[self.head_index])
            self.head_index -= 1
            logging.info(f"HEAD is now at {self.head.commit_id}")
        else:
            logging.info("no commits to undo")

    def redo(self):
        if self.redo_stack:
            redo_commit = self.redo_stack.pop()
            self.commits.append(redo_commit)
            self.head_index += 1
            logging.info(f"HEAD is now {redo_commit.commit_id}")
        else:
            logging.info("no commits to redo")

if __name__ == "__main__":
    pass
