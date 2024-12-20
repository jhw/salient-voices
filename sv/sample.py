from enum import Enum
from urllib.parse import parse_qs

class SVSample:

    @staticmethod
    def parse(sample_str):
        if not sample_str:
            raise RuntimeError("Input string cannot be empty")

        file_path = sample_str

        return SVSample(
            file_path=file_path
        )

    def __init__(self, file_path):
        self.file_path = file_path

    def clone(self):
        return SVSample(
            file_path=self.file_path
        )

    def as_dict(self):
        return  {
            "file_path": self.file_path
        }

    def __str__(self):
        return f"{self.file_path}"

if __name__ == "__main__":
    pass
