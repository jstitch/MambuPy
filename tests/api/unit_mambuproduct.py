import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambuproduct
from MambuPy.mambuutil import MambuPyError


class MambuProduct(unittest.TestCase):
    def setUp(self):
        class child_class(mambuproduct.MambuProduct):
            id = "12345"
        self.child_class = child_class

    def test_implements_interfaces(self):
        mp = mambuproduct.MambuProduct()
        self.assertTrue(isinstance(mp, mambuproduct.MambuEntity))
        self.assertTrue(isinstance(mp, interfaces.MambuWritable))
        self.assertTrue(isinstance(mp, interfaces.MambuAttachable))

    def test_has_properties(self):
        mc = mambuproduct.MambuProduct()
        self.assertEqual(mc._prefix, "loanproducts")
        self.assertEqual(
            mc._filter_keys,
            [
            ],
        )
        self.assertEqual(
            mc._sortBy_fields,
            ["creationDate", "lastModifiedDate", "id", "productName"],
        )
        self.assertEqual(mc._ownerType, "LOAN_PRODUCT")

    @mock.patch("MambuPy.api.entities.MambuEntity.get")
    def test_get(self, mock_get):
        mock_get.return_value = "SupGet"

        mp = mambuproduct.MambuProduct.get(entid="MY PRODUCT")
        self.assertEqual(mp, "SupGet")
        mock_get.assert_called_once_with(
            "MY PRODUCT", detailsLevel="FULL")

        with self.assertRaises(TypeError):
            mambuproduct.MambuProduct.get(detailsLevel="BASIC")

    @mock.patch("MambuPy.api.entities.MambuEntity.refresh")
    def test_refresh(self, mock_refresh):
        mock_refresh.return_value = "SupRefresh"

        mp = self.child_class()
        mp.refresh()
        mock_refresh.assert_called_once_with(detailsLevel="FULL")

        with self.assertRaises(TypeError):
            mp.refresh(detailsLevel="BASIC")

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mp = mambuproduct.MambuProduct.get_all()
        self.assertEqual(mp, "SupGetSeveral")

        with self.assertRaises(TypeError):
            mambuproduct.MambuProduct.get_all(detailsLevel="BASIC")

        mp = mambuproduct.MambuProduct.get_all(filters={})
        self.assertEqual(mp, "SupGetSeveral")

        mp = mambuproduct.MambuProduct.get_all(sortBy="productName:ASC")
        self.assertEqual(mp, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambuproduct.MambuProduct.get_all(
                filters={"Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambuproduct.MambuProduct.get_all(sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
