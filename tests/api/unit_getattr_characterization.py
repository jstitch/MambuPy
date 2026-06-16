"""Characterization tests for the attribute-access contract.

These capture the OBSERVABLE behavior of MambuMapObj.__getattribute__ and
MambuStruct.__getattribute__ BEFORE migrating them to __getattr__, focused on
the edge cases that migration could alter:

  - shadowing: a real method/attribute sharing a name with an _attrs key must win
  - precedence: reading an _attrs key as an attribute (no get_ prefix)
  - dynamic get_* vs raw read
  - missing dunders / copy.deepcopy / pickle must raise a clean AttributeError
  - an _attrs list must not trigger the "magic"
  - hasattr / getattr(.., default)

If any of these fails against the CURRENT code, it reveals an undocumented
contract worth knowing before touching anything.
"""
import copy
import os
import pickle
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import classes, entities, mambustruct  # noqa: E402


class MambuMapObjCharacterization(unittest.TestCase):
    def test_real_method_shadows_attrs_key(self):
        # 'keys' is a real method of MambuMapObj; an _attrs key with the same
        # name must NOT shadow it on attribute access.
        ms = classes.MambuMapObj()
        ms._attrs = {"keys": "i_am_data"}
        self.assertTrue(callable(ms.keys), "the real method must win over _attrs")
        # but dict notation does return the data
        self.assertEqual(ms["keys"], "i_am_data")

    def test_attrs_key_read_as_attribute(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"hello": "world"}
        self.assertEqual(ms.hello, "world")
        self.assertEqual(ms.hello, ms["hello"])  # object/dict duality

    def test_attrs_as_list_no_magic(self):
        ms = classes.MambuMapObj()
        ms._attrs = []
        with self.assertRaises(AttributeError):
            ms.anything

    def test_missing_attribute_raises(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"x": 1}
        with self.assertRaises(AttributeError):
            ms.some_unexistent_property

    def test_hasattr_and_getattr_default(self):
        ms = classes.MambuMapObj()
        ms._attrs = {"x": 1}
        self.assertTrue(hasattr(ms, "x"))
        self.assertFalse(hasattr(ms, "nope"))
        self.assertEqual(getattr(ms, "nope", "default"), "default")

    def test_deepcopy_object(self):
        # deepcopying the OBJECT (not just _attrs) exercises dunders via access
        ms = classes.MambuMapObj(some="value")
        dc = copy.deepcopy(ms)
        self.assertIsNot(dc, ms)
        self.assertEqual(dc["some"], "value")

    def test_pickle_object(self):
        ms = classes.MambuMapObj(some="value")
        restored = pickle.loads(pickle.dumps(ms))
        self.assertEqual(restored["some"], "value")


class MambuStructCharacterization(unittest.TestCase):
    def _make(self):
        ms = mambustruct.MambuStruct(cf_class=entities.MambuEntityCF)
        ms._entities = []
        ms._attrs = {"aField": "abc123"}
        return ms

    def test_attrs_key_without_get_prefix_returns_value(self):
        # without the get_ prefix, the raw _attrs value is returned (not a getter)
        ms = self._make()
        self.assertEqual(ms.aField, "abc123")

    def test_get_prefix_builds_callable(self):
        # with the get_ prefix, a getter (function) is built
        ms = self._make()
        self.assertTrue(callable(ms.get_aField))

    def test_missing_attribute_raises(self):
        ms = self._make()
        with self.assertRaises(AttributeError):
            ms.some_unexistent_property

    def test_dunder_missing_raises_clean(self):
        # a missing dunder must NOT fall into the get_ magic; it must raise
        ms = self._make()
        with self.assertRaises(AttributeError):
            ms.__totally_missing_dunder__

    def test_deepcopy_object(self):
        ms = self._make()
        dc = copy.deepcopy(ms)
        self.assertIsNot(dc, ms)
        self.assertEqual(dc.aField, "abc123")

    def test_hasattr_default(self):
        ms = self._make()
        self.assertTrue(hasattr(ms, "aField"))
        self.assertFalse(hasattr(ms, "nope"))
        self.assertEqual(getattr(ms, "nope", "default"), "default")


if __name__ == "__main__":
    unittest.main()
