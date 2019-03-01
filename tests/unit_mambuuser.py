# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock
import unittest

from MambuPy import mambuconfig
for k,v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambuuser

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRaisesRegex instead

class MambuUserTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getuserurl
        self.assertEqual(mambuuser.mod_urlfunc, getuserurl)

    def test_class(self):
        u = mambuuser.MambuUser(urlfunc=None)
        self.assertTrue(mambuuser.MambuStruct in u.__class__.__bases__)

    def test___init__(self):
        u = mambuuser.MambuUser(urlfunc=None, entid="anything")
        self.assertEqual(u.entid, "anything")

    @mock.patch("MambuPy.rest.mambuuser.MambuStruct.preprocess")
    def test_preprocess(self, mock_super_preprocess):
        from MambuPy.mambuutil import getuserurl
        def build_mock_user(self, *args, **kwargs):
            self.attrs = {
                'username'  : args[1],
                'firstName' : 'my_name ',
                'lastName'  : ' my_last_name ',
                }
        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            u.preprocess()
            self.assertEqual(u.firstName, 'my_name')
            self.assertEqual(u.lastName, 'my_last_name')
            self.assertEqual(u.name, 'my_name my_last_name')

        def build_mock_user_2(self, *args, **kwargs):
            self.attrs = {
                'username'  : args[1],
                }
        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user_2):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            u.preprocess()
            self.assertEqual(u.firstName, '')
            self.assertEqual(u.lastName, '')
            self.assertEqual(u.name, ' ')

    def test_setGroups(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'username':"u.sername"}
        with mock.patch.object(mambuuser.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambugroup.MambuGroups') as mock_mambugroups:
            gps = mock.Mock(return_value=[{'id':"abc123"},{'id':"xyz321"}])
            gps.__iter__ = mock.Mock(return_value=iter([{'id':"abc123"},{'id':"xyz321"}]))
            gps.attrs = [{'id':"abc123"},{'id':"xyz321"}]
            mock_mambugroups.return_value = gps

            u = mambuuser.MambuUser(urlfunc=lambda x:x)
            self.assertFalse(u.has_key('groups'))
            self.assertFalse(u.has_key('mambugroupsclass'))
            u.setGroups()
            self.assertTrue(u.has_key('groups'))
            self.assertTrue(u.has_key('mambugroupsclass'))
            mock_mambugroups.assert_called_once_with(creditOfficerUsername='u.sername')
            self.assertEqual(list(u['groups']), gps.attrs)

    def test_setRoles(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"role": {"encodedKey":"roleEncodedKey"}}
        class my_role(object):
            def __init__(self, id, name):
                self.attrs = {'id':id, 'name':name}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambuuser.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mamburoles.MambuRole') as mock_mamburole:
            my_role_instance = my_role(id="dummyRoleId",name="myRoleName")
            mock_mamburole.return_value = my_role_instance

            u = mambuuser.MambuUser(urlfunc=lambda x:x)
            self.assertTrue(u['role'].get('encodedKey'))
            self.assertFalse(u['role'].get('role'))
            self.assertFalse(u.has_key('mamburoleclass'))
            u.setRoles()
            self.assertTrue(u['role'].get('role'))
            self.assertTrue(u.has_key('mamburoleclass'))
            mock_mamburole.assert_called_once_with(entid='roleEncodedKey')
            self.assertEqual(u['role']['role'], my_role_instance)
            self.assertEqual(u['role']['role']['id'], "dummyRoleId")
            self.assertEqual(u['role']['role']['name'], "myRoleName")


    @mock.patch("MambuPy.rest.mambuuser.MambuStruct.create")
    def test_create(self, mock_super_create):
        """Test create"""
        attrs = {"user":{"user":"moreData"}, "customInformation":[{"linkedEntityKeyValue":"userLink","customFieldSetGroupIndex":0,"customId":"id", "customValue":"value", "customField":{"state":"ACTIVE", "name":"customFieldX", "id":"customFieldID"}}]}
        u = mambuuser.MambuUser(connect=False)
        u.attrs = attrs

        data = {"dataDummy":"dataDummy"}
        # before init() method is called inside create() the attribute
        # u[u.customFieldName] not exists
        with self.assertRaisesRegexp(KeyError, r"^'%s'"%(u.customFieldName)) as ex:
            self.assertTrue(u[u.customFieldName])
        self.assertEqual(u.create(data), None)
        mock_super_create.assert_called_with(data)
        # after init() method is called inside create() the attribute
        # u[u.customFieldName] is created
        self.assertTrue(u[u.customFieldName])


class MambuUsersTests(unittest.TestCase):
    def test_class(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        self.assertTrue(mambuuser.MambuStruct in us.__class__.__bases__)

    def test_iterator(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        us.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(us), 3)
        for n,a in enumerate(us):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convertDict2Attrs(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        us.attrs = [
            {'username':"a_user"},
            {'username':"other_user"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuUsers' object has no attribute 'mambuuserclass'"):
            us.mambuuserclass
        us.convertDict2Attrs()
        self.assertEqual(str(us.mambuuserclass), "<class 'MambuPy.rest.mambuuser.MambuUser'>")
        for u in us:
            self.assertEqual(u.__class__.__name__, 'MambuUser')


if __name__ == '__main__':
    unittest.main()
