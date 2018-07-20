# coding: utf-8

import mock
import unittest

import mamburoles

class MambuRoleTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from mambuutil import getrolesurl
        self.assertEqual(mamburoles.mod_urlfunc, getrolesurl)

    def test_class(self):
        r = mamburoles.MambuRole(urlfunc=None)
        self.assertTrue(mamburoles.MambuStruct in r.__class__.__bases__)

    def test___init__(self):
        r = mamburoles.MambuRole(urlfunc=None, entid="anything")
        self.assertEqual(r.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from mambuutil import getrolesurl
        def build_mock_role_1(self, *args, **kwargs):
            self.attrs = {
                'name' : args[1]
                }

        with mock.patch.object(mamburoles.MambuStruct, "__init__", build_mock_role_1):
            r = mamburoles.MambuRole(urlfunc=getrolesurl, entid="mockrole")
            self.assertRegexpMatches(repr(r), r"^MambuRole - rolename: 'mockrole'")


class MambuRolesTests(unittest.TestCase):
    def test_class(self):
        rs = mamburoles.MambuRoles(urlfunc=None)
        self.assertTrue(mamburoles.MambuStruct in rs.__class__.__bases__)

    def test_iterator(self):
        rs = mamburoles.MambuRoles(urlfunc=None)
        rs.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(rs), 3)
        for n,a in enumerate(rs):
            self.assertEqual(str(n), a.keys()[0])
            self.assertEqual(n, a[str(n)])

    def test_convertDict2Attrs(self):
        rs = mamburoles.MambuRoles(urlfunc=None)
        rs.attrs = [
            {'name':"my_role", 'permissions':{}},
            {'name':"my_2_role", 'permissions':{}},
            ]
        rs.convertDict2Attrs()
        for r in rs:
            self.assertEqual(r.__class__.__name__, 'MambuRole')


if __name__ == '__main__':
    unittest.main()
