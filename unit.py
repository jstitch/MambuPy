import mock
import unittest

import mambustruct

class MambuStructTests(unittest.TestCase):
    def setUp(self):
        s = mambustruct.MambuStruct(entid='1234', urlfunc=lambda x:x, connect=False)
        s.rc.reset()
        self.func = lambda x:'http://example.com'+x

    def test_init_(self):
        # Normal init
        s = mambustruct.MambuStruct(entid='1234', urlfunc=self.func, connect=False)
        self.assertEqual(s.entid, '1234')
        self.assertEqual(s.rc.cnt, 0)
        
        # Test that urlfunc=None sets no attributes
        s = mambustruct.MambuStruct(entid='1234', urlfunc=None)
        self.assertDictEqual(s.__dict__, {})

    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.urlopen')
    def test_connect(self, urlopen, json):
        json.load.side_effect = [{},
                                 {'returnCode'  :'TestErrorCode',
                                  'returnStatus':'Test Error Status',},
                                 {}]
        
        s = mambustruct.MambuStruct(entid='1234', urlfunc=self.func, connect=False)
        s.connect()

        # urlopen is called to open the URL given by func
        urlopen.assert_called_with(self.func('1234'))
        self.assertEqual(s.rc.cnt, 1)

        # simulate Mambu returns an error
        with self.assertRaisesRegexp(mambustruct.MambuError, "^Test Error Status$") as ex:
            s.connect()
        self.assertEqual(s.rc.cnt, 2)

        s = mambustruct.MambuStruct(entid='1234', urlfunc=self.func)
        self.assertEqual(s.rc.cnt, 3)

        
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.urlopen')
    def test_init(self, urlopen, json):
        json.load.side_effect = [{'attr1': 1,
                                  'attr2': 3.141592,
                                  'attr3': "string",
                                 }]

        s = mambustruct.MambuStruct(entid='1234', urlfunc=self.func)
        self.assertEqual(s.attrs['attr1'], 1)
        self.assertEqual(s.attrs['attr2'], 3.141592)
        self.assertEqual(s.attrs['attr3'], "string")

        # Dict-like behaviour
        self.assertEqual(s['attr1'],1)
        s['attr3'] = "hello world!"
        self.assertEqual(s.attrs['attr3'], "hello world!")
        self.assertTrue(s.has_key('attr2'))
        self.assertListEqual(sorted(s.items()), [('attr1',1),
                                                 ('attr2',3.141592),
                                                 ('attr3',"hello world!")])


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
