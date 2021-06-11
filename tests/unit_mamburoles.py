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
from MambuPy.rest import mamburoles

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuRoleTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getrolesurl

        self.assertEqual(mamburoles.mod_urlfunc, getrolesurl)

    def test_class(self):
        r = mamburoles.MambuRole(urlfunc=None)
        self.assertTrue(mamburoles.MambuStruct in r.__class__.__bases__)

    def test___init__(self):
        r = mamburoles.MambuRole(urlfunc=None, entid="anything")
        self.assertEqual(r.entid, "anything")

    def test___repr__(self):
        from datetime import date

        from MambuPy.mambuutil import getrolesurl

        def build_mock_role_1(self, *args, **kwargs):
            self.attrs = {"name": args[1]}

        with mock.patch.object(mamburoles.MambuStruct, "__init__", build_mock_role_1):
            r = mamburoles.MambuRole(urlfunc=getrolesurl, entid="mockrole")
            self.assertRegexpMatches(repr(r), r"^MambuRole - rolename: 'mockrole'")


class MambuRolesTests(unittest.TestCase):
    def test_class(self):
        rs = mamburoles.MambuRoles(urlfunc=None)
        self.assertTrue(mamburoles.MambuStruct in rs.__class__.__bases__)

    def test_iterator(self):
        rs = mamburoles.MambuRoles(urlfunc=None)
        rs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(rs), 3)
        for n, r in enumerate(rs):
            self.assertEqual(str(n), [k for k in r][0])
            self.assertEqual(n, r[str(n)])

    def test_convertDict2Attrs(self):
        from MambuPy.mambuutil import getrolesurl

        rs = mamburoles.MambuRoles(urlfunc=None)
        rs.attrs = [
            {"name": "my_role", "permissions": {}},
            {"name": "my_2_role", "permissions": {}},
        ]
        with self.assertRaisesRegexp(
            AttributeError, "'MambuRoles' object has no attribute 'mamburoleclass'"
        ):
            rs.mamburoleclass
        rs.convertDict2Attrs()
        self.assertEqual(
            str(rs.mamburoleclass), "<class 'MambuPy.rest.mamburoles.MambuRole'>"
        )
        for r in rs:
            self.assertEqual(r.__class__.__name__, "MambuRole")
            self.assertEqual(r._MambuStruct__urlfunc, getrolesurl)


if __name__ == "__main__":
    unittest.main()
