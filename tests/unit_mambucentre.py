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
from MambuPy.rest import mambucentre

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRegex instead

class MambuCentreTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getcentresurl
        self.assertEqual(mambucentre.mod_urlfunc, getcentresurl)

    def test_class(self):
        cn = mambucentre.MambuCentre(urlfunc=None)
        self.assertTrue(mambucentre.MambuStruct in cn.__class__.__bases__)

    def test___init__(self):
        cn = mambucentre.MambuCentre(urlfunc=None, entid="anything")
        self.assertEqual(cn.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from MambuPy.mambuutil import getcentresurl
        def build_mock_cen_1(self, *args, **kwargs):
            self.attrs = {
                'id' : args[1]
                }

        with mock.patch.object(mambucentre.MambuStruct, "__init__", build_mock_cen_1):
            cn = mambucentre.MambuCentre(urlfunc=getcentresurl, entid="mockcentre")
            self.assertRegexpMatches(repr(cn), r"^MambuCentre - id: mockcentre")


class MambuCentresTests(unittest.TestCase):
    def test_class(self):
        cens = mambucentre.MambuCentres(urlfunc=None)
        self.assertTrue(mambucentre.MambuStruct in cens.__class__.__bases__)

    def test_iterator(self):
        cens = mambucentre.MambuCentres(urlfunc=None)
        cens.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(cens), 3)
        for n,c in enumerate(cens):
            self.assertEqual(str(n), [k for k in c][0])
            self.assertEqual(n, c[str(n)])

    def test_convertDict2Attrs(self):
        cens = mambucentre.MambuCentres(urlfunc=None)
        cens.attrs = [
            {'id':"1", 'name':"my_centre"},
            {'id':"2", 'name':"my_2_centre"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuCentres' object has no attribute 'mambucentreclass'"):
            cens.mambucentreclass
        cens.convertDict2Attrs()
        self.assertEqual(str(cens.mambucentreclass), "<class 'MambuPy.rest.mambucentre.MambuCentre'>")
        for c in cens:
            self.assertEqual(c.__class__.__name__, 'MambuCentre')


if __name__ == '__main__':
    unittest.main()
