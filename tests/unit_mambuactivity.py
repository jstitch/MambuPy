# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock
import unittest

from MambuPy import mambuconfig
for k,v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambuactivity

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRegex instead

class MambuActivityTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getactivitiesurl
        self.assertEqual(mambuactivity.mod_urlfunc, getactivitiesurl)

    def test_class(self):
        a = mambuactivity.MambuActivity(urlfunc=None)
        self.assertTrue(mambuactivity.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambuactivity.MambuActivity(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from MambuPy.mambuutil import getactivitiesurl
        def build_mock_act_1(self, *args, **kwargs):
            self.attrs = {
                'activity' : args[1]
                }

        with mock.patch.object(mambuactivity.MambuStruct, "__init__", build_mock_act_1):
            a = mambuactivity.MambuActivity(urlfunc=getactivitiesurl, entid="mockactivity")
            self.assertRegexpMatches(repr(a), r"^MambuActivity - activityid: mockactivity")


class MambuActivitiesTests(unittest.TestCase):
    def test_class(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        self.assertTrue(mambuactivity.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        acs.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(acs), 3)
        for n,a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convertDict2Attrs(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        acs.attrs = [
            {'activity':"my_act"},
            {'activity':"my_2_act"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuActivities' object has no attribute 'mambuactivityclass'"):
            acs.mambuactivityclass
        acs.convertDict2Attrs()
        self.assertEqual(str(acs.mambuactivityclass), "<class 'MambuPy.rest.mambuactivity.MambuActivity'>")
        for a in acs:
            self.assertEqual(a.__class__.__name__, 'MambuActivity')


if __name__ == '__main__':
    unittest.main()
