from sv.client.git import Git, CommitId
from sv.client.model import Project

from unittest.mock import patch, mock_open

import itertools
import json
import os
import shutil
import unittest

class GitTest(unittest.TestCase):

    def setUp(self):
        self.git = Git()
        self.sample_content = Project()

    def unique_slug_generator():
        for i in itertools.count(1):
            yield f"slug-{i}"
        
    """
    def test_git_initialization(self, mock_exists, mock_makedirs):
        git = Git()
        self.assertEqual(git.commits, [])
        self.assertTrue(git.is_empty())
    """

    """
    @patch("sv.client.git.random_name", return_value="random-slug")
    # @patch("sv.client.model.Project.as_dict", return_value={})
    @patch("builtins.open", new_callable=mock_open)
    def test_commit(self, mock_open, mock_as_dict, mock_random_name):
        commit_id = self.git.commit(content=self.sample_content)
        self.assertEqual(len(self.git.commits), 1)
        self.assertEqual(self.git.head.commit_id, commit_id)
        self.assertIn("random-slug", str(commit_id))
    """
 
    @patch("sv.client.git.random_name", side_effect=unique_slug_generator())
    @patch("sv.client.model.Project.clone", return_value=Project())
    def test_checkout(self, mock_clone, mock_random_name):
        first_commit_id = self.git.commit(content=self.sample_content)
        second_commit_id = self.git.commit(content=self.sample_content)
        with self.assertLogs(level="INFO") as log:
            new_commit_id = self.git.checkout(str(first_commit_id))
            self.assertIsNotNone(new_commit_id)
            self.assertEqual(len(self.git.commits), 3)
            self.assertEqual(self.git.head.commit_id, new_commit_id)
            self.assertIn("Checked out to new commit at HEAD", log.output[0])
        with self.assertLogs(level="WARNING") as log:
            self.git.checkout("non-existent-id")
            self.assertIn("Commit non-existent-id not found", log.output[0])
        
    def test_undo(self):
        self.git.commit(content=self.sample_content)
        self.git.commit(content=self.sample_content)
        self.git.undo()
        self.assertEqual(self.git.head_index, 0)
        self.assertEqual(len(self.git.redo_stack), 1)

    def test_redo(self):
        self.git.commit(content=self.sample_content)
        self.git.commit(content=self.sample_content)
        self.git.undo()
        self.git.redo()
        self.assertEqual(self.git.head_index, 1)
        self.assertEqual(len(self.git.redo_stack), 0)

    def test_undo_with_no_commits(self):
        self.git.undo()
        self.assertTrue(self.git.is_empty())
        self.assertEqual(len(self.git.redo_stack), 0)

    def test_redo_with_no_redo_stack(self):
        self.git.commit(content=self.sample_content)
        self.git.redo()
        self.assertEqual(self.git.head_index, 0)

if __name__ == "__main__":
    unittest.main()
