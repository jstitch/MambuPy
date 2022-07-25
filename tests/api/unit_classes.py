import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import classes, entities


class MagicMethodsTests(unittest.TestCase):
    def test___init__(self):
        ms = classes.MambuMapObj(some="value")
        self.assertEqual(ms._attrs, {"some": "value"})

    def test___getitem__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms["hello"], "world")

    def test___getitem__CF(self):
        ms = classes.MambuMapObj(cf_class=entities.MambuEntityCF)
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
        ms = classes.MambuMapObj()
        ms._attrs = {}  # should be automatically created?
        ms["hello"] = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})

    def test___setitem__CF(self):
        ms = classes.MambuMapObj(cf_class=entities.MambuEntityCF)
        cf = entities.MambuEntityCF("world")
        ms._attrs = {"hello": cf}

        ms["hello"] = "goodbye"
        self.assertEqual(
            ms._attrs["hello"]._attrs,
            {"value": "goodbye", "path": "", "type": "STANDARD"},
        )

    def test___delitem__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}
        del ms["hello"]
        self.assertEqual(ms._attrs, {})

    def test___str__(self):
        ms = classes.MambuMapObj()

        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(str(ms), "MambuMapObj - {'id': '12345', 'hello': 'world'}")

        del ms._attrs
        ms.entid = "12345"
        self.assertEqual(str(ms), "MambuMapObj - id: '12345' (not synced with Mambu)")

    def test___repr__(self):
        ms = classes.MambuMapObj()
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
        ms1 = classes.MambuMapObj()
        self.assertEqual("123" == ms1, None)
        self.assertEqual(ms1 == "123", None)

        ms2 = classes.MambuMapObj()
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
        r = classes.MambuMapObj.__eq__(ms, ms1)
        self.assertEqual(r, NotImplemented)

    def test___hash__(self):
        ms = classes.MambuMapObj()
        ms.encodedKey = "abc123"
        self.assertEqual(hash(ms), hash("abc123"))

        ms = classes.MambuMapObj()
        ms.id = "123"
        self.assertEqual(hash(ms), hash("MambuMapObj123"))

        ms = classes.MambuMapObj()
        ms._attrs = {"what": "th?"}
        self.assertEqual(hash(ms), hash("MambuMapObj - {'what': 'th?'}"))

    def test___len__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"id": "12345", "hello": "world"}
        self.assertEqual(len(ms), 2)
        ms._attrs = {"id": "12345"}
        self.assertEqual(len(ms), 1)
        ms._attrs = [1, 2, 3, 4, 5]
        self.assertEqual(len(ms), 5)

    def test___contains__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual("hello" in ms, True)

    def test_get(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(ms.get("hello"), "world")

        ms._attrs = []
        with self.assertRaises(NotImplementedError):
            ms.get("hello")

    def test_keys(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.keys()), ["hello"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.keys()

    def test_items(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.items()), [("hello", "world")])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.items()

    def test_values(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}

        self.assertEqual(list(ms.values()), ["world"])

        del ms._attrs
        with self.assertRaises(NotImplementedError):
            ms.values()

    def test___getattribute__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms._attrs, {"hello": "world"})
        self.assertEqual(ms.hello, "world")

        with self.assertRaises(AttributeError):
            ms.some_unexistent_property

    def test___getattribute__CF(self):
        cf = entities.MambuEntityCF("world")
        ms = classes.MambuMapObj(cf_class=entities.MambuEntityCF)
        ms._attrs = {"hello": cf}
        self.assertEqual(ms["hello"], "world")
        self.assertEqual(
            ms._attrs["hello"]._attrs, {"value": "world", "path": "", "type": "STANDARD"}
        )
        self.assertEqual(ms.hello, "world")

    def test___setattribute__(self):
        ms = classes.MambuMapObj()
        ms._attrs = {}
        ms.hello = "world"
        self.assertEqual(ms._attrs, {"hello": "world"})
        ms.hello = "goodbye"
        self.assertEqual(ms._attrs, {"hello": "goodbye"})

        setattr(ms, "property", "value")
        ms.property = "othervalue"
        self.assertEqual(getattr(ms, "property"), "othervalue")

        ms = classes.MambuMapObj()
        ms._attrs = []
        ms.goodbye = "cruelworld"
        self.assertEqual(getattr(ms, "goodbye"), "cruelworld")

    def test___setattribute__CF(self):
        cf = entities.MambuEntityCF("world")
        ms = classes.MambuMapObj(cf_class=entities.MambuEntityCF)
        ms._attrs = {"hello": cf}

        ms.hello = "goodbye"
        self.assertEqual(
            ms._attrs["hello"]._attrs,
            {"value": "goodbye", "path": "", "type": "STANDARD"},
        )

    def test_has_key(self):
        ms = classes.MambuMapObj()

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


if __name__ == "__main__":
    unittest.main()
