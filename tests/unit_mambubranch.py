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
from MambuPy.rest import mambubranch

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuBranchTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getbranchesurl

        self.assertEqual(mambubranch.mod_urlfunc, getbranchesurl)

    def test_class(self):
        a = mambubranch.MambuBranch(urlfunc=None)
        self.assertTrue(mambubranch.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambubranch.MambuBranch(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")

    def test___repr__(self):
        from MambuPy.mambugeturl import getbranchesurl

        def build_mock_brn_1(self, *args, **kwargs):
            self.attrs = {"id": args[1]}

        with mock.patch.object(mambubranch.MambuStruct, "__init__", build_mock_brn_1):
            b = mambubranch.MambuBranch(urlfunc=getbranchesurl, entid="mockbranch")
            self.assertRegexpMatches(repr(b), r"^MambuBranch - id: mockbranch")

    def test_setUsers(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "myBranch_12345"}

        class my_users(object):
            def __init__(self, ids, usernames, userstates):
                self.attrs = [
                    {"id": id, "username": username, "userState": userstate}
                    for id, username, userstate in zip(ids, usernames, userstates)
                ]

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambubranch.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambuuser.MambuUsers") as mock_mambuusers:
            my_users_instances = my_users(
                ids=["dummyUserId1", "dummyUserId2", "dummyUserId3"],
                usernames=["myUserName1", "myUserName2", "myUserName3"],
                userstates=["ACTIVE", "INACTIVE", "ACTIVE"],
            )
            mock_mambuusers.return_value = my_users_instances

            # no mambuuserclass yet
            b = mambubranch.MambuBranch(urlfunc=lambda x: x)
            self.assertFalse(b.has_key("users"))
            b.setUsers()
            self.assertTrue(b.has_key("users"))
            mock_mambuusers.assert_called_once_with(branchId="myBranch_12345")
            self.assertEqual(
                b["users"], [my_users_instances.attrs[0], my_users_instances.attrs[2]]
            )

            # already with mambuuserclass
            mock_mambuusers.reset_mock()
            b.setUsers()
            self.assertTrue(b.has_key("users"))
            mock_mambuusers.assert_called_once_with(branchId="myBranch_12345")


class MambuBranchesTests(unittest.TestCase):
    def test_class(self):
        acs = mambubranch.MambuBranches(urlfunc=None)
        self.assertTrue(mambubranch.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        brs = mambubranch.MambuBranches(urlfunc=None)
        brs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(brs), 3)
        for n, b in enumerate(brs):
            self.assertEqual(str(n), [k for k in b][0])
            self.assertEqual(n, b[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getbranchesurl

        brs = mambubranch.MambuBranches(urlfunc=None)
        brs.attrs = [
            {"id": "1", "name": "my_branch"},
            {"id": "2", "name": "my_2_branch"},
        ]
        with self.assertRaisesRegex(
            AttributeError, "'MambuBranches' object has no attribute 'mambubranchclass'"
        ):
            brs.mambubranchclass
        brs.convert_dict_to_attrs()
        self.assertEqual(
            str(brs.mambubranchclass), "<class 'MambuPy.rest.mambubranch.MambuBranch'>"
        )
        for b in brs:
            self.assertEqual(b.__class__.__name__, "MambuBranch")
            self.assertEqual(b._MambuStruct__urlfunc, getbranchesurl)


if __name__ == "__main__":
    unittest.main()
