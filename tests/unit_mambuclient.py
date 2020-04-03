# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import json

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock
import unittest

from MambuPy import mambuconfig
for k,v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambuclient

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRegex instead

class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text

class MambuClientTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import getclienturl
        self.assertEqual(mambuclient.mod_urlfunc, getclienturl)

    def test_class(self):
        cl = mambuclient.MambuClient(urlfunc=None)
        self.assertTrue(mambuclient.MambuStruct in cl.__class__.__bases__)

    def test___init__(self):
        cl = mambuclient.MambuClient(urlfunc=None, entid="anything")
        self.assertEqual(cl.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from MambuPy.mambuutil import getclienturl
        def build_mock_cln_1(self, *args, **kwargs):
            self.attrs = {
                'id' : args[1]
                }

        with mock.patch.object(mambuclient.MambuStruct, "__init__", build_mock_cln_1):
            cl = mambuclient.MambuClient(urlfunc=getclienturl, entid="mockclient")
            self.assertRegexpMatches(repr(cl), r"^MambuClient - id: mockclient")

    def test_preprocess(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id'         : "myClient_12345",
                             'firstName'  : " MyName ",
                             'middleName' : " MyMiddleName ",
                             'lastName'   : " MyLastName1 MyLastName2 ",
                             'client'     : {'uno':1, 'dos':2},
                             'addresses'  : [{'dir1':"PERIFERICO"      , 'num':"2258"},
                                             {'dir1':"ESTADO DE MEXICO", 'num':"3"}
                                            ],
                             'idDocuments': [{'documentType':"CURP", 'documentId':"ABCD123456DEFGHI12"},
                                             {'documentType':"INE" , 'documentId':"1234567890"}]
                            }
        with mock.patch.object(mambuclient.MambuStruct, "connect", mock_connect):
            cl = mambuclient.MambuClient(urlfunc=lambda x:x)
            self.assertEqual(cl['firstName'], ' MyName ')
            self.assertEqual(cl['middleName'], ' MyMiddleName ')
            self.assertEqual(cl['lastName'], ' MyLastName1 MyLastName2 ')
            self.assertFalse(cl.has_key('givenName'))
            self.assertTrue(cl.has_key('client'))
            cl.preprocess()
            self.assertEqual(cl['uno'],1)
            self.assertEqual(cl['dos'],2)
            self.assertEqual(cl['firstName'], 'MyName')
            self.assertEqual(cl['middleName'], 'MyMiddleName')
            self.assertEqual(cl['lastName'], 'MyLastName1 MyLastName2')
            self.assertEqual(cl['givenName'], 'MyName MyMiddleName')
            self.assertEqual(cl['firstLastName'], 'MyLastName1')
            self.assertEqual(cl['secondLastName'], 'MyLastName2')
            self.assertEqual(cl['name'], 'MyName MyMiddleName MyLastName1 MyLastName2')
            self.assertEqual(cl['address'], {'dir1':"PERIFERICO", 'num':"2258"})
            self.assertEqual(cl['CURP'],"ABCD123456DEFGHI12")
            self.assertEqual(cl['INE'],"1234567890")
            self.assertFalse(cl.has_key('client'))

    def test_postprocess(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id'        : "myClient_12345",
                             'addresses' : [{'dir1':"PERIFERICO"      , 'num':2258},
                                            {'dir1':"ESTADO DE MEXICO", 'num':3}
                                           ],
                             'address'   : {'dir1':"PERIFERICO", 'num':2258}
                            }
        with mock.patch.object(mambuclient.MambuStruct, "connect", mock_connect):
            cl = mambuclient.MambuClient(urlfunc=lambda x:x)
            cl.postprocess()
            self.assertEqual(cl['addresses'][0]['num'],"2258")
            self.assertEqual(cl['address']['num'],"2258")

    def test_setGroups(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id':"myClient_12345", 'groupKeys':["dummyGroupId1"]}
        class my_group(object):
            def __init__(self, id, groupname):
                self.attrs = {'id':id, 'groupName':groupname}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambuclient.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambugroup.MambuGroup') as mock_mambugroup:
            my_group_instance = my_group(id        = "dummyGroupId1",
                                         groupname = "myGroupName1")
            mock_mambugroup.return_value = my_group_instance

            # no mambugroupclass yet
            cl = mambuclient.MambuClient(urlfunc=lambda x:x)
            self.assertFalse(cl.has_key('groups'))
            cl.setGroups()
            self.assertTrue(cl.has_key('groups'))
            mock_mambugroup.assert_called_once_with(entid='dummyGroupId1')
            self.assertEqual(cl['groups'], [my_group_instance])

            # already with mambugroupclass
            mock_mambugroup.reset_mock()
            cl.setGroups()
            self.assertTrue(cl.has_key('groups'))
            mock_mambugroup.assert_called_once_with(entid='dummyGroupId1')

    def test_setBranch(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {'id':"12345", 'assignedBranchKey':"brnch12345"}
        class my_branch(object):
            def __init__(self, id, name):
                self.attrs = {'id':id, 'name':name}
            def __getitem__(self,item):
                return self.attrs[item]
        with mock.patch.object(mambuclient.MambuStruct, "connect", mock_connect),\
             mock.patch('MambuPy.rest.mambubranch.MambuBranch') as mock_mambubranch:
            my_branch_instance = my_branch(id="dummyBranchId",name="myBranchName")
            mock_mambubranch.return_value = my_branch_instance

            cl = mambuclient.MambuClient(urlfunc=lambda x:x)
            self.assertFalse(cl.has_key('assignedBranch'))
            self.assertFalse(cl.has_key('assignedBranchName'))
            self.assertFalse(cl.has_key('mambubranchclass'))

            # no mambubranchclass yet
            cl.setBranch()
            self.assertTrue(cl.has_key('assignedBranch'))
            self.assertTrue(cl.has_key('assignedBranchName'))
            self.assertTrue(cl.has_key('mambubranchclass'))
            mock_mambubranch.assert_called_once_with(entid='brnch12345')
            self.assertEqual(cl['assignedBranch'], my_branch_instance)
            self.assertEqual(cl['assignedBranchName'], "myBranchName")

            # already with mambubranchclass
            mock_mambubranch.reset_mock()
            cl.setBranch()
            self.assertTrue(cl.has_key('assignedBranch'))
            self.assertTrue(cl.has_key('assignedBranchName'))
            self.assertTrue(cl.has_key('mambubranchclass'))
            mock_mambubranch.assert_called_once_with(entid='brnch12345')

    @mock.patch('MambuPy.rest.mambustruct.requests')
    def test_create(self, mock_requests):
        """Test create"""
        # set data response
        mock_requests.post.return_value = Response('{"client":{"encodedKey":"8a8186ae6e4cc970016e4cf510a60488","state":"PENDING_APPROVAL","id":"AXC657","creationDate":"2019-11-08T21:39:19+0000","lastModifiedDate":"2019-11-08T21:39:19+0000","firstName":"Paola","lastName":"Escobita Lopez","emailAddress":"NA","mobilePhone1":"1122334455","birthDate":"2000-01-01T00:00:00+0000","gender":"FEMALE","loanCycle":0,"groupLoanCycle":0,"preferredLanguage":"SPANISH","clientRole":{"encodedKey":"8a1357704bf8b4f1014bf8b874cb07ac"}},"customInformation":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048b","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818ebc581aebb501581c4f0ed813d3","customField":{"encodedKey":"8a818ebc581aebb501581c4f0ed813d3","id":"nombre_referencia_1","creationDate":"2016-10-31T19:54:53+0000","lastModifiedDate":"2018-10-01T17:43:51+0000","name":"Nombre referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Nombre de referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":8,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818ebc581aebb501581c4f0ed813d4","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818ebc581aebb501581c4f0edd13d5","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"ANA LAURA LOPEZ","indexInList":0,"customFieldID":"nombre_referencia_1","customFieldSetGroupIndex":-1},{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048c","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818ebc581aebb501581c51b2c9149f","customField":{"encodedKey":"8a818ebc581aebb501581c51b2c9149f","id":"telefono_referencia_1","creationDate":"2016-10-31T19:57:46+0000","lastModifiedDate":"2018-10-01T17:44:01+0000","name":"Telefono referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Telefono de referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":19,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818ebc581aebb501581c51b2c914a0","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818ebc581aebb501581c51b2ce14a1","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"5511937471","indexInList":1,"customFieldID":"telefono_referencia_1","customFieldSetGroupIndex":-1},{"encodedKey":"8a8186ae6e4cc970016e4cf5133d048d","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818e6b62c12baf0162c5d54b2532e6","customField":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e6","id":"parentesco_referencia_1","creationDate":"2018-04-14T20:25:13+0000","lastModifiedDate":"2019-02-26T18:56:41+0000","name":"Parentesco referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Parentesco de la referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":20,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e7","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e8","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"AMIGA","indexInList":2,"customFieldID":"parentesco_referencia_1","customFieldSetGroupIndex":-1}],"idDocuments":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a60489","clientKey":"8a8186ae6e4cc970016e4cf510a60488","documentType":"CURP","documentId":"ABCD123456MMCZRR04","issuingAuthority":"SEGOB","indexInList":0,"identificationDocumentTemplateKey":"8af6e10a3b66af8f013b674a671a0ee5"}],"addresses":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048a","parentKey":"8a8186ae6e4cc970016e4cf510a60488","line1":"8 Howling Lane","line2":"Hackney","city":"London","region":"London","postcode":"1234554321","country":"United Kingdom","indexInList":0}]}')
        c = mambuclient.MambuClient(connect=False)
        # since we mock requests.post, send any data
        self.assertEqual(c.create({"client":"data"}), 1)
        # at the end of MambuStruct.connect() are stablished all fields with the init() method
        self.assertEqual(c["firstName"], "Paola")
        self.assertEqual(c["name"], "Paola Escobita Lopez")

    @mock.patch('MambuPy.rest.mambustruct.requests')
    def test_update(self, mock_requests):
        """Test update"""
        # set data response
        mock_requests.patch.return_value = Response('{"returnCode":0,"returnStatus":"SUCCESS"}')
        mock_requests.post.return_value = Response('{"client":{"encodedKey":"8a8186ae6e4cc970016e4cf510a60488","state":"PENDING_APPROVAL","id":"AXC657","creationDate":"2019-11-08T21:39:19+0000","lastModifiedDate":"2019-11-08T21:39:19+0000","firstName":"Paola","lastName":"Escobita Lopez","emailAddress":"NA","mobilePhone1":"1122334455","birthDate":"2000-01-01T00:00:00+0000","gender":"FEMALE","loanCycle":0,"groupLoanCycle":0,"preferredLanguage":"SPANISH","clientRole":{"encodedKey":"8a1357704bf8b4f1014bf8b874cb07ac"}},"customInformation":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048b","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818ebc581aebb501581c4f0ed813d3","customField":{"encodedKey":"8a818ebc581aebb501581c4f0ed813d3","id":"nombre_referencia_1","creationDate":"2016-10-31T19:54:53+0000","lastModifiedDate":"2018-10-01T17:43:51+0000","name":"Nombre referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Nombre de referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":8,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818ebc581aebb501581c4f0ed813d4","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818ebc581aebb501581c4f0edd13d5","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"ANA LAURA LOPEZ","indexInList":0,"customFieldID":"nombre_referencia_1","customFieldSetGroupIndex":-1},{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048c","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818ebc581aebb501581c51b2c9149f","customField":{"encodedKey":"8a818ebc581aebb501581c51b2c9149f","id":"telefono_referencia_1","creationDate":"2016-10-31T19:57:46+0000","lastModifiedDate":"2018-10-01T17:44:01+0000","name":"Telefono referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Telefono de referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":19,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818ebc581aebb501581c51b2c914a0","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818ebc581aebb501581c51b2ce14a1","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"5511937471","indexInList":1,"customFieldID":"telefono_referencia_1","customFieldSetGroupIndex":-1},{"encodedKey":"8a8186ae6e4cc970016e4cf5133d048d","parentKey":"8a8186ae6e4cc970016e4cf510a60488","customFieldKey":"8a818e6b62c12baf0162c5d54b2532e6","customField":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e6","id":"parentesco_referencia_1","creationDate":"2018-04-14T20:25:13+0000","lastModifiedDate":"2019-02-26T18:56:41+0000","name":"Parentesco referencia 1","type":"CLIENT_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":false,"isRequired":false,"description":"Parentesco de la referencia 1 de la cliente","customFieldSet":{"encodedKey":"8a818ebc581aebb501581c4798de127c","id":"Referencias_Integrantes","name":"Referencias","notes":"","createdDate":"2016-10-31T19:46:44+0000","indexInList":8,"type":"CLIENT_INFO","usage":"SINGLE"},"indexInList":20,"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e7","isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818e6b62c12baf0162c5d54b2532e8","isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2"]},"unique":false,"values":[],"amounts":{}},"value":"AMIGA","indexInList":2,"customFieldID":"parentesco_referencia_1","customFieldSetGroupIndex":-1}],"idDocuments":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a60489","clientKey":"8a8186ae6e4cc970016e4cf510a60488","documentType":"CURP","documentId":"ABCD123456MMCZRR04","issuingAuthority":"SEGOB","indexInList":0,"identificationDocumentTemplateKey":"8af6e10a3b66af8f013b674a671a0ee5"}],"addresses":[{"encodedKey":"8a8186ae6e4cc970016e4cf510a6048a","parentKey":"8a8186ae6e4cc970016e4cf510a60488","line1":"8 Howling Lane","line2":"Hackney","city":"London","region":"London","postcode":"1234554321","country":"United Kingdom","indexInList":0}]}')
        mambuclient.MambuStruct.update = mock.Mock()
        mambuclient.MambuStruct.update.return_value = 1
        c = mambuclient.MambuClient(connect=False)
        c.attrs = {}
        cData = {}
        # send none data
        self.assertEqual(c.update(cData), 1)
        cData["client"] = "clientData"
        self.assertEqual(c.update(cData), 2)
        cData["customInformation"] = {"f1":1}
        self.assertEqual(c.update(cData), 3)
        cData["addresses"] = ["oneAddress"]
        self.assertEqual(c.update(cData), 4)

        mambuclient.MambuStruct.update.assert_called()


class MambuClientsTests(unittest.TestCase):
    def test_class(self):
        clns = mambuclient.MambuClients(urlfunc=None)
        self.assertTrue(mambuclient.MambuStruct in clns.__class__.__bases__)

    def test_iterator(self):
        clns = mambuclient.MambuClients(urlfunc=None)
        clns.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(clns), 3)
        for n,c in enumerate(clns):
            self.assertEqual(str(n), [k for k in c][0])
            self.assertEqual(n, c[str(n)])

    def test_convertDict2Attrs(self):
        clns = mambuclient.MambuClients(urlfunc=None)
        clns.attrs = [
            {'id':"1", 'firstName':"my_client"},
            {'id':"2", 'firstName':"my_2_client"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuClients' object has no attribute 'mambuclientclass'"):
            clns.mambuclientclass
        with mock.patch('MambuPy.rest.mambuclient.MambuClient.preprocess') as mock_preprocess:
            clns.convertDict2Attrs()
            self.assertEqual(str(clns.mambuclientclass), "<class 'MambuPy.rest.mambuclient.MambuClient'>")
            for c in clns:
                self.assertEqual(c.__class__.__name__, 'MambuClient')


if __name__ == '__main__':
    unittest.main()
