from rv.readers.reader import read_sunvox_file
from sv.utils.export import export_wav

import io
import unittest

class ExportTest(unittest.TestCase):

    def test_export(self):
        try:
            project = None
            with open("tests/utils/sample-project.sunvox", 'rb') as f:
                project = read_sunvox_file(f)
            if not project:
                raise RuntimeError("project not loaded")
            buf = export_wav(project)
            self.assertTrue(isinstance(buf, io.BytesIO))
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()
