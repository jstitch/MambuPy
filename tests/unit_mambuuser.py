# coding: utf-8

import json
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
from MambuPy.rest import mambuuser

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text


class MambuUserTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getuserurl

        self.assertEqual(mambuuser.mod_urlfunc, getuserurl)

    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_class(self, mock_requests, mock_json):
        u = mambuuser.MambuUser(urlfunc=None)
        self.assertTrue(mambuuser.MambuStruct in u.__class__.__bases__)

        # calling with non ascii char in entid
        mock_requests.get.return_value = mock.Mock()
        mock_json.loads.return_value = {}
        u = mambuuser.MambuUser(entid="d.muñoz", branchId="añil", limit=500)
        self.assertEqual(u.entid, "d.muñoz")

    def test___init__(self):
        u = mambuuser.MambuUser(urlfunc=None, entid="anything")
        self.assertEqual(u.entid, "anything")

    @mock.patch("MambuPy.rest.mambuuser.MambuStruct.preprocess")
    def test_preprocess(self, mock_super_preprocess):
        from MambuPy.mambugeturl import getuserurl

        def build_mock_user(self, *args, **kwargs):
            self.attrs = {
                "username": args[1],
                "firstName": "my_name ",
                "lastName": " my_last_name ",
            }

        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            u.preprocess()
            self.assertEqual(u.firstName, "my_name")
            self.assertEqual(u.lastName, "my_last_name")
            self.assertEqual(u.name, "my_name my_last_name")

        def build_mock_user_2(self, *args, **kwargs):
            self.attrs = {
                "username": args[1],
            }

        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user_2):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            u.preprocess()
            self.assertEqual(u.firstName, "")
            self.assertEqual(u.lastName, "")
            self.assertEqual(u.name, " ")

    def test_setGroups(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"username": "u.sername"}

        with mock.patch.object(
            mambuuser.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambugroup.MambuGroups") as mock_mambugroups:
            gps = mock.Mock(return_value=[{"id": "abc123"}, {"id": "xyz321"}])
            gps.__iter__ = mock.Mock(
                return_value=iter([{"id": "abc123"}, {"id": "xyz321"}])
            )
            gps.attrs = [{"id": "abc123"}, {"id": "xyz321"}]
            mock_mambugroups.return_value = gps

            u = mambuuser.MambuUser(urlfunc=lambda x: x)
            self.assertFalse(u.has_key("groups"))
            self.assertFalse(u.has_key("mambugroupsclass"))

            # no mambugroupsclass yet
            u.setGroups()
            self.assertTrue(u.has_key("groups"))
            self.assertTrue(u.has_key("mambugroupsclass"))
            mock_mambugroups.assert_called_once_with(creditOfficerUsername="u.sername")
            self.assertEqual(list(u["groups"]), gps.attrs)

            # already with mambugroupsclass
            mock_mambugroups.reset_mock()
            u.setGroups()
            self.assertTrue(u.has_key("groups"))
            self.assertTrue(u.has_key("mambugroupsclass"))
            mock_mambugroups.assert_called_once_with(creditOfficerUsername="u.sername")

    def test_setRoles(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"role": {"encodedKey": "roleEncodedKey"}}

        class my_role(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambuuser.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mamburoles.MambuRole") as mock_mamburole:
            my_role_instance = my_role(id="dummyRoleId", name="myRoleName")
            mock_mamburole.return_value = my_role_instance

            u = mambuuser.MambuUser(urlfunc=lambda x: x)
            self.assertTrue(u["role"].get("encodedKey"))
            self.assertFalse(u["role"].get("role"))
            self.assertFalse(u.has_key("mamburoleclass"))

            # no mamburolesclass yet
            u.setRoles()
            self.assertTrue(u["role"].get("role"))
            self.assertTrue(u.has_key("mamburoleclass"))
            mock_mamburole.assert_called_once_with(entid="roleEncodedKey")
            self.assertEqual(u["role"]["role"], my_role_instance)
            self.assertEqual(u["role"]["role"]["id"], "dummyRoleId")
            self.assertEqual(u["role"]["role"]["name"], "myRoleName")

            # already with mamburolesclass
            mock_mamburole.reset_mock()
            u.setRoles()
            self.assertTrue(u["role"].get("role"))
            self.assertTrue(u.has_key("mamburoleclass"))
            mock_mamburole.assert_called_once_with(entid="roleEncodedKey")

    def test_setBranch(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "78945", "assignedBranchKey": "branch123"}

        class my_branch(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambuuser.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambubranch.MambuBranch") as mock_mambubranch:
            my_branch_instance = my_branch(id="dummyBranchId", name="myBranchName")
            mock_mambubranch.return_value = my_branch_instance

            usr = mambuuser.MambuUser(urlfunc=lambda x: x)
            self.assertFalse(usr.has_key("branch"))
            self.assertFalse(usr.has_key("mambubranchclass"))

            # no mambubranchclass yet
            usr.setBranch()
            self.assertTrue(usr.has_key("branch"))
            self.assertTrue(usr.has_key("mambubranchclass"))
            mock_mambubranch.assert_called_once_with(entid="branch123")

            # already with mambubranchclass
            mock_mambubranch.reset_mock()
            usr.setBranch()
            mock_mambubranch.assert_called_once_with(entid="branch123")

    @mock.patch("MambuPy.rest.mambuuser.MambuStruct.create")
    def test_create(self, mock_super_create):
        """Test create"""
        attrs = {
            "user": {"user": "moreData"},
            "customInformation": [
                {
                    "linkedEntityKeyValue": "userLink",
                    "customFieldSetGroupIndex": 0,
                    "customId": "id",
                    "customValue": "value",
                    "customField": {
                        "state": "ACTIVE",
                        "name": "customFieldX",
                        "id": "customFieldID",
                    },
                }
            ],
        }
        u = mambuuser.MambuUser(connect=False)
        u.attrs = attrs

        data = {"dataDummy": "dataDummy"}
        # before init() method is called inside create() the attribute
        # u[u.custom_field_name] not exists
        with self.assertRaisesRegexp(KeyError, r"^'%s'" % (u.custom_field_name)):
            self.assertTrue(u[u.custom_field_name])
        self.assertEqual(u.create(data), 1)
        mock_super_create.assert_called_with(data)
        # after init() method is called inside create() the attribute
        # u[u.custom_field_name] is created
        self.assertTrue(u[u.custom_field_name])

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update(self, mock_requests):
        """Test update"""

        # set data response
        mock_requests.patch.return_value = Response(
            '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        mock_requests.post.return_value = Response(
            '{"encodedKey":"8a68ae574f707810014f84add84610ef","id":631,"creationDate":"2015-08-31T16:53:50+0000","lastModifiedDate":"2021-05-14T13:28:35+0000","lastLoggedInDate":"2021-04-23T13:31:39+0000"}'
        )
        mambuuser.MambuStruct.update = mock.Mock()
        mambuuser.MambuStruct.update.return_value = 1
        user = mambuuser.MambuUser(connect=False)
        user.attrs = {}
        userData = {}

        # send none data
        self.assertEqual(user.update(userData), 1)
        userData["user"] = {"assignedBranchKey": "123456"}
        userData["customInformation"] = [
            {
                "customFieldID": "UnidadesCoordinador",
                "value": "TribuNR-2",
                "customFieldSetGroupIndex": "0",
            }
        ]
        self.assertEqual(user.update(userData), 2)

        mambuuser.MambuStruct.update.assert_called()

    def test_update_patch(self):
        mambuuser.MambuStruct.update_patch = mock.Mock()
        mambuuser.MambuStruct.update_patch.return_value = 1
        data = {
            "customInformation": [
                {"customFieldID": "UnidadesCoordinador", "value": "PRUEBA"}
            ]
        }
        user = mambuuser.MambuUser(connect=False)

        self.assertEqual(user.update_patch(data), 1)
        mambuuser.MambuStruct.update_patch.assert_called()


class MambuUsersTests(unittest.TestCase):
    def test_class(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        self.assertTrue(mambuuser.MambuStruct in us.__class__.__bases__)

    def test_iterator(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        us.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(us), 3)
        for n, a in enumerate(us):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getuserurl

        us = mambuuser.MambuUsers(urlfunc=None)
        us.attrs = [
            {"username": "a_user"},
            {"username": "other_user"},
        ]
        with self.assertRaisesRegexp(
            AttributeError, "'MambuUsers' object has no attribute 'mambuuserclass'"
        ):
            us.mambuuserclass
        us.convert_dict_to_attrs()
        self.assertEqual(
            str(us.mambuuserclass), "<class 'MambuPy.rest.mambuuser.MambuUser'>"
        )
        for u in us:
            self.assertEqual(u.__class__.__name__, "MambuUser")
            self.assertEqual(u._MambuStruct__urlfunc, getuserurl)


if __name__ == "__main__":
    unittest.main()
