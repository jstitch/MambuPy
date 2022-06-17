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
from MambuPy.rest import mambugroup

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text


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
        from MambuPy.mambuutil import getgroupurl

        def build_mock_grp_1(self, *args, **kwargs):
            self.attrs = {"id": args[1]}

        with mock.patch.object(mambugroup.MambuStruct, "__init__", build_mock_grp_1):
            grp = mambugroup.MambuGroup(urlfunc=getgroupurl, entid="mockgroup")
            self.assertRegexpMatches(repr(grp), r"^MambuGroup - id: mockgroup")

    def test_preprocess(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {
                "id": "myGroup_12345",
                "theGroup": {"uno": 1, "dos": 2},
                "notes": "<div>Hello World</div>",
                "groupName": "MyGroupName",
                "addresses": [
                    {"dir1": "PERIFERICO", "num": "2258"},
                    {"dir1": "ESTADO DE MEXICO", "num": "3"},
                ],
            }

        with mock.patch.object(mambugroup.MambuStruct, "connect", mock_connect):
            grp = mambugroup.MambuGroup(urlfunc=lambda x: x)
            self.assertEqual(grp["notes"], "<div>Hello World</div>")
            self.assertEqual(grp["groupName"], "MyGroupName")
            grp.preprocess()
            self.assertEqual(grp["uno"], 1)
            self.assertEqual(grp["dos"], 2)
            self.assertEqual(grp["notes"], "Hello World")
            self.assertEqual(grp["name"], grp["groupName"])
            self.assertEqual(grp["address"], {"dir1": "PERIFERICO", "num": "2258"})
            self.assertFalse(grp.has_key("theGroup"))

    def test_setClients(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {
                "id": "myGroup_12345",
                "groupMembers": [
                    {"clientKey": "dummyClientId1"},
                    {"clientKey": "dummyClientId2"},
                ],
            }

        class my_client(object):
            def __init__(self, id):
                self.attrs = {"id": id}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambugroup.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambuclient.MambuClient") as mock_mambuclient:
            my_client_instance_1 = my_client(id="dummyClientId1")
            my_client_instance_2 = my_client(id="dummyClientId2")
            mock_mambuclient.side_effect = [
                my_client_instance_1,
                my_client_instance_2,
                my_client_instance_1,
                my_client_instance_2,
                my_client_instance_1,
                my_client_instance_2,
            ]

            # no mambuclientclass yet
            grp = mambugroup.MambuGroup(urlfunc=lambda x: x)
            self.assertFalse(grp.has_key("clients"))
            grp.setClients()
            self.assertTrue(grp.has_key("clients"))
            mock_mambuclient.assert_any_call(entid="dummyClientId1", fullDetails=True)
            mock_mambuclient.assert_any_call(entid="dummyClientId2", fullDetails=True)
            self.assertEqual(grp["clients"], [my_client_instance_1, my_client_instance_2])

            # already with mambuclientclass
            mock_mambuclient.reset_mock()
            grp.setClients()
            self.assertTrue(grp.has_key("clients"))
            mock_mambuclient.assert_any_call(entid="dummyClientId1", fullDetails=True)
            mock_mambuclient.assert_any_call(entid="dummyClientId2", fullDetails=True)

            # fullDetails False
            grp.setClients(fullDetails=False)
            self.assertTrue(grp.has_key("clients"))
            mock_mambuclient.assert_any_call(entid="dummyClientId1", fullDetails=False)
            mock_mambuclient.assert_any_call(entid="dummyClientId2", fullDetails=False)

            # specify a mambuclientclass
            clientclass = mock.Mock()
            mock_mambuclient.reset_mock()
            grp.setClients(mambuclientclass=clientclass)
            self.assertTrue(grp.has_key("clients"))
            self.assertEqual(mock_mambuclient.call_count, 0)
            clientclass.assert_any_call(entid="dummyClientId1", fullDetails=True)
            clientclass.assert_any_call(entid="dummyClientId2", fullDetails=True)

    def test_setBranch(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "assignedBranchKey": "brnch12345"}

        class my_branch(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambugroup.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambubranch.MambuBranch") as mock_mambubranch:
            my_branch_instance = my_branch(id="dummyBranchId", name="myBranchName")
            mock_mambubranch.return_value = my_branch_instance

            grp = mambugroup.MambuGroup(urlfunc=lambda x: x)
            self.assertFalse(grp.has_key("branch"))
            self.assertFalse(grp.has_key("mambubranchclass"))

            # no mambubranchclass yet
            grp.setBranch()
            self.assertTrue(grp.has_key("branch"))
            self.assertTrue(grp.has_key("mambubranchclass"))
            mock_mambubranch.assert_called_once_with(entid="brnch12345")

            # already with mambubranchclass
            mock_mambubranch.reset_mock()
            grp.setBranch()
            mock_mambubranch.assert_called_once_with(entid="brnch12345")

    def test_setCentre(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "assignedCentreKey": "centre12345"}

        class my_centre(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambugroup.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambucentre.MambuCentre") as mock_mambucentre:
            my_centre_instance = my_centre(id="dummyCentreId", name="myCentreName")
            mock_mambucentre.return_value = my_centre_instance

            grp = mambugroup.MambuGroup(urlfunc=lambda x: x)
            self.assertFalse(grp.has_key("centre"))
            self.assertFalse(grp.has_key("mambucentreclass"))

            # no mambucentreclass yet
            grp.setCentre()
            self.assertTrue(grp.has_key("centre"))
            self.assertTrue(grp.has_key("mambucentreclass"))
            mock_mambucentre.assert_called_once_with(entid="centre12345")

            # already with mambucentreclass
            mock_mambucentre.reset_mock()
            grp.setCentre()
            mock_mambucentre.assert_called_once_with(entid="centre12345")

    def test_setActivities(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"encodedKey": "myGroup_12345"}

        class my_activity(object):
            def __init__(self, id, timestamp):
                self.attrs = {"id": id, "activity": {"timestamp": timestamp}}

            def __getitem__(self, item):
                return self.attrs[item]

        class my_activities(object):
            def __init__(self, attrs):
                self.attrs = attrs

        with mock.patch.object(
            mambugroup.MambuStruct, "connect", mock_connect
        ), mock.patch(
            "MambuPy.rest.mambuactivity.MambuActivities"
        ) as mock_mambuactivities:
            my_activity_instance_1 = my_activity(
                id="dummyActivityId1", timestamp=987654321
            )
            my_activity_instance_2 = my_activity(
                id="dummyActivityId2", timestamp=876543210
            )
            my_activities_instance = my_activities(
                [my_activity_instance_1, my_activity_instance_2]
            )
            mock_mambuactivities.return_value = my_activities_instance

            # no mambuactivitiesclass yet
            grp = mambugroup.MambuGroup(urlfunc=lambda x: x)
            self.assertFalse(grp.has_key("activities"))
            grp.setActivities()
            self.assertTrue(grp.has_key("activities"))
            mock_mambuactivities.assert_called_once_with(groupId="myGroup_12345")
            self.assertEqual(grp["activities"], my_activities_instance)

            # already with mambuactivitiesclass
            mock_mambuactivities.reset_mock()
            grp.setActivities()
            self.assertTrue(grp.has_key("activities"))
            mock_mambuactivities.assert_called_once_with(groupId="myGroup_12345")

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_create(self, mock_requests):
        """Test create"""
        # set data response
        mock_requests.post.return_value = Response(
            '{"group":{"encodedKey":"8a8186c46edd2297016edd5871271060","id":"RV982",\
"creationDate":"2019-12-06T22:49:25+0000","lastModifiedDate":"2019-12-06T22:49:25+0000",\
"groupName":"NUEVO AMANECER I(COPIA)","notes":"<div id=\\":2da\\" class=\\"ii gt adP adO\\" style=\\"direction: ltr; \
margin: 5px 15px 0px 0px; padding-bottom: 5px; position: relative; background-color: rgb(255, 255, 255);\\">\
<div id=\\":2d9\\" class=\\"a3s aXjCH m1584b9a66e5110e3\\" style=\\"overflow: hidden;\\"><div style=\\"color: \
rgb(34, 34, 34); font-family: arial, sans-serif; font-size: 12.8px;\\">Mapa de Ubicaci\xc3\xb3n:&nbsp;\
<a href=\\"https://drive.google.com/open?id=1mbQ5tI8EEOa65yQt_yArpfmfE2M&amp;usp=sharing:\\">\
https://drive.google.com/open?id=1mbQ5tI8EEOa65yQt_yArpfmfE2M&amp;usp=sharing:</a>\
<div class=\\"yj6qo\\" style=\\"color: rgb(34, 34, 34); font-family: arial, sans-serif; font-size: \
12.8px;\\"><div class=\\"hq gt a10\\" id=\\":nk\\" style=\\"clear: both; margin: 15px 0px; font-size: 12.8px; color: \
rgb(34, 34, 34); font-family: arial, sans-serif; background-color: rgb(255, 255, 255);\\">","loanCycle":0,"idPattern":\
"@@###","preferredLanguage":"ENGLISH","clientRole":{"encodedKey":"8a1357704bf8b4f1014bf8b874cc07ad"}},\
"addresses":[{"encodedKey":"8a8186c46edd2297016edd5871271061","parentKey":"8a8186c46edd2297016edd5871271060",\
"line1":"SAN FELIPE #SN","line2":"EJIDO PALMA","city":"ISIDRO FABELA","region":"MEXICO","postcode":"54480",\
"country":"MEXICO","indexInList":0}],"customInformation":[{"encodedKey":"8a8186c46edd2297016edd5871271062",\
"parentKey":"8a8186c46edd2297016edd5871271060","customFieldKey":"8afae1dc2ecf2844012ee4a468f62773",\
"customField":{"encodedKey":"8afae1dc2ecf2844012ee4a468f62773","id":"Referencia_de_ubicacion_Groups","creationDate":\
"2016-10-10T22:20:45+0000","lastModifiedDate":"2019-12-04T01:22:03+0000","name":"Referencia de ubicacion",\
"type":"GROUP_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":true,"isRequired":true,\
"description":"","customFieldSet":{"encodedKey":"8a116c9c3ce7bf9c013ce7c448b40626",\
"id":"Campos_Personalizados_Grupos","name":"Campos Personalizados","createdDate":"2013-02-17T10:47:46+0000",\
"indexInList":0,"type":"GROUP_INFO","usage":"SINGLE"},"indexInList":0,"state":"NORMAL",\
"customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818897519a4a8601519aa4bd852fd1",\
"isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818897519a4a8601519aa4bd892fd3",\
"isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94",\
"8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b",\
"8a818e5e6594c7f40165a1d7bd2a7faa","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b",\
"8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2",\
"8a818f285bfa98c1015bfe9af3de14f9"]},"unique":false,"values":[],"amounts":{}},\
"value":"CAMINO BALNEARIO MANANTIAL UNA CALLE ARRIBA DE ESTACIONAMIENTO 4 CAMINOS ","indexInList":0,\
"customFieldID":"Referencia_de_ubicacion_Groups","customFieldSetGroupIndex":-1},\
{"encodedKey":"8a8186c46edd2297016edd674faf1063","parentKey":"8a8186c46edd2297016edd5871271060",\
"customFieldKey":"8af63f3538a5ba4b0138acbe9abb1d0f","customField":{"encodedKey":"8af63f3538a5ba4b0138acbe9abb1d0f",\
"id":"Nivel_Groups","creationDate":"2016-10-10T22:20:55+0000","lastModifiedDate":"2019-12-04T01:22:20+0000",\
"name":"Nivel","type":"GROUP_INFO","dataType":"NUMBER","valueLength":"SHORT","isDefault":true,"isRequired":true,\
"description":"Nivel del grupo otorgado por el coordinador","customFieldSet":\
{"encodedKey":"8a116c9c3ce7bf9c013ce7c448b40626","id":"Campos_Personalizados_Grupos","name":"Campos Personalizados",\
"createdDate":"2013-02-17T10:47:46+0000","indexInList":0,"type":"GROUP_INFO","usage":"SINGLE"},"indexInList":2,\
"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818897519a4a8601519aa4bda32fdb",\
"isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818897519a4a8601519aa4bdae2fdd",\
"isAccessibleByAllUsers":false,"roles":["8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633",\
"8a818e09576c4cfe01576c61422a0594","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b",\
"8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2"]},\
"unique":false,"values":[],"amounts":{}},"value":"15","indexInList":1,"customFieldID":"Nivel_Groups",\
"customFieldSetGroupIndex":-1},{"encodedKey":"8a8186c46edd2297016edd674faf1064",\
"parentKey":"8a8186c46edd2297016edd5871271060","customFieldKey":"8af63f3538a5ba4b0138acbefd781d10",\
"customField":{"encodedKey":"8af63f3538a5ba4b0138acbefd781d10","id":"Ciclo-Tipo_Groups",\
"creationDate":"2016-10-10T22:21:04+0000","lastModifiedDate":"2019-12-04T01:22:34+0000",\
"name":"Ciclo-Tipo","type":"GROUP_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":true,\
"isRequired":true,"description":"Ciclo actual del grupo - Tipo de credito","customFieldSet":\
{"encodedKey":"8a116c9c3ce7bf9c013ce7c448b40626","id":"Campos_Personalizados_Grupos","name":"Campos Personalizados",\
"createdDate":"2013-02-17T10:47:46+0000","indexInList":0,"type":"GROUP_INFO","usage":"SINGLE"},"indexInList":3,\
"state":"NORMAL","customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818897519a4a8601519aa4bdbe2fe0",\
"isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818897519a4a8601519aa4bdc22fe2",\
"isAccessibleByAllUsers":false,"roles":["8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633",\
"8a818e09576c4cfe01576c61422a0594","8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b",\
"8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2"]},\
"unique":false,"values":[],"amounts":{}},"value":"C15 - CIMI","indexInList":2,"customFieldID":"Ciclo-Tipo_Groups",\
"customFieldSetGroupIndex":-1},{"encodedKey":"8a8186c46edd2297016edd674faf1065",\
"parentKey":"8a8186c46edd2297016edd5871271060","customFieldKey":"8af63f3538a5ba4b0138acc01b381d11",\
"customField":{"encodedKey":"8af63f3538a5ba4b0138acc01b381d11","id":"Dia_de_reunion_Groups",\
"creationDate":"2016-10-10T22:21:17+0000","lastModifiedDate":"2019-12-03T23:48:57+0000","name":"Dia de reunion",\
"type":"GROUP_INFO","dataType":"SELECTION","valueLength":"SHORT","isDefault":true,"isRequired":true,"description":"",\
"customFieldSet":{"encodedKey":"8a116c9c3ce7bf9c013ce7c448b40626","id":"Campos_Personalizados_Grupos",\
"name":"Campos Personalizados","createdDate":"2013-02-17T10:47:46+0000","indexInList":0,"type":"GROUP_INFO",\
"usage":"SINGLE"},"indexInList":4,"state":"NORMAL","customFieldSelectionOptions":[\
{"encodedKey":"8a68c1894cd107ab014cd10c43f41d5c","value":"Lunes","score":"1"},\
{"encodedKey":"8a68c1894cd107ab014cd10c43f61d5d","value":"Martes","score":"2"},\
{"encodedKey":"8a68c1894cd107ab014cd10c43f81d5e","value":"Miercoles","score":"3"},\
{"encodedKey":"8a68c1894cd107ab014cd10c43fa1d5f","value":"Jueves","score":"4"},\
{"encodedKey":"8a68c1894cd107ab014cd10c43fd1d60","value":"Viernes","score":"5"},\
{"encodedKey":"8a68c1894cd107ab014cd10c43ff1d61","value":"Sabado","score":"6"},\
{"encodedKey":"8a68c1894cd107ab014cd10c44021d62","value":"Domingo","score":"7"}],\
"viewRights":{"encodedKey":"8a818897519a4a8601519aa4c9ed2fe7","isAccessibleByAllUsers":true,"roles":[]},\
"editRights":{"encodedKey":"8a818897519a4a8601519aa4c9f12fe9","isAccessibleByAllUsers":false,\
"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94","8a818e2760e54d450160e6d45eaf1633",\
"8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b","8a818eca5591bf840155998756067649",\
"8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41","8a10ca994b09d039014b0e71ed7e040b",\
"8a6886e7510218560151033d4c170df2","8a818f285bfa98c1015bfe9af3de14f9"]},"unique":false,"values":["Lunes",\
"Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"],"amounts":{"Miercoles":"3","Martes":"2","Viernes":"5",\
"Lunes":"1","Domingo":"7","Jueves":"4","Sabado":"6"}},"value":"Lunes","indexInList":3,\
"customFieldID":"Dia_de_reunion_Groups","customFieldSetGroupIndex":-1},{"encodedKey":\
"8a8186c46edd2297016edd674faf1066","parentKey":"8a8186c46edd2297016edd5871271060","customFieldKey":\
"8af63f3538a5ba4b0138acc05a611d12","customField":{"encodedKey":"8af63f3538a5ba4b0138acc05a611d12",\
"id":"Hora_de_reunion_Groups","creationDate":"2016-10-10T22:21:34+0000","lastModifiedDate":"2019-12-04T01:22:52+0000",\
"name":"Hora de reunion","type":"GROUP_INFO","dataType":"STRING","valueLength":"SHORT","isDefault":true,\
"isRequired":true,"description":"","customFieldSet":{"encodedKey":"8a116c9c3ce7bf9c013ce7c448b40626",\
"id":"Campos_Personalizados_Grupos","name":"Campos Personalizados","createdDate":"2013-02-17T10:47:46+0000",\
"indexInList":0,"type":"GROUP_INFO","usage":"SINGLE"},"indexInList":5,"state":"NORMAL",\
"customFieldSelectionOptions":[],"viewRights":{"encodedKey":"8a818897519a4a8601519aa4c9ff2fec",\
"isAccessibleByAllUsers":true,"roles":[]},"editRights":{"encodedKey":"8a818897519a4a8601519aa4ca032fee",\
"isAccessibleByAllUsers":false,"roles":["8a818868520c7ca901520f6d1ae44dfe","8a818e9f5edd9fc9015ee364730f4e94",\
"8a818e2760e54d450160e6d45eaf1633","8a818e09576c4cfe01576c61422a0594","8a818e9a54e28e440154ea4c71a10f1b",\
"8a818eca5591bf840155998756067649","8a6b86a043fa70ec0143fea56df6145b","8a36366d43e6ebf90143ea757e0e5a41",\
"8a10ca994b09d039014b0e71ed7e040b","8a6886e7510218560151033d4c170df2","8a818f285bfa98c1015bfe9af3de14f9"]},\
"unique":false,"values":[],"amounts":{}},"value":"13:30","indexInList":4,"customFieldID":"Hora_de_reunion_Groups",\
"customFieldSetGroupIndex":-1}]}'
        )
        g = mambugroup.MambuGroup(connect=False)
        # since we mock requests.post, send any data
        self.assertEqual(g.create({"group": "data"}), 1)
        # at the end of MambuStruct.connect() are stablished all fields with the init() method
        self.assertEqual(g["encodedKey"], "8a8186c46edd2297016edd5871271060")
        self.assertEqual(g["groupName"], "NUEVO AMANECER I(COPIA)")
        self.assertEqual(g["id"], "RV982")

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update(self, mock_requests):
        """Test update"""
        # set data response
        mock_requests.patch.return_value = Response(
            '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        mock_requests.post.return_value = Response(
            '{"group":{"encodedKey":"8a10ca994b09d039014b145049e94892","id":"JB324",\
"creationDate":"2015-01-23T01:03:01+0000","lastModifiedDate":"2019-12-11T18:26:46+0000",\
"groupName":"ZAFIRO","notes":"Mapa de Ubicaci\xc3\xb3n<br>\
<a href=\\"https://www.google.com/maps/d/edit?mid=zWpa0weFfb88.kelST7bG9wjU&amp;usp=sharing\\">\
https://www.google.com/maps/d/edit?mid=zWpa0weFfb88.kelST7bG9wjU&amp;usp=sharing</a><br>",\
"assignedUserKey":"8a818fe569173a910169176a41ce0696","assignedBranchKey":"8a6a80593fc305e1013fc47bf2da686e",\
"loanCycle":17,"assignedCentreKey":"8a818f9767c1805b0167c33192306f02","mobilePhone1":"5550566170",\
"preferredLanguage":"SPANISH","clientRole":{"encodedKey":"8a1357704bf8b4f1014bf8b874cc07ad"}},\
"addresses":[{"encodedKey":"8a8187f56ef565cb016ef61c457221c1","parentKey":"8a10ca994b09d039014b145049e94892",\
"line1":"SAN FELIPE","line2":"EJIDO ","city":"Saltadilla","region":"MEXICO","postcode":"54480",\
"country":"MEXICO","indexInList":0}],"groupRoles":[],"groupMembers":[{"encodedKey":"8a8187c06ef5687d016ef6230ca41f7e",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a60faf23935815f01394959bf305787",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":0},{"encodedKey":"8a8187c06ef5687d016ef6230ca41f7f",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a1edda54e72f31a014e7974be7a69b2",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":1},{"encodedKey":"8a8187c06ef5687d016ef6230ca41f80",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a60faf23935815f0139497311205836",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":2},{"encodedKey":"8a8187c06ef5687d016ef624e982209e",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a10800239357cf2013949f50aa76c00",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":3},{"encodedKey":"8a8187c06ef5687d016ef624e982209f",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a60faf23935815f0139497721125857",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":4},{"encodedKey":"8a8187c06ef5687d016ef624e98220a0",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a60faf23935815f0139495e238057a4",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":5},{"encodedKey":"8a8187c06ef5687d016ef624e98220a1",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a10800239357cf2013949f233666bed",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":6},{"encodedKey":"8a8187c06ef5687d016ef624e98220a2",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a818e026be62441016be77b9e514261",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":7},{"encodedKey":"8a8187c06ef5687d016ef624e98220a3",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a818e0d617702e801617c33bef5796f",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":8},{"encodedKey":"8a8187c06ef5687d016ef624e98220a4",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a1a2fa94a2da970014a4f8dcfb94e98",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":9},{"encodedKey":"8a8187c06ef5687d016ef624e98220a5",\
"groupKey":"8a10ca994b09d039014b145049e94892","clientKey":"8a818f4067a7bee90167adb77c1b75b4",\
"creationDate":"2019-12-11T18:07:25+0000","indexInList":10}]}'
        )
        mambugroup.MambuStruct.update = mock.Mock()
        mambugroup.MambuStruct.update.return_value = 1
        g = mambugroup.MambuGroup(connect=False)
        g.attrs = {}
        gData = {}
        # send none data
        self.assertEqual(g.update(gData), 1)
        gData["groupMembers"] = [1, 2, 3]
        gData["groupRoles"] = [1, 2, 3]
        self.assertEqual(g.update(gData), 2)
        gData["group"] = {
            "groupName": "Grupo secreto",
        }
        gData["customInformation"] = {"f1": 1}
        self.assertEqual(g.update(gData), 3)
        gData["addresses"] = ["oneAddress"]
        self.assertEqual(g.update(gData), 4)

        mambugroup.MambuStruct.update.assert_called()

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_addMember(self, mock_requests):
        """Test add member to group"""
        # set data response
        mock_requests.get.return_value = Response("{}")
        mock_requests.patch.return_value = Response(
            '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        g = mambugroup.MambuGroup(
            entid="fakeID",
            urlfunc=lambda *args, **kwargs: "urlMambu",
            user="fakeUser",
            pwd="fakePwd",
        )
        g.attrs = {}
        # set groupMembers
        g.attrs["groupMembers"] = [
            {
                "clientKey": "8a818fc56e65226e016e65fcd66c64ca",
                # u'creationDate': datetime.datetime(2019, 11, 13, 18, 33, 49),
                "encodedKey": "8a818fc56e65226e016e660b08f567b5",
                "groupKey": "8a818fc56e65226e016e66065da26736",
                "indexInList": 1,
            },
            {
                "clientKey": "8a818fc56e65226e016e656582853e9d",
                # u'creationDate': datetime.datetime(2019, 11, 13, 18, 33, 49),
                "encodedKey": "8a818fc56e65226e016e660b08f567b6",
                "groupKey": "8a818fc56e65226e016e66065da26736",
                "indexInList": 2,
            },
            {
                "clientKey": "8a818e5b61de14e70161de42a3fc21a5",
                # u'creationDate': datetime.datetime(2019, 11, 13, 18, 33, 49),
                "encodedKey": "8a818fc56e65226e016e660b08f567b7",
                "groupKey": "8a818fc56e65226e016e66065da26736",
                "indexInList": 3,
            },
        ]
        # call method
        g.addMembers(["idDeIntegranteNueva"])
        mock_requests.patch.assert_called_with(
            "urlMambu",
            auth=("fakeUser", "fakePwd"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            data='{"group": {}, "groupMembers": [{"clientKey": "8a818fc56e65226e016e65fcd66c64ca"}, \
{"clientKey": "8a818fc56e65226e016e656582853e9d"}, {"clientKey": "8a818e5b61de14e70161de42a3fc21a5"}, \
{"clientKey": "idDeIntegranteNueva"}]}',
        )
        # get called when connect()
        mock_requests.get.assert_called_with(
            "urlMambu",
            auth=("fakeUser", "fakePwd"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
        )

        # GROUP whithout members
        g.addMembers(["idDeIntegranteNueva"])
        mock_requests.patch.assert_called_with(
            "urlMambu",
            auth=("fakeUser", "fakePwd"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            data='{"group": {}, "groupMembers": [{"clientKey": "idDeIntegranteNueva"}]}',
        )
        # get called when connect()
        mock_requests.get.assert_called_with(
            "urlMambu",
            auth=("fakeUser", "fakePwd"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
        )


class MambuGroupsTests(unittest.TestCase):
    def test_class(self):
        grps = mambugroup.MambuGroups(urlfunc=None)
        self.assertTrue(mambugroup.MambuStruct in grps.__class__.__bases__)

    def test_iterator(self):
        grps = mambugroup.MambuGroups(urlfunc=None)
        grps.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(grps), 3)
        for n, g in enumerate(grps):
            self.assertEqual(str(n), [k for k in g][0])
            self.assertEqual(n, g[str(n)])

    def test_convertDict2Attrs(self):
        from MambuPy.mambuutil import getgroupurl

        grps = mambugroup.MambuGroups(urlfunc=None)
        grps.attrs = [
            {"id": "1", "groupName": "my_group"},
            {"id": "2", "groupName": "my_2_group"},
        ]
        with self.assertRaisesRegexp(
            AttributeError, "'MambuGroups' object has no attribute 'mambugroupclass'"
        ):
            grps.mambugroupclass
        with mock.patch("MambuPy.rest.mambugroup.MambuGroup.preprocess"):
            grps.convertDict2Attrs()
            self.assertEqual(
                str(grps.mambugroupclass),
                "<class 'MambuPy.rest.mambugroup.MambuGroup'>",
            )
            for g in grps:
                self.assertEqual(g.__class__.__name__, "MambuGroup")
                self.assertEqual(g._MambuStruct__urlfunc, getgroupurl)


if __name__ == "__main__":
    unittest.main()
