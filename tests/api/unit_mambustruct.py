import copy
from datetime import datetime
import mock
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import (
    MambuError,
    MambuPyError,
    OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
    )
from MambuPy.api import mambustruct


class MagicMethodsTests(unittest.TestCase):
    def test___init__(self):
        ms = mambustruct.MambuMapObj(some="value")
        self.assertEqual(ms._attrs, {"some": "value"})

    def test___getitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms["hello"], "world")

    def test___getitem__CF(self):
        ms = mambustruct.MambuMapObj()
        cf = mambustruct.MambuEntityCF("world")
        ms._attrs = {"hello": cf}
        self.assertEqual(ms["hello"], "world")
        self.assertEqual(ms._attrs["hello"]._attrs, {"value": "world"})
        self.assertEqual(ms["hello"], "world")

        with self.assertRaises(KeyError):
            ms["goodbye"]

    def test___setitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {}  # should be automatically created?
        ms["hello"] = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})

    def test___setitem__CF(self):
        ms = mambustruct.MambuMapObj()
        cf = mambustruct.MambuEntityCF("world")
        ms._attrs = {"hello": cf}

        ms["hello"] = "goodbye"
        self.assertEqual(ms._attrs["hello"]._attrs, {"value": "goodbye"})

    def test___delitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}
        del ms["hello"]
        self.assertEqual(ms._attrs, {})

    def test___str__(self):
        ms = mambustruct.MambuMapObj()

        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(str(ms), "MambuMapObj - {'id': '12345', 'hello': 'world'}")

        del ms._attrs
        ms.entid = "12345"
        self.assertEqual(str(ms), "MambuMapObj - id: '12345' (not synced with Mambu)")

    def test___repr__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"id": "12345"}
        self.assertEqual(repr(ms), "MambuMapObj - id: 12345")

        ms._attrs = {"what": "th?"}
        self.assertEqual(repr(ms), "MambuMapObj - {'what': 'th?'}")

        del ms._attrs
        ms.entid = "12345"
        self.assertEqual(repr(ms), "MambuMapObj - id: '12345' (not synced with Mambu)")

        ms._attrs = [1, 2, 3, 4, 5]
        self.assertEqual(repr(ms), "MambuMapObj - len: 5")

    def test___eq__(self):
        ms1 = mambustruct.MambuMapObj()
        self.assertEqual("123" == ms1, None)
        self.assertEqual(ms1 == "123", None)

        ms2 = mambustruct.MambuMapObj()
        self.assertEqual(ms1 == ms2, False)

        ms1._attrs = {}
        ms2._attrs = {}
        self.assertEqual(ms1 == ms2, False)

        ms1._attrs["encodedKey"] = "ek123"
        self.assertEqual(ms1 == ms2, False)

        ms2._attrs["encodedKey"] = "ek321"
        self.assertEqual(ms1 == ms2, False)

        ms2._attrs["encodedKey"] = "ek123"
        self.assertEqual(ms1 == ms2, True)

        ms = {}
        r = mambustruct.MambuMapObj.__eq__(ms, ms1)
        self.assertEqual(r, NotImplemented)

    def test___hash__(self):
        ms = mambustruct.MambuMapObj()
        ms.encodedKey = "abc123"
        self.assertEqual(hash(ms), hash("abc123"))

        ms = mambustruct.MambuMapObj()
        ms.id = "123"
        self.assertEqual(hash(ms), hash("MambuMapObj123"))

        ms = mambustruct.MambuMapObj()
        ms._attrs = {"what": "th?"}
        self.assertEqual(hash(ms), hash("MambuMapObj - {'what': 'th?'}"))

    def test___len__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(len(ms), 2)
        ms._attrs = {"id": "12345"}
        self.assertEqual(len(ms), 1)
        ms._attrs = [1, 2, 3, 4, 5]
        self.assertEqual(len(ms), 5)

    def test___contains__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual("hello" in ms, True)

    def test_get(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(ms.get("hello"), "world")

        ms._attrs = []
        with self.assertRaises(NotImplementedError):
            ms.get("hello")

    def test_keys(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.keys()), ["hello"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.keys()

    def test_items(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.items()), [("hello", "world")])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.items()

    def test_values(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.values()), ["world"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.values()

    def test___getattribute__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms._attrs, {"hello": "world"})
        self.assertEqual(ms.hello, "world")

        with self.assertRaises(AttributeError):
            ms.some_unexistent_property

    def test___getattribute__CF(self):
        cf = mambustruct.MambuEntityCF("world")
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": cf}
        self.assertEqual(ms["hello"], "world")
        self.assertEqual(ms._attrs["hello"]._attrs, {"value": "world"})
        self.assertEqual(ms.hello, "world")

    def test___setattribute__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {}
        ms.hello = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})
        ms.hello = "goodbye"
        self.assertEqual(ms._attrs, {"hello": "goodbye"})

        setattr(ms, "property", "value")
        ms.property = "othervalue"
        self.assertEqual(getattr(ms, "property"), "othervalue")

        ms = mambustruct.MambuMapObj()
        ms._attrs = []
        ms.goodbye = "cruelworld"
        self.assertEqual(getattr(ms, "goodbye"), "cruelworld")

    def test___setattribute__CF(self):
        cf = mambustruct.MambuEntityCF("world")
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": cf}

        ms.hello = "goodbye"
        self.assertEqual(ms._attrs["hello"]._attrs, {"value": "goodbye"})

    def test_has_key(self):
        ms = mambustruct.MambuMapObj()

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.has_key("hello")

        ms._attrs = []

        with self.assertRaises(NotImplementedError):
            ms.has_key("hello")

        ms._attrs = {}
        self.assertEqual(ms.has_key("goodbye"), False)

        ms._attrs = {"hello": "world"}
        self.assertEqual(ms.has_key("hello"), True)


