from sv.utils.naming import random_name

import unittest

class NamingUtilsTest(unittest.TestCase):

    def test_random_name(self):
        print (random_name())
            
if __name__ == "__main__":
    unittest.main()

