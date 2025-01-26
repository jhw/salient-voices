from sv.client.git import Git, CommitId, Commit
from sv.client.naming import random_name

from datetime import datetime
from unittest.mock import MagicMock

import unittest

class TestGitFunctionality(unittest.TestCase):

    def setUp(self):
        self.git = Git()
        self.mock_random_name = MagicMock(return_value="test-slug")

    def test_commit_creates_new_commit(self):
        commit_id = self.git.commit("Initial content", name_fn=self.mock_random_name)
        
        self.assertEqual(len(self.git.commits), 1)
        self.assertEqual(commit_id.slug, "test-slug")
        self.assertTrue(commit_id.timestamp)

    def test_head_points_to_latest_commit(self):
        self.git.commit("First commit", name_fn=self.mock_random_name)
        self.git.commit("Second commit", name_fn=self.mock_random_name)

        self.assertEqual(self.git.head.content, "Second commit")

    def test_undo_moves_head_to_previous_commit(self):
        self.git.commit("First commit", name_fn=self.mock_random_name)
        self.git.commit("Second commit", name_fn=self.mock_random_name)

        self.git.undo()

        self.assertEqual(self.git.head.content, "First commit")
        self.assertEqual(len(self.git.redo_stack), 1)

    def test_redo_restores_head_to_redo_stack_commit(self):
        self.git.commit("First commit", name_fn=self.mock_random_name)
        self.git.commit("Second commit", name_fn=self.mock_random_name)

        self.git.undo()
        self.git.redo()

        self.assertEqual(self.git.head.content, "Second commit")
        self.assertEqual(len(self.git.redo_stack), 0)

    def test_checkout_creates_new_commit_with_cloned_content(self):
        class MockContent:
            def __init__(self, data):
                self.data = data

            def clone(self):
                return MockContent(self.data)

        first_content = MockContent("First content")
        first_commit_id = self.git.commit(first_content, name_fn=self.mock_random_name)
        second_content = MockContent("Second content")
        self.git.commit(second_content, name_fn=self.mock_random_name)

        cloned_commit_id = self.git.checkout(str(first_commit_id), name_fn=self.mock_random_name)

        self.assertEqual(len(self.git.commits), 3)
        # self.assertNotEqual(str(cloned_commit_id), str(first_commit_id))
        self.assertEqual(self.git.head.content.data, "First content")

    def test_is_empty_returns_true_for_new_git(self):
        self.assertTrue(self.git.is_empty())

    def test_is_empty_returns_false_after_commit(self):
        self.git.commit("First commit", name_fn=self.mock_random_name)
        self.assertFalse(self.git.is_empty())

    def test_commit_id_randomise(self):
        commit_id = CommitId.randomise(self.mock_random_name)
        
        self.assertEqual(commit_id.slug, "test-slug")
        self.assertTrue(commit_id.timestamp)

    def test_commit_id_from_filename(self):
        filename = "2024-01-01-12-00-00-test-slug.json"
        commit_id = CommitId.from_filename(filename)

        self.assertEqual(commit_id.slug, "test-slug")
        self.assertEqual(commit_id.timestamp, "2024-01-01-12-00-00")

    def test_short_name_formatting(self):
        commit_id = CommitId(slug="test-slug", timestamp="2024-01-01-12-00-00")
        self.assertEqual(commit_id.short_name, "tst-slg")

if __name__ == "__main__":
    unittest.main()