class MambuConnector(unittest.TestCase):
    def test_has_mambuconnector(self):
        ms = mambustruct.MambuStruct()
        self.assertEqual(ms._connector.__class__.__name__, "MambuConnectorREST")


class MambuStruct(unittest.TestCase):
    def setUp(self):
        class child_class(mambustruct.MambuStruct):
            _prefix = "un_prefix"
            _ownerType = "MY_ENTITY"
            id = "12345"

        self.child_class = child_class

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    def test___get_several(
        self,
        mock_extractCustomFields,
        mock_convertDict2Attrs
    ):
        mock_func = mock.Mock()

        mock_func.return_value = b'''[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"},
        {"encodedKey":"ghi789","id":"54321"},
        {"encodedKey":"jkl012","id":"09876"}
        ]'''

        ms = self.child_class.__get_several(mock_func)

        self.assertEqual(len(ms), 4)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey":"abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey":"def456", "id": "67890"})
        self.assertEqual(ms[2].__class__.__name__, "child_class")
        self.assertEqual(ms[2]._attrs, {"encodedKey":"ghi789", "id": "54321"})
        self.assertEqual(ms[3].__class__.__name__, "child_class")
        self.assertEqual(ms[3]._attrs, {"encodedKey":"jkl012", "id": "09876"})

        mock_func.assert_called_with("un_prefix", offset=0, limit=OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE)
        self.assertEqual(mock_convertDict2Attrs.call_count, 4)
        mock_convertDict2Attrs.assert_called_with()
        self.assertEqual(mock_extractCustomFields.call_count, 4)
        mock_extractCustomFields.assert_called_with()

        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 5
        self.child_class.__get_several(mock_func)
        mock_func.assert_called_with("un_prefix", offset=0, limit=5)

        self.child_class.__get_several(mock_func, offset=20, limit=2)
        mock_func.assert_called_with("un_prefix", offset=20, limit=2)

        mock_func.reset_mock()
        mock_func.side_effect = [
            b'''[{"encodedKey":"abc123","id":"12345"}]''',
            b'''[{"encodedKey":"def456","id":"67890"}]''',
            b'''[{"encodedKey":"ghi789","id":"54321"}]''',
            b'''[{"encodedKey":"jkl012","id":"09876"}]''',
            b'''[]''',
            ]
        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1
        self.child_class.__get_several(mock_func, limit=4)
        self.assertEqual(mock_func.call_count, 4)
        mock_func.assert_any_call("un_prefix", offset=0, limit=1)
        mock_func.assert_any_call("un_prefix", offset=1, limit=1)
        mock_func.assert_any_call("un_prefix", offset=2, limit=1)
        mock_func.assert_any_call("un_prefix", offset=3, limit=1)

        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_get(
        self,
        mock_connector,
        mock_extractCustomFields,
        mock_convertDict2Attrs
    ):
        mock_connector.mambu_get.return_value = b'{"encodedKey":"abc123","id":"12345"}'

        ms = self.child_class.get("12345")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="BASIC")
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()

        ms = self.child_class.get("12345", "FULL")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="FULL")

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_get_all(self, mock_connector):
        mock_connector.mambu_get_all.return_value = b'''[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]'''

        ms = self.child_class.get_all()

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey":"abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey":"def456", "id": "67890"})

        ms = self.child_class.get_all(filters={"one": "two"})

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey":"abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey":"def456", "id": "67890"})

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_search(self, mock_connector):
        mock_connector.mambu_search.return_value = b'''[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]'''

        ms = self.child_class.search()

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey":"abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey":"def456", "id": "67890"})

        ms = self.child_class.search(filterCriteria={"one": "two"})

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey":"abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey":"def456", "id": "67890"})

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_update(self, mock_connector):
        mock_connector.mambu_update.return_value = b'''{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }'''
        child = self.child_class()
        child._attrs["myProp"] = "myVal"

        child.update()

        mock_connector.mambu_update.assert_called_with(
            "12345", "un_prefix", {"myProp": "myVal"})

        mock_connector.mambu_update.side_effect = MambuError("Un Err")
        with self.assertRaisesRegex(MambuError, r"Un Err"):
            child.update()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_attach_document(self, mock_connector):
        mock_connector.mambu_upload_document.return_value = b'''{
        "encodedKey":"0123456789abcdef","id":"12345","ownerType":"MY_ENTITY",
        "type":"png","fileName":"someImage.png"
        }'''
        upl = self.child_class().attach_document(
            "/tmp/someImage.png",
            "MyImage",
            "this is a test")

        self.assertEqual(upl, mock_connector.mambu_upload_document.return_value)
        mock_connector.mambu_upload_document.assert_called_with(
            owner_type="MY_ENTITY",
            entid="12345",
            filename="/tmp/someImage.png",
            name="MyImage",
            notes="this is a test")

        del self.child_class._ownerType
        child = self.child_class()
        with self.assertRaisesRegex(
            MambuPyError,
            r"child_class entity does not supports attachments!"
        ):
            child.attach_document(
                "/tmp/someImage.png",
                "MyImage",
                "this is a test")

    def test__convertDict2Attrs(self):
        """Test conversion of dictionary elements (strings) in to proper datatypes"""
        ms = mambustruct.MambuStruct()
        ms._attrs = {"aStr": "abc123",
                     "aNum": "123",
                     "trailZeroes": "00123",
                     "aFloat": "15.56",
                     "aBool": "TRUE",
                     "otherBool": "FALSE",
                     "aDate": "2021-10-23T10:36:00-06:00",
                     "anotherDate": "2021-10-23T10:36:00",
                     "aList": [
                         "abc123",
                         "123",
                         "00123",
                         "15.56",
                         "2021-10-23T10:36:00-06:00",
                         ["123"],
                         {"key": "123"}],
                     "aDict": {
                         "str": "abc123",
                         "num": "123",
                         "trailZeroes": "00123",
                         "float": "15.56",
                         "date": "2021-10-23T10:36:00-06:00",
                         "list": ["123"],
                         "dict": {"key": "123"}}
                     }
        ms._tzattrs = copy.deepcopy(ms._attrs)

        ms._convertDict2Attrs()

        # extracts timezone info from aDate field
        self.assertEqual(ms._tzattrs, {"aDate": "UTC-06:00",
                                       "anotherDate": None,
                                       "aList": [
                                           None,
                                           None,
                                           None,
                                           None,
                                           "UTC-06:00",
                                           [None],
                                           {}],
                                       "aDict": {
                                           "date": "UTC-06:00",
                                           "list": [None],
                                           "dict": {}}
                                           })

        # string remains string
        self.assertEqual(ms.aStr, "abc123")

        # integer transforms in to int
        self.assertEqual(ms.aNum, 123)

        # integer with trailing 0's remains as string
        self.assertEqual(ms.trailZeroes, "00123")

        # floating point transforms in to float
        self.assertEqual(ms.aFloat, 15.56)

        # "TRUE" transforms in to boolean True
        self.assertEqual(ms.aBool, True)

        # "FALSE" transforms in to boolean False
        self.assertEqual(ms.otherBool, False)

        # datetime transforms in to datetime object
        self.assertEqual(
            ms.aDate,
            datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"))

        # lists recursively convert each of its elements
        self.assertEqual(
            ms.aList,
            ["abc123", 123, "00123", 15.56, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"), [123], {"key": 123}],
        )

        # dictonaries recursively convert each of its elements
        self.assertEqual(
            ms.aDict,
            {
             "str": "abc123",
             "num": 123,
             "trailZeroes": "00123",
             "float": 15.56,
             "date": datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"),
             "list": [123],
             "dict": {"key": 123},
            },
        )

        # idempotency
        ms._convertDict2Attrs()
        self.assertEqual(ms._tzattrs, {"aDate": "UTC-06:00",
                                       "anotherDate": None,
                                       "aList": [
                                           None,
                                           None,
                                           None,
                                           None,
                                           "UTC-06:00",
                                           [None],
                                           {}],
                                       "aDict": {
                                           "date": "UTC-06:00",
                                           "list": [None],
                                           "dict": {}}
                                           })
        self.assertEqual(ms.aStr, "abc123")
        self.assertEqual(ms.aNum, 123)
        self.assertEqual(ms.trailZeroes, "00123")
        self.assertEqual(ms.aFloat, 15.56)
        self.assertEqual(ms.aBool, True)
        self.assertEqual(ms.otherBool, False)
        self.assertEqual(
            ms.aDate,
            datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(
            ms.aList,
            ["abc123", 123, "00123", 15.56, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"), [123], {"key": 123}],
        )
        self.assertEqual(
            ms.aDict,
            {
             "str": "abc123",
             "num": 123,
             "trailZeroes": "00123",
             "float": 15.56,
             "date": datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"),
             "list": [123],
             "dict": {"key": 123},
            },
        )

        # certain fields remain as-is with no conversion to anything
        data = {
            "id": "12345",
            "groupName": "3.1415792",
            "name": "2.78",
            "homePhone": "2021-10-23T10:36:00-06:00",
            "mobilePhone": "54321",
            "mobilePhone2": "-1.256",
            "postcode": "98765",
            "emailAddress": "TRUE",
            "description": "FALSE",
            "someKey": "0123",
            }
        ms._attrs = {}
        for key, val in data.items():
            ms._attrs[key] = val
        ms._tzattrs = copy.deepcopy(ms._attrs)

        ms._convertDict2Attrs()
        for key, val in ms._attrs.items():
            self.assertEqual(val, data[key])

        # idempotency
        ms._convertDict2Attrs()
        for key, val in ms._attrs.items():
            self.assertEqual(val, data[key])

    def test__serializeFields(self):
        """Test revert of conversion from dictionary elements (native datatype)
        to strings"""
        someDate = datetime.strptime(
            "2021-10-23T10:36:00", "%Y-%m-%dT%H:%M:%S")
        someMambuStructObj = self.child_class()
        ms = mambustruct.MambuStruct()
        ms._attrs = {"aStr": "abc123",
                     "aNum": 123,
                     "trailZeroes": "00123",
                     "aFloat": 15.56,
                     "aBool": True,
                     "otherBool": False,
                     "aDate": someDate,
                     "aList": [
                         "abc123",
                         123,
                         "00123",
                         15.56,
                         someDate,
                         [123],
                         {"key": 123}],
                     "aDict": {
                         "str": "abc123",
                         "num": 123,
                         "trailZeroes": "00123",
                         "float": 15.56,
                         "date": someDate,
                         "list": [123],
                         "dict": {"key": 123}},
                     "aMambuStruct": someMambuStructObj,
                     }
        ms._tzattrs = {"aDate": "UTC-06:00",
                       "aList": [
                           None, None, None, None,
                           "UTC-05:00",
                           [None],
                           {}],
                        "aDict": {
                            "date": None}}

        ms._serializeFields()

        # string remains string
        self.assertEqual(ms.aStr, "abc123")

        # integer transformation to str
        self.assertEqual(ms.aNum, "123")

        # integer with trailing 0's remains as string
        self.assertEqual(ms.trailZeroes, "00123")

        # floating point transformation to str
        self.assertEqual(ms.aFloat, "15.56")

        # boolean True transforms in to "TRUE"
        self.assertEqual(ms.aBool, "true")

        # boolean False transforms in to "FALSE"
        self.assertEqual(ms.otherBool, "false")

        # datetime transformation to str using timezone
        self.assertEqual(
            ms.aDate,
            someDate.isoformat() + "-06:00")

        # lists recursively convert each of its elements
        self.assertEqual(
            ms.aList,
            ["abc123", "123", "00123", "15.56", someDate.isoformat() + "-05:00", ["123"], {"key": "123"}],
        )

        # dictonaries recursively convert each of its elements
        self.assertEqual(
            ms.aDict,
            {
             "str": "abc123",
             "num": "123",
             "trailZeroes": "00123",
             "float": "15.56",
             "date": someDate.isoformat(),
             "list": ["123"],
             "dict": {"key": "123"},
            },
        )

        # MambuStruct objects are kept as is
        self.assertEqual(ms.aMambuStruct, someMambuStructObj)

        # idempotency
        ms._serializeFields()
        self.assertEqual(ms.aStr, "abc123")
        self.assertEqual(ms.aNum, "123")
        self.assertEqual(ms.trailZeroes, "00123")
        self.assertEqual(ms.aFloat, "15.56")
        self.assertEqual(ms.aBool, "true")
        self.assertEqual(ms.otherBool, "false")
        self.assertEqual(
            ms.aDate,
            someDate.isoformat() + "-06:00")
        self.assertEqual(
            ms.aList,
            ["abc123", "123", "00123", "15.56", someDate.isoformat() + "-05:00", ["123"], {"key": "123"}],
        )
        self.assertEqual(
            ms.aDict,
            {
             "str": "abc123",
             "num": "123",
             "trailZeroes": "00123",
             "float": "15.56",
             "date": someDate.isoformat(),
             "list": ["123"],
             "dict": {"key": "123"},
            },
        )
        self.assertEqual(ms.aMambuStruct, someMambuStructObj)

    def test__extractCustomFields(self):
        ms = mambustruct.MambuStruct()
        ms._attrs = {"aField": "abc123",
                     "_customFieldList": [
                         "abc123",
                         123,
                         15.56],
                     "_customFieldDict": {
                         "str": "abc123",
                         "num": 123,
                         "float": 15.56}
                     }

        ms._extractCustomFields()

        self.assertEqual(ms.aField, "abc123")
        self.assertEqual(ms.customFieldList, ms._customFieldList)
        self.assertEqual(ms.str, ms._customFieldDict["str"])
        self.assertEqual(ms.num, ms._customFieldDict["num"])
        self.assertEqual(ms.float, ms._customFieldDict["float"])

        ms._attrs["_invalidFieldSet"] = "someVal"
        with self.assertRaisesRegex(
            MambuPyError,
            r"CustomFieldSet _invalidFieldSet is not a dictionary"
        ):
            ms._extractCustomFields()

    def test__updateCustomFields(self):
        ms = mambustruct.MambuStruct()
        ms._attrs = {"aField": "abc123",
                     "_customFieldList": [
                         "abc123",
                         123,
                         15.56],
                     "_customFieldDict": {
                         "num": 123,
                         "bool": True},
                     "num": 123,
                     "bool": True,
                     "customFieldList": [
                         "abc123",
                         123,
                         15.56],
                     }

        ms._attrs["num"] = 321
        ms._attrs["customFieldList"][1] = 321
        ms._updateCustomFields()

        self.assertEqual(ms._customFieldList, ["abc123", 321, 15.56])
        self.assertEqual(ms._customFieldDict["num"], 321)
        self.assertEqual(ms._customFieldDict["bool"], "TRUE")
        self.assertEqual(hasattr(ms, "num"), False)
        self.assertEqual(hasattr(ms, "bool"), False)
        self.assertEqual(hasattr(ms, "customFieldList"), False)

        ms._attrs["_invalidFieldSet"] = "someVal"
        with self.assertRaisesRegex(
            MambuPyError,
            r"CustomFieldSet _invalidFieldSet is not a dictionary"
        ):
            ms._updateCustomFields()


class MambuEntity(unittest.TestCase):
    def test_has_properties(self):
        me = mambustruct.MambuEntity()
        self.assertEqual(me._prefix, "")


class MambuEntityCF(unittest.TestCase):
    def test___init__(self):
        ms = mambustruct.MambuEntityCF("_VALUE_")
        self.assertEqual(ms._attrs, {"value": "_VALUE_"})


if __name__ == "__main__":
    unittest.main()
