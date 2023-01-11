import json
import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.mambuutil import (MambuError, MambuPyError)


class MambuWritableEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class_writable(
            entities.MambuEntity, entities.MambuEntityWritable
        ):
            _prefix = "un_prefix"
            _connector = mock.Mock()

            def __init__(self, **kwargs):
                super().__init__(connector=self._connector, **kwargs)
                self._attrs = {"id": "12345"}

        self.child_class_writable = child_class_writable

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractVOs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._extractCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    def test_update(
        self,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
        mock_extractCustomFields,
        mock_extractVOs
    ):
        child = self.child_class_writable()
        mock_connector = child._connector
        mock_connector.mambu_update.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""

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
    def test_create(
        self,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
        mock_extractCustomFields,
        mock_extractVOs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_connector.mambu_create.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_add(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/myProp"

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

        mock_connector.mambu_patch.reset_mock()
        mock_efp.return_value = ""
        with self.assertRaisesRegex(
                MambuPyError, r'^You cannot patch myProp field$'
        ):
            child.patch(["myProp"])
        self.assertEqual(mock_connector.mambu_patch.call_count, 0)

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_replace(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_remove(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_add_cf_standard(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/_myCFSet/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_replace_cf_standard(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        mock_efp.return_value = "/_myCFSet/myProp"

        child = self.child_class_writable()
        mock_connector = child._connector

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_remove_cf_standard(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/_myCFSet/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_add_cf_grouped(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/_myCFSet/0/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_replace_cf_grouped(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/_myCFSet/1/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_remove_cf_grouped(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        mock_efp.return_value = "/_myCFSet/0/myProp"

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
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_exceptions(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

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

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._serializeFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateCustomFields")
    @mock.patch("MambuPy.api.mambustruct.MambuStruct._updateVOs")
    @mock.patch("MambuPy.api.entities.MambuEntity._extract_field_path")
    def test_patch_empty(
        self,
        mock_efp,
        mock_updateVOs,
        mock_updateCustomFields,
        mock_serializeFields,
        mock_convertDict2Attrs,
    ):
        child = self.child_class_writable()
        mock_connector = child._connector

        child._resp = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","myProp":"myVal"
        }"""
        child._attrs = dict(json.loads(child._resp))
        child._attrs["myProp"] = "myVal2"

        child.patch([])

        self.assertEqual(mock_connector.mambu_patch.call_count, 0)
        mock_updateVOs.assert_called_once_with()
        mock_updateCustomFields.assert_called_once_with()
        mock_serializeFields.assert_called_once_with()
        mock_convertDict2Attrs.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
