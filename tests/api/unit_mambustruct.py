import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambustruct


class MagicMethodsTests(unittest.TestCase):
    def test___getitem__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms["hello"], "world")

        with self.assertRaises(KeyError):
            ms["goodbye"]

    def test___setitem__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {}  # should be automatically created?
        ms["hello"] = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})

    def test___delitem__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}
        del ms["hello"]
        self.assertEqual(ms._attrs, {})

    def test___str__(self):
        ms = mambustruct.MambuJsonObj()

        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(str(ms), "MambuJsonObj - {'id': '12345', 'hello': 'world'}")

        del ms._attrs
        ms.entid = "12345"
        self.assertEqual(str(ms), "MambuJsonObj - id: '12345' (not synced with Mambu)")

    def test___repr__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"id": "12345"}
        self.assertEqual(repr(ms), "MambuJsonObj - id: 12345")

        ms._attrs = {}
        self.assertEqual(repr(ms), "MambuJsonObj (no standard entity)")

        del ms._attrs
        ms.entid = "12345"
        self.assertEqual(repr(ms), "MambuJsonObj - id: '12345' (not synced with Mambu)")

        ms._attrs = [1, 2, 3, 4, 5]
        self.assertEqual(repr(ms), "MambuJsonObj - len: 5")

    def test___eq__(self):
        ms1 = mambustruct.MambuJsonObj()
        self.assertEqual("123" == ms1, None)
        self.assertEqual(ms1 == "123", None)

        ms2 = mambustruct.MambuJsonObj()
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

    def test___hash__(self):
        ms = mambustruct.MambuJsonObj()
        ms.encodedKey = "abc123"
        self.assertEqual(hash(ms), hash("abc123"))

        ms = mambustruct.MambuJsonObj()
        ms.id = "123"
        self.assertEqual(hash(ms), hash("MambuJsonObj123"))

        ms = mambustruct.MambuJsonObj()
        ms._attrs = {}
        self.assertEqual(hash(ms), hash("MambuJsonObj (no standard entity)"))

    def test___len__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(len(ms), 2)
        ms._attrs = {"id": "12345"}
        self.assertEqual(len(ms), 1)
        ms._attrs = [1, 2, 3, 4, 5]
        self.assertEqual(len(ms), 5)

    def test___contains__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual("hello" in ms, True)

    def test_get(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(ms.get("hello"), "world")

        ms._attrs = []
        with self.assertRaises(NotImplementedError):
            ms.get("hello")

    def test_keys(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.keys()), ["hello"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.keys()

    def test_items(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.items()), [("hello", "world")])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.items()

    def test_values(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.values()), ["world"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.values()

    def test___getattribute__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms._attrs, {"hello": "world"})
        self.assertEqual(ms.hello, "world")

        with self.assertRaises(AttributeError):
            ms.some_unexistent_property

    def test___setattribute__(self):
        ms = mambustruct.MambuJsonObj()
        ms._attrs = {}
        ms.hello = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})
        ms.hello = "goodbye"
        self.assertEqual(ms._attrs, {"hello": "goodbye"})

        setattr(ms, "property", "value")
        ms.property = "othervalue"
        self.assertEqual(getattr(ms, "property"), "othervalue")

        ms = mambustruct.MambuJsonObj()
        ms._attrs = []
        ms.goodbye = "cruelworld"
        self.assertEqual(getattr(ms, "goodbye"), "cruelworld")

    def test_has_key(self):
        ms = mambustruct.MambuJsonObj()

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
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._connector")
    def test_connect(self, mock_connector):
        mock_connector.mambu_get.return_value = b'{"encodedKey":"abc123","id":"12345"}'

        ms = mambustruct.MambuStruct()
        ms.__dict__["_url_prefix"] = "un_url_prefix"
        ms._attrs = {}
        ms.connect("12345")

        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector.mambu_get.assert_called_with(
            "12345", url_prefix="un_url_prefix")


if __name__ == "__main__":
    unittest.main()
