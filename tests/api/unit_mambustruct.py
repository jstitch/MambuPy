import copy
import inspect
import json
import os
import sys
import unittest
from datetime import datetime

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities, mambustruct
from MambuPy.mambuutil import (OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
                               MambuError, MambuPyError)


class MagicMethodsTests(unittest.TestCase):
    def test___init__(self):
        ms = mambustruct.MambuMapObj(some="value")
        self.assertEqual(ms._attrs, {"some": "value"})

    def test___getitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms["hello"], "world")

    def test___getitem__CF(self):
        ms = mambustruct.MambuMapObj(cf_class=entities.MambuEntityCF)
        cf = entities.MambuEntityCF("world")
        ms._attrs = {"hello": cf}
        self.assertEqual(ms["hello"], "world")
        self.assertEqual(
            ms._attrs["hello"]._attrs, {"value": "world", "path": "", "type": "STANDARD"}
        )
        self.assertEqual(ms["hello"], "world")

        with self.assertRaises(KeyError):
            ms["goodbye"]

    def test___setitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {}  # should be automatically created?
        ms["hello"] = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})

    def test___setitem__CF(self):
        ms = mambustruct.MambuMapObj(cf_class=entities.MambuEntityCF)
        cf = entities.MambuEntityCF("world")
        ms._attrs = {"hello": cf}

        ms["hello"] = "goodbye"
        self.assertEqual(
            ms._attrs["hello"]._attrs,
            {"value": "goodbye", "path": "", "type": "STANDARD"},
        )

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
        cf = entities.MambuEntityCF("world")
        ms = mambustruct.MambuMapObj(cf_class=entities.MambuEntityCF)
        ms._attrs = {"hello": cf}
        self.assertEqual(ms["hello"], "world")
        self.assertEqual(
            ms._attrs["hello"]._attrs, {"value": "world", "path": "", "type": "STANDARD"}
        )
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
        cf = entities.MambuEntityCF("world")
        ms = mambustruct.MambuMapObj(cf_class=entities.MambuEntityCF)
        ms._attrs = {"hello": cf}

        ms.hello = "goodbye"
        self.assertEqual(
            ms._attrs["hello"]._attrs,
            {"value": "goodbye", "path": "", "type": "STANDARD"},
        )

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


class MambuConnectorTests(unittest.TestCase):
    def test_has_mambuconnector(self):
        ms = entities.MambuEntity()
        self.assertEqual(ms._connector.__class__.__name__, "MambuConnectorREST")


