# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambusaving

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuSavingTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getsavingssurl

        self.assertEqual(mambusaving.mod_urlfunc, getsavingssurl)
    def test_class(self):
        a = mambusaving.MambuSaving(urlfunc=None)
        self.assertTrue(mambusaving.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambusaving.MambuSaving(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")

    def test_setUser(self):

        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345"}

        class my_user(object):
            def __init__(self, id):
                self.attrs = {"id": id}

            def __getitem__(self, item):
                return self.attrs[item]

        # no user assigned to account
        with mock.patch.object(
            mambusaving.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambuuser.MambuUser") as mock_mambuuser:
            my_user_instance = my_user(id="dummyCentreId")
            mock_mambuuser.return_value = my_user_instance

            l = mambusaving.MambuSaving(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("assignedUser"))
            with self.assertRaisesRegexp(
                mambusaving.MambuError, r"La cuenta 12345 no tiene asignado un usuario"
            ):
                l.setUser()
            self.assertFalse(l.has_key("user"))

class MambuSavingsTests(unittest.TestCase):
    def test_class(self):
        acs = mambusaving.MambuSavings(urlfunc=None)
        self.assertTrue(mambusaving.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambusaving.MambuSavings(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getsavingssurl

        acs = mambusaving.MambuSavings(urlfunc=None)
        acs.attrs = [
            {"saving": "my_saving"},
            {"saving": "my_2_saving"},
        ]
        with self.assertRaisesRegexp(
            AttributeError,
            "'MambuSavings' object has no attribute 'saving'",
        ):
            acs.saving
        acs.convert_dict_to_attrs()
        self.assertEqual(
            str(acs.itemclass),
            "<class 'MambuPy.rest.mambusaving.MambuSaving'>",
        )
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuSaving")
            self.assertEqual(a._MambuStruct__urlfunc, getsavingssurl)


if __name__ == "__main__":
    unittest.main()
