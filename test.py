import os
import sys
import unittest

Filters = {"core": lambda x: "machines" not in x,
           "machines": lambda x: "machines" in x,
           "all": lambda x: True}

def find_and_run_tests(root_dirs, filter_fn):
    suite = unittest.TestSuite()
    print ()
    for root_dir in root_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if (file.endswith('.py') and
                    filter_fn(f"{root}/{file}")):
                    full_path = os.path.join(root, file)
                    module_name = full_path.replace(os.sep, '.')[:-3] 
                    module = __import__(module_name, fromlist=[''])
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (isinstance(obj, type) and
                            issubclass(obj, unittest.TestCase)):
                            print (str(obj)[1:-1].split(" ")[-1][1:-1])
                            suite.addTest(unittest.TestLoader().loadTestsFromTestCase(obj))
    print ()
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise RuntimeError(f"please enter {'|'.join(list(Filters.keys()))}")
        suite_type = sys.argv[1]
        if suite_type not in Filters:
            raise RuntimeError(f"{suite_type} is not a valid option")
        filter_fn = Filters[suite_type]
        find_and_run_tests(["tests"], filter_fn)
    except RuntimeError as error:
        print(f"ERROR: {error}")
