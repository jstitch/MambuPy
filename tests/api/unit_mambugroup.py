import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambugroup
from MambuPy.mambuutil import MambuPyError


class MambuGroup(unittest.TestCase):
    def test_implements_interfaces(self):
        mg = mambugroup.MambuGroup()
        self.assertTrue(isinstance(mg, mambugroup.MambuEntity))
        self.assertTrue(isinstance(mg, interfaces.MambuWritable))
        self.assertTrue(isinstance(mg, interfaces.MambuAttachable))
        self.assertTrue(isinstance(mg, interfaces.MambuSearchable))

    def test_has_properties(self):
        mg = mambugroup.MambuGroup()
        self.assertEqual(mg._prefix, "groups")
        self.assertEqual(
            mg._filter_keys, ["branchId", "centreId", "creditOfficerUsername"]
        )
        self.assertEqual(
            mg._sortBy_fields, ["creationDate", "lastModifiedDate", "groupName"]
        )
        self.assertEqual(mg._ownerType, "GROUP")
        self.assertEqual(mg._vos, [("addresses", "MambuAddress")])

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mg = mambugroup.MambuGroup.get_all()
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(filters={})
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(sortBy="groupName:ASC")
        self.assertEqual(mg, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambugroup.MambuGroup.get_all(
                filters={"branchId": "MyBranch", "Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambugroup.MambuGroup.get_all(sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
