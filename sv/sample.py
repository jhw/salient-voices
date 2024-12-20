from enum import Enum
from urllib.parse import parse_qs

class SVSample:

    @staticmethod
    def parse(sample_str):
        if not sample_str:
            raise RuntimeError("Input string cannot be empty")

        # Extract bank_name and file_path
        tokens = sample_str.split("/", 1)
        if len(tokens) < 2 or not tokens[0]:
            raise RuntimeError("Bank name cannot be empty")
        bank_name = tokens[0]
        file_path = tokens[1] if len(tokens) > 1 else ""

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

    def as_dict(self):
        return  {
            "bank_name": self.bank_name,
            "file_path": self.file_path
        }

    def __str__(self):
        return f"{self.bank_name}/{self.file_path}"

if __name__ == "__main__":
    pass
