import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambucentre
from MambuPy.mambuutil import MambuPyError


class MambuCentre(unittest.TestCase):
    def test_implements_interfaces(self):
        mc = mambucentre.MambuCentre()
        self.assertTrue(isinstance(mc, mambucentre.MambuEntity))

    def test_has_properties(self):
        mc = mambucentre.MambuCentre()
        self.assertEqual(mc._prefix, "centres")
        self.assertEqual(
            mc._filter_keys,
            ["branchId"],
        )
        self.assertEqual(
            mc._sortBy_fields, ["creationDate", "lastModifiedDate", "id", "name"]
        )

    @mock.patch("MambuPy.api.mambustruct.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mb = mambucentre.MambuCentre.get_all()
        self.assertEqual(mb, "SupGetSeveral")

        mb = mambucentre.MambuCentre.get_all(filters={})
        self.assertEqual(mb, "SupGetSeveral")

        mb = mambucentre.MambuCentre.get_all(sortBy="id:ASC")
        self.assertEqual(mb, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambucentre.MambuCentre.get_all(filters={"centreId": "MyCentre", "Squad": "Red"})

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambucentre.MambuCentre.get_all(sortBy="field:ASC")

        mambucentre.MambuCentre._filter_keys = ["id"]
        mb = mambucentre.MambuCentre.get_all(filters={"id": "ASC"})
        self.assertEqual(mb, "SupGetSeveral")
        mambucentre.MambuCentre._filter_keys = ["branchId"]


if __name__ == "__main__":
    unittest.main()