class MambuStructTests(unittest.TestCase):
    def test__convertDict2Attrs(self):
        """Test conversion of dictionary elements (strings) in to proper datatypes"""
        ms = mambustruct.MambuStruct()
        ms._attrs = {
            "aStr": "abc123",
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
                {"key": "123"},
            ],
            "aDict": {
                "str": "abc123",
                "num": "123",
                "trailZeroes": "00123",
                "float": "15.56",
                "date": "2021-10-23T10:36:00-06:00",
                "list": ["123"],
                "dict": {"key": "123"},
            },
        }
        ms._tzattrs = copy.deepcopy(ms._attrs)

        ms._convertDict2Attrs()

        # extracts timezone info from aDate field
        self.assertEqual(
            ms._tzattrs,
            {
                "aDate": "UTC-06:00",
                "anotherDate": None,
                "aList": [None, None, None, None, "UTC-06:00", [None], {}],
                "aDict": {"date": "UTC-06:00", "list": [None], "dict": {}},
            },
        )

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
            ms.aDate, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S")
        )

        # lists recursively convert each of its elements
        self.assertEqual(
            ms.aList,
            [
                "abc123",
                123,
                "00123",
                15.56,
                datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"),
                [123],
                {"key": 123},
            ],
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
        self.assertEqual(
            ms._tzattrs,
            {
                "aDate": "UTC-06:00",
                "anotherDate": None,
                "aList": [None, None, None, None, "UTC-06:00", [None], {}],
                "aDict": {"date": "UTC-06:00", "list": [None], "dict": {}},
            },
        )
        self.assertEqual(ms.aStr, "abc123")
        self.assertEqual(ms.aNum, 123)
        self.assertEqual(ms.trailZeroes, "00123")
        self.assertEqual(ms.aFloat, 15.56)
        self.assertEqual(ms.aBool, True)
        self.assertEqual(ms.otherBool, False)
        self.assertEqual(
            ms.aDate, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S")
        )
        self.assertEqual(
            ms.aList,
            [
                "abc123",
                123,
                "00123",
                15.56,
                datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"),
                [123],
                {"key": 123},
            ],
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
        someDate = datetime.strptime("2021-10-23T10:36:00", "%Y-%m-%dT%H:%M:%S")
        someMambuStructObj = mambustruct.MambuStruct()
        ms = mambustruct.MambuStruct()
        ms._attrs = {
            "aStr": "abc123",
            "aNum": 123,
            "trailZeroes": "00123",
            "aFloat": 15.56,
            "aBool": True,
            "otherBool": False,
            "aDate": someDate,
            "aList": ["abc123", 123, "00123", 15.56, someDate, [123], {"key": 123}],
            "aDict": {
                "str": "abc123",
                "num": 123,
                "trailZeroes": "00123",
                "float": 15.56,
                "date": someDate,
                "list": [123],
                "dict": {"key": 123},
            },
            "aMambuStruct": someMambuStructObj,
        }
        ms._tzattrs = {
            "aDate": "UTC-06:00",
            "aList": [None, None, None, None, "UTC-05:00", [None], {}],
            "aDict": {"date": None},
        }

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
        self.assertEqual(ms.aDate, someDate.isoformat() + "-06:00")

        # lists recursively convert each of its elements
        self.assertEqual(
            ms.aList,
            [
                "abc123",
                "123",
                "00123",
                "15.56",
                someDate.isoformat() + "-05:00",
                ["123"],
                {"key": "123"},
            ],
        )

        # dictonaries recursively convert each of its elements
        self.assertEqual(
            ms.aDict,
            {
                "str": "abc123",
                "num": "123",
                "trailZeroes": "00123",
                "float": "15.56",
                "date": someDate.isoformat()[:10],
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
        self.assertEqual(ms.aDate, someDate.isoformat() + "-06:00")
        self.assertEqual(
            ms.aList,
            [
                "abc123",
                "123",
                "00123",
                "15.56",
                someDate.isoformat() + "-05:00",
                ["123"],
                {"key": "123"},
            ],
        )
        self.assertEqual(
            ms.aDict,
            {
                "str": "abc123",
                "num": "123",
                "trailZeroes": "00123",
                "float": "15.56",
                "date": someDate.isoformat()[:10],
                "list": ["123"],
                "dict": {"key": "123"},
            },
        )
        self.assertEqual(ms.aMambuStruct, someMambuStructObj)

    def test__extractCustomFields(self):
        ms = mambustruct.MambuStruct(cf_class=entities.MambuEntityCF)
        ms._attrs = {
            "aField": "abc123",
            "_customFieldList": [
                {"str": "abc123", "num": 123, "float": 15.56, "_index": 0},
                {"str": "def456", "num": 456, "float": 23.34, "_index": 1},
            ],
            "_customFieldDict": {"str": "abc123", "num": 123, "float": 15.56},
        }

        ms._extractCustomFields()

        self.assertEqual(ms.aField, "abc123")
        self.assertEqual(ms.customFieldList, ms._customFieldList)
        self.assertEqual(ms.str, ms._customFieldDict["str"])
        self.assertEqual(ms.num, ms._customFieldDict["num"])
        self.assertEqual(ms.float, ms._customFieldDict["float"])

        # idempotency
        ms._extractCustomFields()
        self.assertEqual(ms.aField, "abc123")
        self.assertEqual(ms.customFieldList, ms._customFieldList)
        self.assertEqual(ms.str, ms._customFieldDict["str"])
        self.assertEqual(ms.num, ms._customFieldDict["num"])
        self.assertEqual(ms.float, ms._customFieldDict["float"])

        ms._attrs["_invalidFieldSet"] = "someVal"
        with self.assertRaisesRegex(
            MambuPyError, r"CustomFieldSet _invalidFieldSet is not a dictionary"
        ):
            ms._extractCustomFields()

        del ms._attrs["_invalidFieldSet"]
        ms._attrs["_invalidListField"] = ["somfield", "another"]
        with self.assertRaisesRegex(
            MambuPyError,
            r"CustomFieldSet _invalidListField is not a list of dictionaries",
        ):
            ms._extractCustomFields()

        some_external_attr = {"_mycf": {"hello": "world"}}
        ms._extractCustomFields(some_external_attr)
        self.assertEqual(some_external_attr["hello"]["value"], "world")
        self.assertEqual(some_external_attr["hello"]["path"], "/_mycf/hello")
        self.assertEqual(some_external_attr["hello"]["type"], "STANDARD")

    def test__updateCustomFields(self):
        extracted_fields = {
            "aField": "abc123",
            "_customFieldList": [
                {
                    "str": "abc123",
                    "num": 123,
                    "float": 15.56,
                    "bool": True,
                    "not_converted": "?",
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": False,
                    "not_converted": "?",
                    "_index": 1,
                },
                "invalidElement",
            ],
            "_customFieldDict": {"num": 123, "bool": True, "not_converted": "?"},
            "_notConvertedList": [],
            "num": 123,
            "bool": True,
            "customFieldList": [
                {"str": "abc123", "num": 123, "float": 15.56, "_index": 0},
                {"str": "def456", "num": 456, "float": 23.34, "_index": 1},
            ],
            "str_0": "abc123",
            "num_0": 123,
            "float_0": 15.56,
            "bool_0": True,
            "str_1": "def456",
            "num_1": 456,
            "float_1": 23.34,
            "bool_1": False,
        }
        ms = mambustruct.MambuStruct()
        ms._attrs = copy.deepcopy(extracted_fields)

        ms._attrs["num"] = 321
        ms._attrs["customFieldList"][0]["num"] = 321

        ms._updateCustomFields()

        self.assertEqual(
            ms._customFieldList,
            [
                {
                    "str": "abc123",
                    "num": 321,
                    "float": 15.56,
                    "bool": "TRUE",
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": "FALSE",
                    "_index": 1,
                },
            ],
        )
        self.assertEqual(ms._customFieldDict["num"], 321)
        self.assertEqual(ms._customFieldDict["bool"], "TRUE")
        self.assertEqual(hasattr(ms, "num"), False)
        self.assertEqual(hasattr(ms, "bool"), False)
        self.assertEqual(hasattr(ms, "customFieldList"), False)

        # idempotency
        ms._updateCustomFields()
        self.assertEqual(
            ms._customFieldList,
            [
                {
                    "str": "abc123",
                    "num": 321,
                    "float": 15.56,
                    "bool": "TRUE",
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": "FALSE",
                    "_index": 1,
                },
            ],
        )
        self.assertEqual(ms._customFieldDict["num"], 321)
        self.assertEqual(ms._customFieldDict["bool"], "TRUE")
        self.assertEqual(hasattr(ms, "num"), False)
        self.assertEqual(hasattr(ms, "bool"), False)
        self.assertEqual(hasattr(ms, "customFieldList"), False)

        ms._attrs = copy.deepcopy(extracted_fields)
        ms._attrs["_invalidFieldSet"] = "someVal"
        with self.assertRaisesRegex(
            MambuPyError, r"CustomFieldSet _invalidFieldSet is not a dictionary"
        ):
            ms._updateCustomFields()

    def test__extractVOs(self):
        ms = mambustruct.MambuStruct()
        ms._vos = [("a_vo", "MambuValueObject"),
                   ("a_list_vo", "MambuValueObject")]
        ms._attrs = {
            "aField": "abc123",
            "a_vo": {"aProp": "aVal"},
            "a_list_vo": [{"aProp1": "aVal1"}, {"aProp2": "aVal2"}],
        }

        ms._extractVOs()

        self.assertEqual(ms.a_vo.__class__.__name__, "MambuValueObject")
        for ind, elem in enumerate(ms.a_list_vo):
            self.assertEqual(elem.__class__.__name__, "MambuValueObject")

        # idempotency
        ms._extractVOs()
        self.assertEqual(ms.a_vo.__class__.__name__, "MambuValueObject")
        for ind, elem in enumerate(ms.a_list_vo):
            self.assertEqual(elem.__class__.__name__, "MambuValueObject")

        # if fields are absent from _attrs, don't break
        ms._attrs = {
            "aField": "abc123",
        }
        ms._extractVOs()
        self.assertFalse("a_vo" in ms._attrs)
        self.assertFalse("a_list_vo" in ms._attrs)

    @mock.patch("MambuPy.api.mambustruct.import_module")
    def test__extractVOs_assignEntObjs(self, mock_import):
        from MambuPy.api import vos
        mock_import.return_value = vos
        vos.MambuValueObject._assignEntObjs = mock.Mock()

        ms = mambustruct.MambuStruct()
        ms._vos = [("a_vo", "MambuValueObject"),
                   ("a_list_vo", "MambuValueObject")]
        ms._attrs = {
            "aField": "abc123",
            "a_vo": {"aProp": "aVal"},
            "a_list_vo": [{"aProp1": "aVal1"}, {"aProp2": "aVal2"}]}
        ms._assignEntObjs = mock.Mock()

        ms._extractVOs(get_entities=True)
        vos.MambuValueObject._assignEntObjs.assert_called_with(
            [], get_entities=True, debug=False)
        self.assertEqual(vos.MambuValueObject._assignEntObjs.call_count, 3)

    def test__updateVOs(self):
        from mambupy.api.vos import MambuValueObject

        ms = mambustruct.MambuStruct()
        ms._vos = [("a_vo", "MambuValueObject"),
                   ("a_list_vo", "MambuValueObject"),]
        ms._attrs = {
            "aField": "abc123",
            "a_vo": MambuValueObject(**{"aProp": "aVal"}),
            "a_list_vo": [MambuValueObject(**{"aProp1": "aVal1"}),
                          MambuValueObject(**{"aProp2": "aVal2"})],
        }

        ms.a_vo.aProp = "anotherVal"
        ms.a_list_vo[0].aProp1 = "anotherVal1"
        ms.a_list_vo[1].aProp2 = "anotherVal2"

        ms._updateVOs()

        self.assertEqual(ms.a_vo, {"aProp": "anotherVal"})
        self.assertEqual(ms.a_list_vo, [{"aProp1": "anotherVal1"},
                                        {"aProp2": "anotherVal2"}])

        # idempotency
        ms._updateVOs()

        self.assertEqual(ms.a_vo, {"aProp": "anotherVal"})
        self.assertEqual(ms.a_list_vo, [{"aProp1": "anotherVal1"},
                                        {"aProp2": "anotherVal2"}])

        # if fields are absent from _attrs, don't break
        ms._attrs = {
            "aField": "abc123",
        }
        ms._updateVOs()
        self.assertFalse("a_vo" in ms._attrs)
        self.assertFalse("a_list_vo" in ms._attrs)

    @mock.patch("MambuPy.api.mambustruct.import_module")
    def test__assignEntObjs(self, mock_import):
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone"]

        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "entities.MambuEntity", "an_ent"),
                        ("a_list_ent_keys", "entities.MambuEntity", "ents")]
        ms._attrs = {
            "aField": "abc123",
            "an_ent_key": "abcdef12345",
            "a_list_ent_keys": ["fedcba6789", "02468acebdf"],
        }

        ms._assignEntObjs()
        self.assertEqual(mock_import.call_count, 2)
        mock_import.assert_any_call(".entities", "mambupy.api")
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 3)
        mock_import().MambuEntity.get.assert_any_call(
            "abcdef12345", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba6789", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "02468acebdf", detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])

        # optional arguments
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone"]
        mock_import.reset_mock()
        ms._assignEntObjs(detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "abcdef12345", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba6789", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "02468acebdf", detailsLevel="FULL", get_entities=True, debug=True)

        # explicit entities list argument
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone"]
        mock_import.reset_mock()
        ms._assignEntObjs([
            ("an_ent_key", "entities.MambuEntity", "an_ent"),
            ("a_list_ent_keys", "entities.MambuEntity", "ents")])
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])

        # invalid entity key as argument
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone"]
        mock_import.reset_mock()
        ms._assignEntObjs([
            ("an_INVALID_ent_key", "entities.MambuEntity", "an_ent")])
        self.assertEqual(mock_import.call_count, 1)
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 0)

        # get doesn't supports detailsLevel argument
        mock_import.return_value.MambuEntity.get.side_effect = [
            TypeError(""), "Treebeard",
            TypeError(""), "Quickbeam",
            TypeError(""), "Beechbone"]
        mock_import.reset_mock()
        ms._assignEntObjs()
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "abcdef12345", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "fedcba6789", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "02468acebdf", get_entities=False, debug=False)
        self.assertEqual(mock_import.call_count, 2)
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 6)
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])

        # invalid import, assigns None to property
        mock_import.return_value.invalid_class.get.side_effect = AttributeError("")
        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "invalid_class", "an_ent")]
        ms._attrs = {
            "an_ent_key": "abcdef12345",
        }
        ms._assignEntObjs()
        self.assertEqual(ms.an_ent, None)

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._assignEntObjs")
    def test_getEntities(self, mock_assign):
        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "entities.MambuEntity", "an_ent"),
                        ("a_list_ent_keys", "entities.MambuEntity", "ents")]
        ms._attrs = {
            "aField": "abc123",
            "an_ent_key": "abcdef12345",
            "a_list_ent_keys": ["fedcba6789", "02468acebdf"],
            "lost_entwives": [
                mambustruct.MambuStruct(),
                mambustruct.MambuStruct(),
                "notsonofmine"],
        }
        ms.lost_entwives[0]._entities = [("Fimbrethil", "entwive", "treebeards")]
        ms.lost_entwives[1]._entities = [("Wandlimb", "entwive", "treebeards2")]
        ms.lost_entwives[0]._assignEntObjs = mock.Mock()
        ms.lost_entwives[1]._assignEntObjs = mock.Mock()

        ms.getEntities(["an_ent"])
        mock_assign.assert_called_with(
            entities=[("an_ent_key", "entities.MambuEntity", "an_ent")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)
        self.assertEqual(mock_assign.call_count, 1)

        # optional arguments
        mock_assign.reset_mock()
        ms.getEntities(
            ["ents"], detailsLevel="FULL", get_entities=True, debug=True)
        mock_assign.assert_called_with(
            entities=[("a_list_ent_keys", "entities.MambuEntity", "ents")],
            detailsLevel="FULL",
            get_entities=True,
            debug=True)
        self.assertEqual(mock_assign.call_count, 1)

        # entities for items in a list
        mock_assign.reset_mock()
        ms.getEntities(["lost_entwives"])
        ms.lost_entwives[0]._assignEntObjs.assert_called_with(
            entities=[("Fimbrethil", "entwive", "treebeards")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)
        ms.lost_entwives[1]._assignEntObjs.assert_called_with(
            entities=[("Wandlimb", "entwive", "treebeards2")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)
        self.assertEqual(mock_assign.call_count, 0)

        # exception, there's no such property
        with self.assertRaisesRegex(
            MambuPyError, r"^The name \w+ is not part of the nested entities$"
        ):
            ms.getEntities(["Saruman"])

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._assignEntObjs")
    def test___getattribute__(self, mock_assign):
        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "entities.MambuEntity", "an_ent")]
        ms._attrs = {
            "aField": "abc123",
            "an_ent_key": "abcdef12345",
        }

        self.assertEqual(inspect.isfunction(ms.get_an_ent), True)
        self.assertEqual(
            inspect.getsource(ms.get_an_ent).strip(),
            "return lambda **kwargs: self.getEntities([ent], **kwargs)")
        ms.get_an_ent()
        mock_assign.assert_called_with(
            entities=[("an_ent_key", "entities.MambuEntity", "an_ent")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)

        # normal getattribute
        self.assertEqual(ms.aField, "abc123")
        with self.assertRaises(AttributeError):
            ms.some_unexistent_property


class MambuEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class(entities.MambuEntity):
            _prefix = "un_prefix"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}

        class child_class_writable(
            entities.MambuEntity, entities.MambuEntityWritable
        ):
            _prefix = "un_prefix"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}

        class child_class_attachable(
            entities.MambuEntity, entities.MambuEntityAttachable
        ):
            _prefix = "un_prefix"
            _ownerType = "MY_ENTITY"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}
                self._attachments = {}

        class child_class_commentable(
            entities.MambuEntity, entities.MambuEntityCommentable
        ):
            _prefix = "un_prefix"
            _ownerType = "MY_ENTITY"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}

        class child_class_searchable(
            entities.MambuEntity, entities.MambuEntitySearchable
        ):
            """"""

        self.child_class = child_class
        self.child_class._assignEntObjs = mock.Mock()
        self.child_class_writable = child_class_writable
        self.child_class_attachable = child_class_attachable
        self.child_class_commentable = child_class_commentable
        self.child_class_searchable = child_class_searchable

    def test_has_properties(self):
        me = entities.MambuEntity()
        self.assertEqual(me._prefix, "")

    @mock.patch("MambuPy.api.entities.print")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    def test__get_several(
        self,
        mock_extractVOs,
        mock_extractCustomFields,
        mock_convertDict2Attrs,
        mock_print
    ):
        mock_func = mock.Mock()

        mock_func.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"},
        {"encodedKey":"ghi789","id":"54321"},
        {"encodedKey":"jkl012","id":"09876"}
        ]"""

        ms = self.child_class._get_several(mock_func)

        self.assertEqual(len(ms), 4)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(list(ms[0]._tzattrs.keys()), ["encodedKey", "id"])
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})
        self.assertEqual(list(ms[1]._tzattrs.keys()), ["encodedKey", "id"])
        self.assertEqual(ms[2].__class__.__name__, "child_class")
        self.assertEqual(ms[2]._attrs, {"encodedKey": "ghi789", "id": "54321"})
        self.assertEqual(list(ms[2]._tzattrs.keys()), ["encodedKey", "id"])
        self.assertEqual(ms[3].__class__.__name__, "child_class")
        self.assertEqual(ms[3]._attrs, {"encodedKey": "jkl012", "id": "09876"})
        self.assertEqual(list(ms[3]._tzattrs.keys()), ["encodedKey", "id"])

        mock_func.assert_called_with(
            "un_prefix",
            offset=0,
            limit=OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
            detailsLevel="BASIC",
        )
        self.assertEqual(mock_convertDict2Attrs.call_count, 4)
        mock_convertDict2Attrs.assert_called_with()
        self.assertEqual(mock_extractCustomFields.call_count, 4)
        mock_extractCustomFields.assert_called_with()
        self.assertEqual(mock_extractVOs.call_count, 4)
        mock_extractVOs.assert_called_with(
            get_entities=False, debug=False)

        elems = self.child_class._get_several(
            mock_func,
            **{"prefix": "something else",
               "get_entities": True,
               "debug": True})
        mock_func.assert_called_with(
            "something else",
            offset=0,
            limit=OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
            detailsLevel="BASIC"
        )
        mock_print.assert_called_with(
            "child_class" + "-" +
            elems[0]._attrs["id"] +
            " ({}) ".format(len(elems)) +
            "0:0:0.0")
        for elem in elems:
            elem._assignEntObjs.assert_called_with(
                [], "BASIC", True, debug=True)

        entities.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 5
        self.child_class._get_several(mock_func, detailsLevel="FULL")
        mock_func.assert_called_with("un_prefix", offset=0, limit=5, detailsLevel="FULL")

        self.child_class._get_several(mock_func, offset=20, limit=2)
        mock_func.assert_called_with(
            "un_prefix", offset=20, limit=2, detailsLevel="BASIC"
        )

        mock_func.reset_mock()
        mock_func.side_effect = [
            b"""[{"encodedKey":"abc123","id":"12345"}]""",
            b"""[{"encodedKey":"def456","id":"67890"}]""",
            b"""[{"encodedKey":"ghi789","id":"54321"}]""",
            b"""[{"encodedKey":"jkl012","id":"09876"}]""",
            b"""[]""",
        ]
        entities.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1
        self.child_class._get_several(mock_func, limit=4)
        self.assertEqual(mock_func.call_count, 4)
        mock_func.assert_any_call("un_prefix", offset=0, limit=1, detailsLevel="BASIC")
        mock_func.assert_any_call("un_prefix", offset=1, limit=1, detailsLevel="BASIC")
        mock_func.assert_any_call("un_prefix", offset=2, limit=1, detailsLevel="BASIC")
        mock_func.assert_any_call("un_prefix", offset=3, limit=1, detailsLevel="BASIC")

        entities.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

    @mock.patch("MambuPy.api.entities.print")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_get(
        self,
        mock_connector,
        mock_extractVOs, mock_extractCustomFields, mock_convertDict2Attrs,
        mock_print
    ):
        mock_connector.mambu_get.return_value = b'{"encodedKey":"abc123","id":"12345"}'

        ms = self.child_class.get("12345")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms._detailsLevel, "BASIC")
        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="BASIC"
        )
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with(
            get_entities=False, debug=False)

        ms = self.child_class.get("12345", "FULL")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="FULL"
        )

        ms = self.child_class.get("12345", get_entities=True, debug=True)
        mock_print.assert_called_with(
            "child_class" + "-" +
            ms._attrs["id"] +
            " 0:0:0.0")
        ms._assignEntObjs.assert_called_with(
            [], "BASIC", True, debug=True)

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_refresh(
        self, mock_connector,
        mock_extractVOs, mock_extractCustomFields, mock_convertDict2Attrs
    ):
        mock_connector.mambu_get.return_value = (
            b'{"encodedKey":"abc123","id":"12345","someAttribute":"someValue"}'
        )
        ms = self.child_class.get("12345", detailsLevel="FULL")
        ms.test_prop = "testing"
        ms.someAttribute = "anotherValue"

        mock_connector.reset_mock()
        ms.refresh()

        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="FULL"
        )
        self.assertEqual(ms.test_prop, "testing")
        self.assertEqual(ms.someAttribute, "someValue")

        mock_connector.reset_mock()
        ms.refresh(detailsLevel="BASIC")
        mock_connector.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="BASIC"
        )

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_get_all(self, mock_connector):
        mock_connector.mambu_get_all.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]"""

        ms = self.child_class.get_all()

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})

        self.child_class._filter_keys = ["one"]
        ms = self.child_class.get_all(filters={"one": "two"})

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all_filters_n_sortby(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        self.child_class._filter_keys = ["branchId"]
        self.child_class._sortBy_fields = ["id"]

        ms = self.child_class.get_all()
        self.assertEqual(ms, "SupGetSeveral")

        ms = self.child_class.get_all(filters={})
        self.assertEqual(ms, "SupGetSeveral")

        ms = self.child_class.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(ms, "SupGetSeveral")

        ms = self.child_class.get_all(sortBy="id:ASC")
        self.assertEqual(ms, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            self.child_class.get_all(filters={"branchId": "MyBranch", "Squad": "Red"})

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            self.child_class.get_all(sortBy="field:ASC")

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all_kwargs(self, mock_get_several):
        self.child_class.get_all(**{"hello": "world"})
        mock_get_several.assert_any_call(
            self.child_class._connector.mambu_get_all,
            filters=None,
            offset=None, limit=None,
            paginationDetails="OFF", detailsLevel="BASIC",
            sortBy=None,
            hello="world")

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_search(self, mock_connector):
        mock_connector.mambu_search.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]"""

        ms = self.child_class_searchable.search()

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})

        ms = self.child_class_searchable.search(
            filterCriteria={"one": "two"}, otherParam="random")

        mock_connector.mambu_search.assert_called_with(
            "",
            filterCriteria={"one": "two"},
            sortingCriteria=None,
            offset=0,
            limit=1000,
            paginationDetails="OFF",
            detailsLevel="BASIC",
            otherParam="random")
        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_update(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
        mock_extractCustomFields,
        mock_extractVOs
    ):
        mock_connector.mambu_update.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child = self.child_class_writable()
        child._attrs["myProp"] = "myVal"

        child.update()

        mock_connector.mambu_update.assert_called_with(
            "12345", "un_prefix", {"id": "12345", "myProp": "myVal"}
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with()

        # MambuError
        mock_updateVOs.reset_mock()
        mock_updateCustomFields.reset_mock()
        mock_serializeFields.reset_mock()
        mock_convertDict2Attrs.reset_mock()
        mock_extractCustomFields.reset_mock()
        mock_extractVOs.reset_mock()
        mock_connector.mambu_update.side_effect = MambuError("Un Err")
        with self.assertRaisesRegex(MambuError, r"Un Err"):
            child.update()
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_create(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
        mock_extractCustomFields,
        mock_extractVOs,
    ):
        mock_connector.mambu_create.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child = self.child_class_writable()
        child._attrs = {}
        child._attrs["myProp"] = "myVal"
        child._detailsLevel = "BASIC"

        child.create()

        self.assertEqual(
            child._resp,
            b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }""",
        )
        self.assertEqual(
            child._attrs,
            {"encodedKey": "0123456789abcdef", "id": "12345", "myProp": "myVal"},
        )
        self.assertEqual(child._detailsLevel, "FULL")
        mock_connector.mambu_create.assert_called_with("un_prefix", {"myProp": "myVal"})
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with()

        # MambuError
        child._attrs = {}
        child._attrs["myProp"] = "myVal"
        child._detailsLevel = "BASIC"
        mock_updateVOs.reset_mock()
        mock_updateCustomFields.reset_mock()
        mock_serializeFields.reset_mock()
        mock_convertDict2Attrs.reset_mock()
        mock_extractCustomFields.reset_mock()
        mock_extractVOs.reset_mock()
        mock_connector.mambu_create.side_effect = MambuError("Un Err")
        with self.assertRaisesRegex(MambuError, r"Un Err"):
            child.create()
        self.assertEqual(child._attrs, {"myProp": "myVal"})
        self.assertEqual(child._detailsLevel, "BASIC")
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_add(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["myProp"] = "myVal"

        child.patch(["myProp"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("ADD", "/myProp", "myVal")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_replace(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["myProp"] = "myVal2"

        child.patch(["myProp"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REPLACE", "/myProp", "myVal2")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_remove(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child._attrs = dict(json.loads(child._resp))
        del child._attrs["myProp"]

        child.patch(autodetect_remove=True)

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REMOVE", "/myProp")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_add_cf_standard(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = {}
        child._attrs["myProp"] = entities.MambuEntityCF("myVal", "/_myCFSet/myProp")

        child.patch(["myProp"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("ADD", "/_myCFSet/myProp", "myVal")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_replace_cf_standard(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","_myCFSet":{"myProp":"myVal"}
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = {"myProp": "myVal"}
        child._attrs["myProp"] = entities.MambuEntityCF("myVal2", "/_myCFSet/myProp")

        child.patch(["myProp"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REPLACE", "/_myCFSet/myProp", "myVal2")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_remove_cf_standard(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","_myCFSet":{"myProp":"myVal"}
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = {"myProp": "myVal"}
        child._attrs["myProp"] = entities.MambuEntityCF("myVal", "/_myCFSet/myProp")

        del child._attrs["myProp"]
        child.patch(autodetect_remove=True)

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REMOVE", "/_myCFSet/myProp")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_add_cf_grouped(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = []
        child._attrs["myCFSet"] = []
        child._attrs["myProp"] = entities.MambuEntityCF(
            "myVal", "/_myCFSet/0/myProp", "GROUPED"
        )

        child.patch(["myProp"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("ADD", "/_myCFSet/0/myProp", "myVal")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_replace_cf_grouped(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","_myCFSet":[{"myProp":"myVal"},{"myProp":"myVal2"}]
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = [{"myProp": "myVal"}, {"myProp": "myVal2"}]
        child._attrs["myCFSet"] = [{}, {}]
        child._attrs["myProp_0"] = entities.MambuEntityCF(
            "myVal", "/_myCFSet/0/myProp", "GROUPED"
        )
        child._attrs["myProp_1"] = entities.MambuEntityCF(
            "myVal2", "/_myCFSet/1/myProp", "GROUPED"
        )

        child._attrs["myProp_1"] = entities.MambuEntityCF(
            "myVal3", "/_myCFSet/1/myProp", "GROUPED"
        )
        child.patch(["myProp_1"])

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REPLACE", "/_myCFSet/1/myProp", "myVal3")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_remove_cf_grouped(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","_myCFSet":[{"myProp":"myVal"},{"myProp":"myVal2"}]
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["_myCFSet"] = [{"myProp": "myVal"}, {"myProp": "myVal2"}]
        child._attrs["myCFSet"] = [{}, {}]
        child._attrs["myProp_0"] = entities.MambuEntityCF(
            "myVal", "/_myCFSet/0/myProp", "GROUPED"
        )
        child._attrs["myProp_1"] = entities.MambuEntityCF(
            "myVal2", "/_myCFSet/1/myProp", "GROUPED"
        )

        del child._attrs["myProp_0"]
        child.patch(autodetect_remove=True)

        mock_connector.mambu_patch.assert_called_once_with(
            "12345", "un_prefix", [("REMOVE", "/_myCFSet/0/myProp")]
        )
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_patch_exceptions(
        self,
        mock_connector,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["myProp"] = "myVal2"

        with self.assertRaisesRegex(
            MambuPyError, r"Unrecognizable field \w+ for patching"
        ):
            child.patch(["myProperty"])

        mock_connector.mambu_patch.side_effect = MambuError("A Mambu Error")
        with self.assertRaisesRegex(MambuError, r"A Mambu Error"):
            child.patch(["myProp"])

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_attach_document(self, mock_connector):
        mock_connector.mambu_upload_document.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","ownerType":"MY_ENTITY",
        "type":"png","fileName":"someImage.png"
        }"""
        child = self.child_class_attachable()
        upl = child.attach_document("/tmp/someImage.png", "MyImage", "this is a test")

        self.assertEqual(list(child._attachments.keys()), ["12345"])
        self.assertEqual(
            child._attachments["12345"]._attrs,
            {
                "encodedKey": "0123456789abcdef",
                "id": "12345",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "someImage.png",
            },
        )
        self.assertEqual(upl, mock_connector.mambu_upload_document.return_value)
        mock_connector.mambu_upload_document.assert_called_with(
            owner_type="MY_ENTITY",
            entid="12345",
            filename="/tmp/someImage.png",
            name="MyImage",
            notes="this is a test",
        )

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_get_attachments_metadata(self, mock_connector):
        mock_connector.mambu_get_documents_metadata.return_value = b"""[{
        "encodedKey":"0123456789abcdef","id":"67890","ownerType":"MY_ENTITY",
        "type":"png","fileName":"someImage.png"
        },
        {
        "encodedKey":"fedcba9876543210","id":"09876","ownerType":"MY_ENTITY",
        "type":"png","fileName":"anotherImage.png"
        }]"""

        child = self.child_class_attachable()
        metadata = child.get_attachments_metadata()

        self.assertEqual(list(child._attachments.keys()), ["67890", "09876"])
        self.assertEqual(
            child._attachments["67890"]._attrs,
            {
                "encodedKey": "0123456789abcdef",
                "id": "67890",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "someImage.png",
            },
        )
        self.assertEqual(
            child._attachments["09876"]._attrs,
            {
                "encodedKey": "fedcba9876543210",
                "id": "09876",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "anotherImage.png",
            },
        )
        self.assertEqual(
            metadata,
            mock_connector.mambu_get_documents_metadata.return_value)
        mock_connector.mambu_get_documents_metadata.assert_called_with(
            entid="12345",
            owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF"
        )
        mock_connector.mambu_get_documents_metadata.assert_called_with(
            entid="12345",
            owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF"
        )

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_del_attachment(self, mock_connector):
        mock_connector.mambu_delete_document.return_value = None

        child = self.child_class_attachable()
        child._attachments = {
            "67890": {
                "encodedKey": "0123456789abcdef",
                "id": "67890",
                "ownerType": "MY_ENTITY",
                "name": "someImage",
                "type": "png",
                "fileName": "someImage.png"
            },
            "09876": {
                "encodedKey": "fedcba9876543210",
                "id": "09876",
                "ownerType": "MY_ENTITY",
                "name": "anotherImage",
                "type": "png",
                "fileName": "anotherImage.png"
            },
            "75310": {
                "encodedKey": "fedcba9876543210",
                "id": "75310",
                "ownerType": "MY_ENTITY",
                "name": "yaImage",
                "type": "png",
                "fileName": "yaImage.png"
            },
        }

        with self.assertRaisesRegex(
            MambuPyError,
            r"^You must provide a documentId or a documentName$"
        ):
            child.del_attachment()

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document name 'aName' is not an attachment of child_class_attachable - id: 12345$"
        ):
            child.del_attachment(documentName="aName")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document id 'anId' is not an attachment of child_class_attachable - id: 12345$"
        ):
            child.del_attachment(documentId="anId")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document with name 'anotherImage' does not has id '67890'$"
        ):
            child.del_attachment(documentId="67890", documentName="anotherImage")

        child.del_attachment(documentId="67890")
        self.assertEqual(
            sorted(list(child._attachments.keys())),
            ["09876", "75310"])
        mock_connector.mambu_delete_document.assert_called_with("67890")

        child.del_attachment(documentName="anotherImage")
        self.assertEqual(list(child._attachments.keys()), ["75310"])
        mock_connector.mambu_delete_document.assert_called_with("09876")

        child.del_attachment(documentId="75310", documentName="yaImage")
        self.assertEqual(list(child._attachments.keys()), [])
        mock_connector.mambu_delete_document.assert_called_with("75310")

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_get_comments(self, mock_connector):
        mock_connector.mambu_get_comments.return_value = b"""[{
        "encodedKey":"my_comment_EK",
        "ownerKey":"my_owner_Key",
        "ownerType":"MY_ENTITY",
        "creationDate":"2022-07-11T12:33:21-05:00",
        "lastModifiedDate":"2022-07-11T12:33:46-05:00",
        "text":"LITTLE PIGS LITTLE PIGS LET ME IN!",
        "userKey":"author_EK"
        }]"""

        child = self.child_class_commentable()
        comments = child.get_comments()

        self.assertEqual(len(child._comments), 1)
        self.assertEqual(
            child._comments[0]._attrs,
            {
                "encodedKey": "my_comment_EK",
                "ownerKey": "my_owner_Key",
                "ownerType": "MY_ENTITY",
                "creationDate": "2022-07-11T12:33:21-05:00",
                "lastModifiedDate": "2022-07-11T12:33:46-05:00",
                "text": "LITTLE PIGS LITTLE PIGS LET ME IN!",
                "userKey": "author_EK"
            })

        self.assertEqual(
            comments,
            json.loads(mock_connector.mambu_get_comments.return_value))

        mock_connector.mambu_get_comments.assert_called_once_with(
            owner_id="12345", owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF")


class MambuEntityCFTests(unittest.TestCase):
    def test___init__(self):
        ms = entities.MambuEntityCF("_VALUE_")
        self.assertEqual(ms._attrs, {"value": "_VALUE_", "path": "", "type": "STANDARD"})

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_")
        self.assertEqual(
            ms._attrs, {"value": "_VALUE_", "path": "_PATH_", "type": "STANDARD"}
        )

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_", "STANDARD")
        self.assertEqual(
            ms._attrs, {"value": "_VALUE_", "path": "_PATH_", "type": "STANDARD"}
        )

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_", "GROUPED")
        self.assertEqual(
            ms._attrs, {"value": "_VALUE_", "path": "_PATH_", "type": "GROUPED"}
        )

        with self.assertRaisesRegex(MambuPyError, r"invalid CustomField type!"):
            entities.MambuEntityCF("_VALUE_", "_PATH_", "_TYPE_")


if __name__ == "__main__":
    unittest.main()
