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
from MambuPy.rest import mambugroup

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRegex instead

class MambuGroupTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getgroupurl
        self.assertEqual(mambugroup.mod_urlfunc, getgroupurl)

    def test_class(self):
        gr = mambugroup.MambuGroup(urlfunc=None)
        self.assertTrue(mambugroup.MambuStruct in gr.__class__.__bases__)

    def test___init__(self):
        gr = mambugroup.MambuGroup(urlfunc=None, entid="anything")
        self.assertEqual(gr.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from MambuPy.mambuutil import getgroupurl
        def build_mock_grp_1(self, *args, **kwargs):
            self.attrs = {
                'id' : args[1]
                }

        with mock.patch.object(mambugroup.MambuStruct, "__init__", build_mock_grp_1):
            grp = mambugroup.MambuGroup(urlfunc=getgroupurl, entid="mockgroup")
            self.assertRegexpMatches(repr(grp), r"^MambuGroup - id: mockgroup")

    def test_preprocess(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id'        : "myGroup_12345",
                             'theGroup'  : {'uno':1, 'dos':2},
                             'notes'     : "<div>Hello World</div>",
                             'groupName' : "MyGroupName",
                             'addresses'  : [{'dir1':"PERIFERICO"      , 'num':"2258"},
                                             {'dir1':"ESTADO DE MEXICO", 'num':"3"}
                                            ],
                            }
        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect):
            grp = mambugroup.MambuGroup(urlfunc=lambda x:x)
            self.assertEqual(grp['notes'], "<div>Hello World</div>")
            self.assertEqual(grp['groupName'], "MyGroupName")
            grp.preprocess()
            self.assertEqual(grp['uno'],1)
            self.assertEqual(grp['dos'],2)
            self.assertEqual(grp['notes'], "Hello World")
            self.assertEqual(grp['name'], grp['groupName'])
            self.assertEqual(grp['address'], {'dir1':"PERIFERICO", 'num':"2258"})
            self.assertFalse(grp.has_key('theGroup'))

    def test_setClients(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id':"myGroup_12345", 'groupMembers':[{'clientKey':"dummyClientId1"},{'clientKey':"dummyClientId2"}]}
        class my_client(object):
            def __init__(self, id):
                self.attrs = {'id':id}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambuclient.MambuClient') as mock_mambuclient:
            my_client_instance_1 = my_client(id="dummyClientId1")
            my_client_instance_2 = my_client(id="dummyClientId2")
            mock_mambuclient.side_effect = [my_client_instance_1,
                                            my_client_instance_2,
                                            my_client_instance_1,
                                            my_client_instance_2,
                                            my_client_instance_1,
                                            my_client_instance_2,]

            # no mambuclientclass yet
            grp = mambugroup.MambuGroup(urlfunc=lambda x:x)
            self.assertFalse(grp.has_key('clients'))
            grp.setClients()
            self.assertTrue(grp.has_key('clients'))
            mock_mambuclient.assert_any_call(entid='dummyClientId1', fullDetails=True)
            mock_mambuclient.assert_any_call(entid='dummyClientId2', fullDetails=True)
            self.assertEqual(grp['clients'], [my_client_instance_1, my_client_instance_2])

            # already with mambuclientclass
            mock_mambuclient.reset_mock()
            grp.setClients()
            self.assertTrue(grp.has_key('clients'))
            mock_mambuclient.assert_any_call(entid='dummyClientId1', fullDetails=True)
            mock_mambuclient.assert_any_call(entid='dummyClientId2', fullDetails=True)

            # fullDetails False
            grp.setClients(fullDetails=False)
            self.assertTrue(grp.has_key('clients'))
            mock_mambuclient.assert_any_call(entid='dummyClientId1', fullDetails=False)
            mock_mambuclient.assert_any_call(entid='dummyClientId2', fullDetails=False)

    def test_setBranch(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id':"12345", 'assignedBranchKey':"brnch12345"}
        class my_branch(object):
            def __init__(self, id, name):
                self.attrs = {'id':id, 'name':name}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambubranch.MambuBranch') as mock_mambubranch:
            my_branch_instance = my_branch(id="dummyBranchId",name="myBranchName")
            mock_mambubranch.return_value = my_branch_instance

            grp = mambugroup.MambuGroup(urlfunc=lambda x:x)
            self.assertFalse(grp.has_key('branch'))
            self.assertFalse(grp.has_key('mambubranchclass'))

            # no mambubranchclass yet
            grp.setBranch()
            self.assertTrue(grp.has_key('branch'))
            self.assertTrue(grp.has_key('mambubranchclass'))
            mock_mambubranch.assert_called_once_with(entid='brnch12345')

            # already with mambubranchclass
            mock_mambubranch.reset_mock()
            grp.setBranch()
            mock_mambubranch.assert_called_once_with(entid='brnch12345')

    def test_setCentre(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id':"12345", 'assignedCentreKey':"centre12345"}
        class my_centre(object):
            def __init__(self, id, name):
                self.attrs = {'id':id, 'name':name}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambucentre.MambuCentre') as mock_mambucentre:
            my_centre_instance = my_centre(id="dummyCentreId",name="myCentreName")
            mock_mambucentre.return_value = my_centre_instance

            grp = mambugroup.MambuGroup(urlfunc=lambda x:x)
            self.assertFalse(grp.has_key('centre'))
            self.assertFalse(grp.has_key('mambucentreclass'))

            # no mambucentreclass yet
            grp.setCentre()
            self.assertTrue(grp.has_key('centre'))
            self.assertTrue(grp.has_key('mambucentreclass'))
            mock_mambucentre.assert_called_once_with(entid='centre12345')

            # already with mambucentreclass
            mock_mambucentre.reset_mock()
            grp.setCentre()
            mock_mambucentre.assert_called_once_with(entid='centre12345')

    def test_setActivities(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'encodedKey':"myGroup_12345"}
        class my_activity(object):
            def __init__(self, id, timestamp):
                self.attrs = {'id':id, 'activity':{'timestamp':timestamp}}
            def __getitem__(self,item):
                return self.attrs[item]
        class my_activities(object):
            def __init__(self, attrs):
                self.attrs = attrs
        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambuactivity.MambuActivities') as mock_mambuactivities:
            my_activity_instance_1 = my_activity(id="dummyActivityId1", timestamp=987654321)
            my_activity_instance_2 = my_activity(id="dummyActivityId2", timestamp=876543210)
            my_activities_instance = my_activities([my_activity_instance_1, my_activity_instance_2])
            mock_mambuactivities.return_value = my_activities_instance

            # no mambuactivitiesclass yet
            grp = mambugroup.MambuGroup(urlfunc=lambda x:x)
            self.assertFalse(grp.has_key('activities'))
            grp.setActivities()
            self.assertTrue(grp.has_key('activities'))
            mock_mambuactivities.assert_called_once_with(groupId='myGroup_12345')
            self.assertEqual(grp['activities'], my_activities_instance)

            # already with mambuactivitiesclass
            mock_mambuactivities.reset_mock()
            grp.setActivities()
            self.assertTrue(grp.has_key('activities'))
            mock_mambuactivities.assert_called_once_with(groupId='myGroup_12345')


class MambuGroupsTests(unittest.TestCase):
    def test_class(self):
        grps = mambugroup.MambuGroups(urlfunc=None)
        self.assertTrue(mambugroup.MambuStruct in grps.__class__.__bases__)

    def test_iterator(self):
        grps = mambugroup.MambuGroups(urlfunc=None)
        grps.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(grps), 3)
        for n,g in enumerate(grps):
            self.assertEqual(str(n), [k for k in g][0])
            self.assertEqual(n, g[str(n)])

    def test_convertDict2Attrs(self):
        grps = mambugroup.MambuGroups(urlfunc=None)
        grps.attrs = [
            {'id':"1", 'groupName':"my_group"},
            {'id':"2", 'groupName':"my_2_group"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuGroups' object has no attribute 'mambugroupclass'"):
            grps.mambugroupclass
        with mock.patch('MambuPy.rest.mambugroup.MambuGroup.preprocess') as mock_preprocess:
            grps.convertDict2Attrs()
            self.assertEqual(str(grps.mambugroupclass), "<class 'MambuPy.rest.mambugroup.MambuGroup'>")
            for g in grps:
                self.assertEqual(g.__class__.__name__, 'MambuGroup')


if __name__ == '__main__':
    unittest.main()
