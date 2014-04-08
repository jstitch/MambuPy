import mock
import unittest

class MambuStructTests(unittest.TestCase):
    def test_init(self):
        from mambustruct import MambuStruct

        s = MambuStruct(entid='1234', urlfunc=lambda x:x, connect=False)
        self.assertEqual(s.entid, '1234')

if __name__ == '__main__':
    test_classes_to_run = [
                           MambuStructTests,
                          ]
    tl = unittest.TestLoader()
    suites_list = []
    for test_class in test_classes_to_run:
        print "%s testcases:" % test_class.__name__
        suite = tl.loadTestsFromTestCase(test_class)
        testcases = tl.getTestCaseNames(test_class)
        for t in testcases:
            print " ", t
        print ""
        suites_list.append(suite)
    big_suite = unittest.TestSuite(suites_list)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(big_suite)
