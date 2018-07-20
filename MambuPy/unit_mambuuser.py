# coding: utf-8

import mock
import unittest

import mambuuser

class MambuUserTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from mambuutil import getuserurl
        self.assertEqual(mambuuser.mod_urlfunc, getuserurl)

    def test_class(self):
        u = mambuuser.MambuUser(urlfunc=None)
        self.assertTrue(mambuuser.MambuStruct in u.__class__.__bases__)

    def test___init__(self):
        u = mambuuser.MambuUser(urlfunc=None, entid="anything")
        self.assertEqual(u.entid, "anything")

    @mock.patch("mambuuser.MambuStruct.preprocess")
    def test_preprocess(self, mock_super_preprocess):
        from mambuutil import getuserurl
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

    @mock.patch("mambuuser.MambuGroups")
    def test_setGroups(self, mock_mambugroups):
        from mambuutil import getuserurl
        def build_mock_user(self, *args, **kwargs):
            self.attrs = {
                'username'  : args[1],
                }
        mock_mambugroups.return_value = {'id':"mock_group"}

        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            self.assertEqual(u.setGroups(), 1)
            mock_mambugroups.assert_called_with(creditOfficerUsername="jstitch")
            self.assertEqual(u.groups, {'id':"mock_group"})

    @mock.patch("mambuuser.MambuRole")
    def test_setRole(self, mock_mamburole):
        from mambuutil import getuserurl
        def build_mock_user(self, *args, **kwargs):
            self.attrs = {
                'username'  : args[1],
                }
            if kwargs.has_key('fullDetails') and kwargs['fullDetails']==True:
                self.attrs['role'] = {'encodedKey' : 'role_id'}
        mock_mamburole.return_value = {'name':"mock_role"}

        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch", fullDetails=True)
            self.assertEqual(u.setRoles(), 1)
            mock_mamburole.assert_called_with(entid="role_id")
            self.assertEqual(u.role['role'], {'name':"mock_role"})

        mock_mamburole.reset_mock()
        with mock.patch.object(mambuuser.MambuStruct, "__init__", build_mock_user):
            u = mambuuser.MambuUser(urlfunc=getuserurl, entid="jstitch")
            self.assertEqual(u.setRoles(), 0)
            self.assertFalse(mock_mamburole.called)

    @mock.patch("mambuuser.MambuStruct.create")
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
            self.assertEqual(str(n), a.keys()[0])
            self.assertEqual(n, a[str(n)])

    def test_convertDict2Attrs(self):
        us = mambuuser.MambuUsers(urlfunc=None)
        us.attrs = [
            {'username':"a_user"},
            {'username':"other_user"},
            ]
        us.convertDict2Attrs()
        for u in us:
            self.assertEqual(u.__class__.__name__, 'MambuUser')


if __name__ == '__main__':
    unittest.main()
