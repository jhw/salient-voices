from sv.utils.urlparse import parse_value, parse_querystring, format_querystring, parse_url

import unittest

class UrlParseTest(unittest.TestCase):

    def test_parse_value(self):
        self.assertEqual(parse_value("42"), 42)  # Integer parsing
        self.assertEqual(parse_value("-42"), -42)  # Negative integer
        self.assertEqual(parse_value("3.14"), 3.14)  # Float parsing
        self.assertEqual(parse_value("-3.14"), -3.14)  # Negative float
        self.assertEqual(parse_value("hello"), "hello")  # Non-numeric string

    def test_parse_querystring(self):
        qs = "a=42&b=3.14&c=hello&d=-10"
        expected = {
            "a": 42,
            "b": 3.14,
            "c": "hello",
            "d": -10
        }
        self.assertEqual(parse_querystring(qs), expected)

    def test_format_querystring(self):
        params = {
            "b": 3.14,
            "c": "hello",
            "a": 42
        }
        expected = "a=42&b=3.14&c=hello"  # Sorted keys: a, b, c
        self.assertEqual(format_querystring(params), expected)

    def test_parse_url_with_querystring(self):
        url = "https://example.com/path?a=42&b=3.14&c=hello"
        expected_path = "https://example.com/path"
        expected_params = {
            "a": 42,
            "b": 3.14,
            "c": "hello"
        }
        path, params = parse_url(url)
        self.assertEqual(path, expected_path)
        self.assertEqual(params, expected_params)

    def test_parse_url_without_querystring(self):
        url = "https://example.com/path"
        expected_path = "https://example.com/path"
        expected_params = {}
        path, params = parse_url(url)
        self.assertEqual(path, expected_path)
        self.assertEqual(params, expected_params)

if __name__ == "__main__":
    unittest.main()
