from rv.readers.reader import read_sunvox_file
from sv.utils.export import export_wav

import io
import os
import unittest

class ExportUtilsTest(unittest.TestCase):

    def test_export(self):
        project = None
        with open("tests/utils/sample-project.sunvox", 'rb') as f:
            project = read_sunvox_file(f)
        if not project:
            raise RuntimeError("project not loaded")
        buf = export_wav(project)
        self.assertTrue(isinstance(buf, io.BytesIO))
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/sample-project.wav", 'wb') as f:
            f.write(buf.getvalue())
            
if __name__ == "__main__":
    unittest.main()
