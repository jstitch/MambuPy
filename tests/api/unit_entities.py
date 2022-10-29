import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.mambuutil import MambuError, MambuPyError


class mock_mambucustomfieldset:
    def __init__(self, id, customFields=None):
        self.id = id
        if not customFields:
            self.customFields = []
        else:
            self.customFields = customFields


class MambuConnectorTests(unittest.TestCase):
    def test_has_mambuconnector(self):
        ms = entities.MambuEntity()
        self.assertEqual(ms._connector, None)


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

    def test__extract_field_path(self):
        with mock.patch(
                "MambuPy.api.mambucustomfield.MambuCustomFieldSet"
        ) as mock_mcf:
            me = entities.MambuEntity()
            me._mcfs = []
            me.aField = ""
            self.assertEqual(
                me._extract_field_path(
                    "aField", {"aField": "hello"}, {}, type),
                ""
            )
            self.assertEqual(
                me._extract_field_path(
                    "aField", {"aField": "hello"}, {"aField": "hello"}, type),
                "/aField"
            )

            myCF = entities.MambuEntityCF("aValue", path="/_mySet/myField")
            self.assertEqual(
                me._extract_field_path(
                    "myField",
                    {"myField": myCF},
                    {"myField": myCF},
                    entities.MambuEntityCF),
                "/_mySet/myField"
            )

            mock_mcf.get_all.return_value = [
                mock_mambucustomfieldset(
                    "_otherCFSet",
                    [{"id": "someAttrs"}, {"id": "otherAttrs"}, ]),
                mock_mambucustomfieldset("_myCFSet", [{"id": "myAttrs"}])
            ]
            me = entities.MambuEntity()
            me._ownerType = "MyType"
            me._attrs = {"myAttrs": "myProp"}
            me._cf_class = entities.MambuEntityCF
            self.assertEqual(
                me._extract_field_path("myAttrs"), "/_myCFSet/myAttrs")
            mock_mcf.get_all.assert_called_once_with(availableFor="MyType")

    @mock.patch("MambuPy.api.entities.print")
    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    def test__get_several(
        self,
        mock_extractVOs,
        mock_extractCustomFields,
        mock_convertDict2Attrs,
        mock_connector_rest,
        mock_print
    ):
        mock_func = mock.Mock()

        mock_func.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"},
        {"encodedKey":"ghi789","id":"54321"},
        {"encodedKey":"jkl012","id":"09876"}
        ]"""

        ms = self.child_class._get_several(
            mock_func, mock_connector_rest.return_value)

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
            mock_connector_rest.return_value,
            **{"prefix": "something else",
               "get_entities": True,
               "debug": True})
        mock_func.assert_called_with(
            "something else",
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
        self.child_class._get_several(
            mock_func, mock_connector_rest.return_value, detailsLevel="FULL")
        mock_func.assert_called_with("un_prefix", detailsLevel="FULL")

        self.child_class._get_several(
            mock_func, mock_connector_rest.return_value, offset=20, limit=2)
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
        self.child_class._get_several(
            mock_func, mock_connector_rest.return_value, limit=4)
        self.assertEqual(mock_func.call_count, 1)
        mock_func.assert_called_with("un_prefix", limit=4, detailsLevel="BASIC")

        entities.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

    @mock.patch("MambuPy.api.entities.print")
    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    def test_get(
        self,
        mock_extractVOs, mock_extractCustomFields, mock_convertDict2Attrs,
        mock_connector_rest,
        mock_print
    ):
        mock_connector = mock_connector_rest.return_value
        mock_connector.mambu_get.return_value = b'{"encodedKey":"abc123","id":"12345"}'

        ms = self.child_class.get(
            "12345", user="myuser", pwd="mypwd", url="myurl")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms._detailsLevel, "BASIC")
        mock_connector_rest.assert_called_with(
            user="myuser", pwd="mypwd", url="myurl")
        mock_connector_rest.return_value.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="BASIC"
        )
        mock_convertDict2Attrs.assert_called_once_with()
        mock_extractCustomFields.assert_called_once_with()
        mock_extractVOs.assert_called_once_with(
            get_entities=False, debug=False)

        ms = self.child_class.get("12345", "FULL")

        self.assertEqual(ms.__class__.__name__, "child_class")
        self.assertEqual(ms._attrs, {"encodedKey": "abc123", "id": "12345"})
        mock_connector_rest.return_value.mambu_get.assert_called_with(
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
    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    def test_refresh(
        self, mock_connector_rest,
        mock_extractVOs, mock_extractCustomFields, mock_convertDict2Attrs
    ):
        mock_connector_rest.return_value.mambu_get.return_value = (
            b'{"encodedKey":"abc123","id":"12345","someAttribute":"someValue"}'
        )
        ms = self.child_class.get("12345", detailsLevel="FULL")
        ms.test_prop = "testing"
        ms.someAttribute = "anotherValue"

        mock_connector_rest.return_value.reset_mock()
        ms.refresh()

        mock_connector_rest.return_value.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="FULL"
        )
        self.assertEqual(ms.test_prop, "testing")
        self.assertEqual(ms.someAttribute, "someValue")

        mock_connector_rest.return_value.reset_mock()
        ms.refresh(detailsLevel="BASIC")
        mock_connector_rest.return_value.mambu_get.assert_called_with(
            "12345", prefix="un_prefix", detailsLevel="BASIC"
        )

    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    def test_get_all(self, mock_connector_rest):
        mock_connector_rest.return_value.mambu_get_all.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]"""

        ms = self.child_class.get_all(user="myuser", pwd="mypwd", url="myurl")

        mock_connector_rest.assert_called_with(
            user="myuser", pwd="mypwd", url="myurl")
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

    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all_kwargs(self, mock_get_several, mock_connector_rest):
        self.child_class.get_all(**{"hello": "world"})
        mock_get_several.assert_any_call(
            mock_connector_rest.return_value.mambu_get_all,
            mock_connector_rest.return_value,
            filters=None,
            offset=None, limit=None,
            paginationDetails="OFF", detailsLevel="BASIC",
            sortBy=None,
            hello="world")


