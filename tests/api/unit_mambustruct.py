import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
from MambuPy.api import mambustruct


class MagicMethodsTests(unittest.TestCase):
    def test___getitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms["hello"], "world")

        with self.assertRaises(KeyError):
            ms["goodbye"]

    def test___setitem__(self):
        ms = mambustruct.MambuMapObj()
        ms._attrs = {}  # should be automatically created?
        ms["hello"] = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})

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

        ms._attrs = {}
        self.assertEqual(repr(ms), "MambuMapObj (no standard entity)")

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
        ms._attrs = {}
        self.assertEqual(hash(ms), hash("MambuMapObj (no standard entity)"))

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

        self.child_class = child_class

    def test___get_several(self):
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

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_get(self, mock_connector):
        mock_connector.mambu_get.return_value = b'{"encodedKey":"abc123","id":"12345"}'

        ms = self.child_class.get("12345")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", url_prefix="un_prefix", detailsLevel="BASIC")

        ms = self.child_class.get("12345", "FULL")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", url_prefix="un_prefix", detailsLevel="FULL")

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

    def test_convertDict2Attrs(self):
        """Test conversion of dictionary elements (strings) in to proper datatypes"""
        ms = mambustruct.MambuStruct()
        ms._attrs = {"aStr": "abc123",
                     "aNum": "123",
                     "trailZeroes": "00123",
                     "aFloat": "15.56",
                     "aDate": "2021-10-23T10:36:00-06:00",
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

        ms.convertDict2Attrs()

        # string remains string
        self.assertEqual(ms.aStr, "abc123")

        # integer transforms in to int
        self.assertEqual(ms.aNum, 123)

        # integer with trailing 0's remains as string
        self.assertEqual(ms.trailZeroes, "00123")

        # floating point transforms in to float
        self.assertEqual(ms.aFloat, 15.56)

        # datetime transforms in to datetime object
        from datetime import datetime
        self.assertEqual(ms.aDate, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"))

        # lists recursively convert each of its elements
        self.assertEqual(
            ms.aList,
            ["abc123", 123, "00123", 15.56, datetime.strptime("2021-10-23 10:36:00", "%Y-%m-%d %H:%M:%S"), [123], {"key": 123}],
        )

        # dictonaries recursively convert each of its elements
        ms.convertDict2Attrs()
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
            "emailAddress": "111",
            "description": "000",
            "someKey": "0123",
            }
        ms._attrs = {}
        for key, val in data.items():
            ms._attrs[key] = val
        ms.convertDict2Attrs()

        for key, val in ms._attrs.items():
            self.assertEqual(val, data[key])


if __name__ == "__main__":
    unittest.main()
