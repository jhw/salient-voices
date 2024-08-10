from sv.utils.naming import random_name

import unittest

class NamingTest(unittest.TestCase):

    def test_random_name(self):
        try:
            print (random_name())
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()

