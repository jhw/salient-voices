from sv.utils.cli.parse import parse_line

import unittest

class CLIParseUtilsTest(unittest.TestCase):

    def test_string(self):
        class CLI:
            @parse_line([{"name": "foo",
                          "type": "str"}])
            def task(self, foo):
                return foo
        cli = CLI()
        self.assertEqual(cli.task("bar"), "bar")

    def test_int(self):
        class CLI:
            @parse_line([{"name": "foo",
                          "type": "int"}])
            def task(self, foo):
                return foo
        cli = CLI()
        self.assertEqual(cli.task("1"), 1)

    def test_enum(self):
        class CLI:
            @parse_line([{"name": "foo",
                          "type": "enum",
                          "options": ["bar"]}])
            def task(self, foo):
                return foo
        cli = CLI()
        self.assertEqual(cli.task("bar"), "bar")
            
if __name__ == "__main__":
    unittest.main()
