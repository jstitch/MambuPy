import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambucustomfield
from MambuPy.mambuutil import MambuPyError


class MambuCustomField(unittest.TestCase):
    def test_implements_interfaces(self):
        mcf = mambucustomfield.MambuCustomField()
        self.assertTrue(isinstance(mcf, mambucustomfield.MambuEntity))

    def test_has_properties(self):
        mcf = mambucustomfield.MambuCustomField()
        self.assertEqual(mcf._prefix, "customfields")


class MambuCustomFieldSet(unittest.TestCase):
    def test_implements_interfaces(self):
        mcfs = mambucustomfield.MambuCustomFieldSet()
        self.assertTrue(isinstance(mcfs, mambucustomfield.MambuEntity))

    def test_has_properties(self):
        mcfs = mambucustomfield.MambuCustomFieldSet()
        self.assertEqual(mcfs._prefix, "customfieldsets")

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mcfs = mambucustomfield.MambuCustomFieldSet.get_all()
        self.assertEqual(mcfs, "SupGetSeveral")

        mcfs = mambucustomfield.MambuCustomFieldSet.get_all(availableFor="")
        self.assertEqual(mcfs, "SupGetSeveral")

        for afor in mambucustomfield.MambuCustomFieldSet._availableFor:
            mcfs = mambucustomfield.MambuCustomFieldSet.get_all(
                availableFor=afor)
            self.assertEqual(mcfs, "SupGetSeveral")

        with self.assertRaisesRegex(
                MambuPyError, r"^key something not in allowed _availableFor: "
        ):
            mambucustomfield.MambuCustomFieldSet.get_all(
                availableFor="something")

        with self.assertRaisesRegex(
                MambuPyError, r"^filters is not allowed on MambuCustomFieldSet$"
        ):
            mambucustomfield.MambuCustomFieldSet.get_all(filters={})

        with self.assertRaisesRegex(
                MambuPyError, r"^sortBy is not allowed on MambuCustomFieldSet$"
        ):
            mambucustomfield.MambuCustomFieldSet.get_all(sortBy="id:ASC")


if __name__ == "__main__":
    unittest.main()
