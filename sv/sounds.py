from enum import Enum
from urllib.parse import parse_qs

DefaultCutoff = 16000

class SVSample(dict):

    class FX(Enum):
        REV = "rev"
        RET2 = "ret2"
        RET4 = "ret4"
        RET8 = "ret8"
        RET16 = "ret16"

    @staticmethod
    def parse(sample_str):
        if not sample_str:
            raise RuntimeError("Input string cannot be empty")

        # Split tags first
        tag_split = sample_str.split("#")
        sample_and_qs = tag_split[0]
        tags = tag_split[1:] if len(tag_split) > 1 else []

        # Parse bank_name, file_path, and query string
        path_and_query = sample_and_qs.split("?")
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

        fx_value = query_dict.get("fx", [None])[0]
        fx = SVSample.FX(fx_value) if fx_value in SVSample.FX._value2member_map_ else None

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
            fx=fx,
            start=start,
            cutoff=cutoff,
            tags=tags,
        )

    def __init__(self, bank_name, file_path, note=0, fx=None, start=0, cutoff=DefaultCutoff, tags=None):
        dict.__init__(self)
        self["bank_name"] = bank_name
        self["file_path"] = file_path
        self["note"] = note
        self["fx"] = fx
        self["start"] = start
        self["cutoff"] = cutoff
        self["tags"] = tags or []

    def clone(self):
        return SVSample(
            bank_name=self.bank_name,
            file_path=self.file_path,
            note=self.note,
            fx=self.fx,
            start=self.start,
            cutoff=self.cutoff,
            tags=list(self.tags),
        )

    @property
    def bank_name(self):
        return self["bank_name"]

    @property
    def file_path(self):
        return self["file_path"]

    @property
    def note(self):
        return self["note"]

    @note.setter
    def note(self, value):
        self["note"] = value

    @property
    def fx(self):
        return self["fx"]

    @fx.setter
    def fx(self, value):
        if value is not None and not isinstance(value, SVSample.FX):
            raise ValueError(f"fx must be an instance of SVSample.FX or None, got {value}")
        self["fx"] = value

    @property
    def start(self):
        return self["start"]

    @start.setter
    def start(self, value):
        if value > self.cutoff:
            raise ValueError("start cannot be greater than cutoff")
        self["start"] = value

    @property
    def cutoff(self):
        return self["cutoff"]

    @cutoff.setter
    def cutoff(self, value):
        if value is not None and self.start > value:
            raise ValueError("cutoff cannot be less than start")
        self["cutoff"] = value

    @property
    def querystring(self):
        qs = {}
        if self["note"] != 0:
            qs["note"] = self["note"]
        if self["fx"] is not None:
            qs["fx"] = self["fx"].value
        if self["start"] != 0:
            qs["start"] = self["start"]
        if self["cutoff"] != DefaultCutoff:
            qs["cutoff"] = self["cutoff"]
        return qs

    @property
    def tags(self):
        return self["tags"]

    def __str__(self):
        query_parts = [
            f"{key}={value}" for key, value in self.querystring.items()
        ]
        query_string = "?" + "&".join(query_parts) if query_parts else ""
        tag_string = "".join([f"#{tag}" for tag in sorted(self.tags)])
        return f"{self.bank_name}/{self.file_path}{query_string}{tag_string}"

    def __getstate__(self):
        """Filter out default values when serializing."""
        state = {
            key: value
            for key, value in self.items()
            if not (
                (key == "note" and value == 0) or
                (key == "fx" and value is None) or
                (key == "start" and value == 0) or
                (key == "cutoff" and value == DefaultCutoff)
            )
        }
        return state

    def __setstate__(self, state):
        """Ensure defaults are set when deserializing."""
        self.__init__(
            bank_name=state.get("bank_name"),
            file_path=state.get("file_path"),
            note=state.get("note", 0),
            fx=state.get("fx"),
            start=state.get("start", 0),
            cutoff=state.get("cutoff", DefaultCutoff),
            tags=state.get("tags", []),
        )


if __name__ == "__main__":
    pass
