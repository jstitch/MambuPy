import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.mambuutil import (OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE,
                               MambuPyError)


class MambuConnectorTests(unittest.TestCase):
    def test_has_mambuconnector(self):
        ms = entities.MambuEntity()
        self.assertEqual(ms._connector.__class__.__name__, "MambuConnectorREST")


class MambuEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class(entities.MambuEntity):
            _prefix = "un_prefix"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}

        self.child_class = child_class
        self.child_class._assignEntObjs = mock.Mock()

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