class MambuEntityCFTests(unittest.TestCase):
    def test___init__(self):
        ms = entities.MambuEntityCF("_VALUE_")
        self.assertEqual(
            ms._attrs,
            {"value": "_VALUE_", "path": "", "type": "STANDARD", "mcf": None})

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_")
        self.assertEqual(
            ms._attrs,
            {"value": "_VALUE_", "path": "_PATH_", "type": "STANDARD", "mcf": None}
        )

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_", "STANDARD")
        self.assertEqual(
            ms._attrs,
            {"value": "_VALUE_", "path": "_PATH_", "type": "STANDARD", "mcf": None}
        )

        ms = entities.MambuEntityCF("_VALUE_", "_PATH_", "GROUPED")
        self.assertEqual(
            ms._attrs,
            {"value": "_VALUE_", "path": "_PATH_", "type": "GROUPED", "mcf": None}
        )

        with self.assertRaisesRegex(MambuPyError, r"invalid CustomField type!"):
            entities.MambuEntityCF("_VALUE_", "_PATH_", "_TYPE_")

    @mock.patch("MambuPy.api.entities.import_module")
    def test_get_mcf(self, mock_import_module):
        mock_import_module().MambuCustomField.get.return_value = "My_MambuCF"

        ms = entities.MambuEntityCF("_VALUE_", "_a_cf_set/_a_cf", "STANDARD")

        ms.get_mcf()

        self.assertEqual(ms._attrs["mcf"], "My_MambuCF")
        mock_import_module.assert_called_with("MambuPy.api.mambucustomfield")
        mock_import_module().MambuCustomField.get.assert_called_with("_a_cf")
        self.assertEqual(mock_import_module().MambuCustomField.get.call_count, 1)

        ms.get_mcf()
        self.assertEqual(mock_import_module().MambuCustomField.get.call_count, 1)

        mock_import_module().MambuCustomField.get.side_effect = [
            "Other_MambuCF",
            MambuError,
        ]
        ms = entities.MambuEntityCF(
            [{"_KEY_": "_VALUE_", "_OTHER_": "_VAL_"}], "_a_cf_set/_a_cf", "GROUPED"
        )

        ms.get_mcf()

        self.assertEqual(ms._attrs["mcf"], {"_KEY_": "Other_MambuCF", "_OTHER_": None})


if __name__ == "__main__":
    unittest.main()
