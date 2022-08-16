import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mamburole
from MambuPy.mambuutil import MambuPyError


class MambuRole(unittest.TestCase):
    def test_implements_interfaces(self):
        mr = mamburole.MambuRole()
        self.assertTrue(isinstance(mr, mamburole.MambuEntity))
        self.assertTrue(isinstance(mr, mamburole.MambuEntityWritable))

    def test_has_properties(self):
        mr = mamburole.MambuRole()
        self.assertEqual(mr._prefix, "userroles")
        self.assertEqual(
            mr._filter_keys,
            [],
        )
        self.assertEqual(
            mr._sortBy_fields,
            [],
        )

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mr = mamburole.MambuRole.get_all()
        self.assertEqual(mr, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mamburole.MambuRole.get_all(
                filters={"EchoThree": "EchoSeven"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mamburole.MambuRole.get_all(sortBy="Han:DoYouReadMe?")


if __name__ == "__main__":
    unittest.main()
