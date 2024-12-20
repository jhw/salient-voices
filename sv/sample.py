from enum import Enum
from urllib.parse import parse_qs

DefaultCutoff = 16000

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
        try:
            note = int(query_dict.get("note", [0])[0])  # Default note to 0 if not provided
        except ValueError:
            note = 0

        start = int(query_dict.get("start", [0])[0]) if "start" in query_dict else 0
        cutoff = (
            int(query_dict.get("cutoff", [DefaultCutoff])[0])
            if "cutoff" in query_dict and query_dict["cutoff"][0].isdigit()
            else DefaultCutoff
        )

        # Validation at initialization
        if start > cutoff:
            raise ValueError("start cannot be greater than cutoff")

        return SVSample(
            bank_name=bank_name,
            file_path=file_path,
            note=note,
            start=start,
            cutoff=cutoff
        )

    def __init__(self, bank_name, file_path, note=0, start=0, cutoff=DefaultCutoff):
        self.bank_name = bank_name
        self.file_path = file_path
        self.note = note
        self.start = start
        self.cutoff = cutoff

    def clone(self):
        return SVSample(
            bank_name=self.bank_name,
            file_path=self.file_path,
            note=self.note,
            start=self.start,
            cutoff=self.cutoff
        )

    @property
    def querystring(self):
        qs = {}
        if self.note != 0:
            qs["note"] = self.note
        if self.start != 0:
            qs["start"] = self.start
        if self.cutoff != DefaultCutoff:
            qs["cutoff"] = self.cutoff
        return qs

    def as_dict(self):
        state = {
            "bank_name": self.bank_name,
            "file_path": self.file_path,
            "note": self.note if self.note != 0 else None,
            "start": self.start if self.start != 0 else None,
            "cutoff": self.cutoff if self.cutoff != DefaultCutoff else None
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
