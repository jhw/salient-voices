from rv.readers.reader import read_sunvox_file
from sv.client.export import export_wav

import io
import unittest

class ExportWavTest(unittest.TestCase):

    def test_export(self):
        project = None
        with open("tests/client/sample-project.sunvox", 'rb') as f:
            project = read_sunvox_file(f)
        if not project:
            raise RuntimeError("project not loaded")
        buf = export_wav(project)
        self.assertTrue(isinstance(buf, io.BytesIO))
            
if __name__ == "__main__":
    unittest.main()
