from sv.utils import is_online

import unittest

class UtilsTest(unittest.TestCase):

    def test_is_online(self):
        print (is_online())
            
if __name__ == "__main__":
    unittest.main()

