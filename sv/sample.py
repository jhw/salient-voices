from enum import Enum
from urllib.parse import parse_qs

class SVSample:

    @staticmethod
    def parse(sample_str):
        if not sample_str:
            raise RuntimeError("Input string cannot be empty")

        # Parse bank_name, file_path, and query string
        path_and_query = sample_str.split("?")
        path = path_and_query[0]
        query_string = path_and_query[1] if len(path_and_query) > 1 else ""

        # Extract bank_name and file_path
        tokens = path.split("/", 1)
        if len(tokens) < 2 or not tokens[0]:
            raise RuntimeError("Bank name cannot be empty")
        bank_name = tokens[0]
        file_path = tokens[1] if len(tokens) > 1 else ""

        # Parse query string into a dictionary
        query_dict = parse_qs(query_string)

        return SVSample(
            bank_name=bank_name,
            file_path=file_path
        )

    def __init__(self, bank_name, file_path):
        self.bank_name = bank_name
        self.file_path = file_path

    def clone(self):
        return SVSample(
            bank_name=self.bank_name,
            file_path=self.file_path
        )

    @property
    def querystring(self):
        qs = {}
        return qs

    def as_dict(self):
        state = {
            "bank_name": self.bank_name,
            "file_path": self.file_path
        }
        return {k: v for k, v in state.items() if v is not None}

    def __str__(self):
        query_parts = [
            f"{key}={value}" for key, value in self.querystring.items()
        ]
        query_string = "?" + "&".join(query_parts) if query_parts else ""
        return f"{self.bank_name}/{self.file_path}{query_string}"

if __name__ == "__main__":
    pass
