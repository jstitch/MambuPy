import copy
import inspect
import os
import sys
import unittest
from datetime import datetime

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities, mambucustomfield, mambustruct
from MambuPy.mambuutil import MambuPyError


class MambuStructTests(unittest.TestCase):
    def test__convertDict2Attrs_not_comparable(self):
        class A():
            def __eq__(self, other):
                raise TypeError("non-comparable types")

        ms = mambustruct.MambuStruct()
        ms._attrs = {
            "aObj": A(),
        }
        ms._convertDict2Attrs()

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
        other_ms = mambustruct.MambuStruct()
        other_ms._attrs = {
            "aNum": "123",
        }
        other_ms._tzattrs = copy.deepcopy(other_ms._attrs)
        ms._attrs["aMambuEnt"] = other_ms
        ms._tzattrs["aMambuEnt"] = {}

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

        #
        self.assertEqual(ms.aMambuEnt, other_ms)

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
        class A():
            def __eq__(self, other):
                raise TypeError("non-comparable types")

        obj0 = mambustruct.MambuStruct()
        obj0.encodedKey = "someEncodedKey"
        obj1 = mambustruct.MambuStruct()
        obj1.encodedKey = "anotherEncodedKey"
        obj = mambustruct.MambuStruct()
        obj.encodedKey = "myEncodedKey"
        obj_new = mambustruct.MambuStruct()
        obj_new.encodedKey = "newEncodedKey"
        extracted_fields = {
            "aField": "abc123",
            "_customFieldList": [
                {
                    "str": "abc123",
                    "num": 123,
                    "float": 15.56,
                    "bool": True,
                    "obj": "someEncodedKey",
                    "not_converted": "?",
                    "exception": A(),
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": False,
                    "obj": "anotherEncodedKey",
                    "not_converted": "?",
                    "exception": A(),
                    "_index": 1,
                },
                "invalidElement",
            ],
            "_customFieldDict": {"num": 123, "bool": True, "obj": "myEncodedKey", "not_converted": "?"},
            "_notConvertedList": [],
            "num": 123,
            "bool": True,
            "obj": obj,
            "customFieldList": [
                {"str": "abc123", "num": 123, "float": 15.56, "bool": True, "obj": obj0, "_index": 0},
                {"str": "def456", "num": 456, "float": 23.34, "bool": True, "obj": obj1, "_index": 1},
            ],
            "str_0": "abc123",
            "num_0": 123,
            "float_0": 15.56,
            "bool_0": True,
            "obj_0": obj0,
            "exception_0": A(),
            "str_1": "def456",
            "num_1": 456,
            "float_1": 23.34,
            "bool_1": False,
            "obj_1": obj1,
            "exception_1": A(),
        }
        ms = mambustruct.MambuStruct()
        ms._attrs = copy.deepcopy(extracted_fields)

        ms._attrs["num"] = 321
        ms._attrs["obj"] = obj_new
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
                    "obj": "someEncodedKey",
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": "FALSE",
                    "obj": "anotherEncodedKey",
                    "_index": 1,
                },
            ],
        )
        self.assertEqual(ms._customFieldDict["num"], 321)
        self.assertEqual(ms._customFieldDict["bool"], "TRUE")
        self.assertEqual(ms._customFieldDict["obj"], "newEncodedKey")
        self.assertEqual(hasattr(ms, "num"), False)
        self.assertEqual(hasattr(ms, "bool"), False)
        self.assertEqual(hasattr(ms, "obj"), False)
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
                    "obj": "someEncodedKey",
                    "_index": 0,
                },
                {
                    "str": "def456",
                    "num": 456,
                    "float": 23.34,
                    "bool": "FALSE",
                    "obj": "anotherEncodedKey",
                    "_index": 1,
                },
            ],
        )
        self.assertEqual(ms._customFieldDict["num"], 321)
        self.assertEqual(ms._customFieldDict["bool"], "TRUE")
        self.assertEqual(hasattr(ms, "num"), False)
        self.assertEqual(hasattr(ms, "bool"), False)
        self.assertEqual(hasattr(ms, "obj"), False)
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
        ms._tzattrs = {"a_vo": {"hello": "world"},
                       "a_list_vo": [{"tzAProp1": "tzAVal1"},
                                     {"tzAProp2": "tzAVal2"}]}
        ms._attrs = {
            "aField": "abc123",
            "a_vo": {"aProp": "aVal"},
            "a_list_vo": [{"aProp1": "aVal1"}, {"aProp2": "aVal2"}],
        }

        ms._extractVOs()

        self.assertEqual(ms.a_vo.__class__.__name__, "MambuValueObject")
        self.assertEqual(ms.a_vo._tzattrs, {"hello": "world"})
        for ind, elem in enumerate(ms.a_list_vo):
            self.assertEqual(elem.__class__.__name__, "MambuValueObject")
        self.assertEqual(ms.a_list_vo[0]._tzattrs, {"tzAProp1": "tzAVal1"})
        self.assertEqual(ms.a_list_vo[1]._tzattrs, {"tzAProp2": "tzAVal2"})

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
        ms._tzattrs = {"a_vo": {}, "a_list_vo": [{}, {}]}
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
            "Treebeard", "Quickbeam", "Beechbone", "Old Man Willow", "Grey Willow"]

        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "entities.MambuEntity", "an_ent"),
                        ("a_list_ent_keys", "entities.MambuEntity", "ents"),
                        ("a_dict_ent_key", "entities.MambuEntity", "huorns"),
                        ("a_dict_ent_key_id", "entities.MambuEntity", "a_huorn"),
                        ("an_alien_dict_ent", "entities.MambuEntity", "bombadil")]
        ms._attrs = {
            "aField": "abc123",
            "an_ent_key": "abcdef12345",
            "a_list_ent_keys": ["fedcba6789", "02468acebdf"],
            "a_dict_ent_key": {"encodedKey": "fedcba54321"},
            "a_dict_ent_key_id": {"id": "12345"},
            "an_alien_dict_ent": {"something": "in the way"},
        }

        self.assertEqual(
            ms._assignEntObjs(),
            ["Treebeard",
             ["Quickbeam", "Beechbone"],
             "Old Man Willow",
             "Grey Willow"])
        self.assertEqual(mock_import.call_count, 5)
        mock_import.assert_any_call(".entities", "mambupy.api")
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 5)
        mock_import().MambuEntity.get.assert_any_call(
            "abcdef12345", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba6789", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "02468acebdf", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba54321", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import().MambuEntity.get.assert_any_call(
            "12345", detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])
        self.assertEqual(ms.huorns, "Old Man Willow")
        self.assertEqual(ms.a_huorn, "Grey Willow")

        # optional arguments
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        del ms._attrs["huorns"]
        del ms._attrs["a_huorn"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone", "Old Man Willow", "Grey Willow"]
        mock_import.reset_mock()
        ms._assignEntObjs(detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "abcdef12345", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba6789", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "02468acebdf", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "fedcba54321", detailsLevel="FULL", get_entities=True, debug=True)
        mock_import().MambuEntity.get.assert_any_call(
            "12345", detailsLevel="FULL", get_entities=True, debug=True)

        # explicit entities list argument
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        del ms._attrs["huorns"]
        del ms._attrs["a_huorn"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone"]
        mock_import.reset_mock()
        ents = ms._assignEntObjs([
            ("an_ent_key", "entities.MambuEntity", "an_ent"),
            ("a_list_ent_keys", "entities.MambuEntity", "ents")])
        self.assertEqual(ents, ["Treebeard", ["Quickbeam", "Beechbone"]])
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])

        # invalid entity key as argument
        del ms._attrs["an_ent"]
        del ms._attrs["ents"]
        mock_import.return_value.MambuEntity.get.side_effect = [
            "Treebeard", "Quickbeam", "Beechbone", "Old Man Willow", "Grey Willow"]
        mock_import.reset_mock()
        ents = ms._assignEntObjs([
            ("an_INVALID_ent_key", "entities.MambuEntity", "an_ent")])
        self.assertEqual(ents, [])
        self.assertEqual(mock_import.call_count, 1)
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 0)

        # get doesn't supports detailsLevel argument
        mock_import.return_value.MambuEntity.get.side_effect = [
            TypeError(""), "Treebeard",
            TypeError(""), "Quickbeam",
            TypeError(""), "Beechbone",
            TypeError(""), "Old Man Willow",
            TypeError(""), "Grey Willow"]
        mock_import.reset_mock()
        ents = ms._assignEntObjs()
        self.assertEqual(
            ents,
            ["Treebeard", ["Quickbeam", "Beechbone"], "Old Man Willow", "Grey Willow"])
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "abcdef12345", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "fedcba6789", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "02468acebdf", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "fedcba54321", get_entities=False, debug=False)
        mock_import.return_value.MambuEntity.get.assert_any_call(
            "12345", get_entities=False, debug=False)
        self.assertEqual(mock_import.call_count, 5)
        self.assertEqual(mock_import.return_value.MambuEntity.get.call_count, 10)
        self.assertEqual(ms.an_ent, "Treebeard")
        self.assertEqual(ms.ents, ["Quickbeam", "Beechbone"])

        # invalid import, assigns None to property
        mock_import.return_value.invalid_class.get.side_effect = AttributeError("")
        ms = mambustruct.MambuStruct()
        ms._entities = [("an_ent_key", "invalid_class", "an_ent")]
        ms._attrs = {
            "an_ent_key": "abcdef12345",
        }
        self.assertEqual(ms._assignEntObjs(), [None])
        self.assertEqual(ms.an_ent, None)

    @mock.patch("MambuPy.api.mambustruct.import_module")
    def test__assignEntObjs_customfields(self, mock_import):
        ms = mambustruct.MambuStruct(cf_class=entities.MambuEntityCF)
        ms._entities = []
        ms._attrs = {
            "a_custom_field": "def456",
            "a_custom_field_ek": entities.MambuEntityCF("abc123"),
            "a_grouped_custom_field_ek": entities.MambuEntityCF(
                [{"field": "ghi789"}], "a_grouped_custom_field_ek", "GROUPED",
            ),
            "field_0": entities.MambuEntityCF(
                "ghi789", "/_a_grouped_custom_field_ek/0/field"),
        }

        self.assertEqual(
            ms._assignEntObjs(
                entities=[
                    ("a_custom_field", "mambuuser.MambuUser", "a_custom_field"),
                    ("a_custom_field_ek", "mambugroup.MambuGroup", "a_custom_field_ek"),
                    (
                        "a_grouped_custom_field_ek/0/field",
                        "mambuclient.MambuClient",
                        "a_grouped_custom_field_ek/0/field",
                    ),
                ]
            ),
            [
                mock_import.return_value.MambuUser.get.return_value,
                mock_import.return_value.MambuGroup.get.return_value,
                mock_import.return_value.MambuClient.get.return_value,
            ],
        )
        self.assertEqual(
            ms._attrs["field_0"].value,
            mock_import.return_value.MambuClient.get.return_value)
        mock_import.return_value.MambuUser.get.assert_called_once_with(
            "def456", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import.return_value.MambuGroup.get.assert_called_once_with(
            "abc123", detailsLevel="BASIC", get_entities=False, debug=False)
        mock_import.return_value.MambuClient.get.assert_called_once_with(
            "ghi789", detailsLevel="BASIC", get_entities=False, debug=False)

        # some field from grouped CF, updates also field at index in group
        mock_import.return_value.MambuClient.get.reset_mock()
        ms = mambustruct.MambuStruct(cf_class=entities.MambuEntityCF)
        ms._entities = []
        ms._attrs = {
            "a_grouped_custom_field_ek": entities.MambuEntityCF(
                [{"field": "ghi789"}], "a_grouped_custom_field_ek", "GROUPED",
            ),
            "field_0": entities.MambuEntityCF(
                "ghi789", "/_a_grouped_custom_field_ek/0/field"),
        }
        self.assertEqual(
            ms._assignEntObjs(
                entities=[("field_0", "mambuclient.MambuClient", "field_0")]),
            [mock_import.return_value.MambuClient.get.return_value]
        )
        self.assertEqual(
            ms._attrs["a_grouped_custom_field_ek"].value[0]["field"],
            mock_import.return_value.MambuClient.get.return_value)
        mock_import.return_value.MambuClient.get.assert_called_once_with(
            "ghi789", detailsLevel="BASIC", get_entities=False, debug=False)

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._assignEntObjs")
    def test_getEntities(self, mock_assign):
        mock_assign.return_value = "MY ENTITY"
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

        self.assertEqual(ms.getEntities(["an_ent"]), "MY ENTITY")
        mock_assign.assert_called_with(
            entities=[("an_ent_key", "entities.MambuEntity", "an_ent")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)
        self.assertEqual(mock_assign.call_count, 1)

        # with alternative config_entities
        mock_assign.reset_mock()
        ents = ms.getEntities(
            ["other_ent"],
            config_entities=[
                ("other_ent_key", "entities.MambuEntity", "other_ent")])
        self.assertEqual(ents, "MY ENTITY")
        mock_assign.assert_called_with(
            entities=[("other_ent_key", "entities.MambuEntity", "other_ent")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)
        self.assertEqual(mock_assign.call_count, 1)

        # optional arguments
        mock_assign.reset_mock()
        ents = ms.getEntities(
            ["ents"], detailsLevel="FULL", get_entities=True, debug=True)
        self.assertEqual(ents, "MY ENTITY")
        mock_assign.assert_called_with(
            entities=[("a_list_ent_keys", "entities.MambuEntity", "ents")],
            detailsLevel="FULL",
            get_entities=True,
            debug=True)
        self.assertEqual(mock_assign.call_count, 1)

        # entities for items in a list
        mock_assign.reset_mock()
        ents = ms.getEntities(["lost_entwives"])
        self.assertEqual(
            ents,
            [ms.lost_entwives[0]._assignEntObjs.return_value,
             ms.lost_entwives[1]._assignEntObjs.return_value])
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
        my_cf = mambucustomfield.MambuCustomField(**{"type": "CLIENT_LINK"})
        int_cf = mambucustomfield.MambuCustomField(**{"type": "Number"})
        ms = mambustruct.MambuStruct(cf_class=entities.MambuEntityCF)
        ms._entities = [("an_ent_key", "entities.MambuEntity", "an_ent")]
        ms._attrs = {
            "aField": "abc123",
            "an_ent_key": "abcdef12345",
            "a_custom_field": entities.MambuEntityCF(
                "value", "_a_custom_field_set/a_custom_field"),
            "linked_cf": entities.MambuEntityCF(
                "abcdef12345", "_a_custom_field_set/linked_cf", mcf=my_cf),
            "grouped_cf": entities.MambuEntityCF([
                {"field": 123, "ek": "abcdef12345"},
                {"field": 456, "ek": "fedcba67890"},
            ],
                "_other_custom_field_set/grouped_cf",
                "GROUPED",
                mcf={"field": int_cf, "ek": my_cf},
            ),
        }

        # get a func to get an entity from default config
        self.assertEqual(inspect.isfunction(ms.get_an_ent), True)
        self.assertEqual(
            inspect.getsource(ms.get_an_ent).strip(),
            "return lambda **kwargs: self.getEntities([ent], **kwargs)[0]")
        ms.get_an_ent()
        mock_assign.assert_called_with(
            entities=[("an_ent_key", "entities.MambuEntity", "an_ent")],
            detailsLevel="BASIC",
            get_entities=False,
            debug=False)

        # get a func to get an entity from a normal customfield
        mock_assign.reset_mock()
        with mock.patch(
                "MambuPy.api.mambucustomfield.MambuCustomField.get"
        ) as mock_get_mcf:
            self.assertEqual(inspect.isfunction(ms.get_a_custom_field), True)
            self.assertEqual(
                inspect.getsource(ms.get_a_custom_field).strip(),
                "return lambda **kwargs: value")
            ms.get_a_custom_field()
            self.assertEqual(mock_assign.call_count, 0)
            mock_get_mcf.assert_called_with("a_custom_field")

        # get a func to get an entity from a linked customfield
        mock_assign.reset_mock()
        with mock.patch(
                "MambuPy.api.mambucustomfield.MambuCustomField.get"
        ) as mock_get_mcf:
            self.assertEqual(inspect.isfunction(ms.get_linked_cf), True)
            self.assertEqual(
                inspect.getsource(ms.get_linked_cf).strip(),
                """return lambda **kwargs: self.getEntities(
                [ent], config_entities=[(ent, classpath, ent)], **kwargs
            )[0]""")
            ms.get_linked_cf()
            mock_assign.assert_called_with(
                entities=[("linked_cf", "mambuclient.MambuClient", "linked_cf")],
                detailsLevel="BASIC",
                get_entities=False,
                debug=False)
            self.assertEqual(mock_get_mcf.call_count, 0)

        # get a func to get a entities from grouped linked customfields
        mock_assign.reset_mock()
        with mock.patch(
            "MambuPy.api.mambucustomfield.MambuCustomField.get"
        ) as mock_get_mcf:
            self.assertEqual(inspect.isfunction(ms.get_grouped_cf), True)
            self.assertEqual(
                inspect.getsource(ms.get_grouped_cf).strip(),
                """return lambda **kwargs: attributes""")
            ms.get_grouped_cf()
            mock_assign.assert_called_with(
                entities=[
                    ("grouped_cf/1/ek", "mambuclient.MambuClient", "grouped_cf/1/ek")],
                detailsLevel="BASIC",
                get_entities=False,
                debug=False)
            self.assertEqual(mock_get_mcf.call_count, 0)

        # get a func to get any property's value
        mock_assign.reset_mock()
        self.assertEqual(inspect.isfunction(ms.get_aField), True)
        self.assertEqual(
            inspect.getsource(ms.get_aField).strip(),
            "return lambda **kwargs: entity")
        self.assertEqual(ms.get_aField(), "abc123")
        self.assertEqual(mock_assign.call_count, 0)

        # normal getattribute
        self.assertEqual(ms.aField, "abc123")
        with self.assertRaises(AttributeError):
            ms.some_unexistent_property


if __name__ == "__main__":
    unittest.main()
