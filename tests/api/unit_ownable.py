import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities


class MambuOwnableEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class_ownable(
            entities.MambuEntity, entities.MambuEntityOwnable
        ):
            _prefix = "un_prefix"
            _entities = []

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._attrs = {"id": "12345"}
                self._entities = [("accountHolderKey", "", "accountHolder")]

        self.child_class_ownable = child_class_ownable

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._assignEntObjs")
    def test__assignEntObjs(self, mock_assign):
        # link type CLIENT
        mc = self.child_class_ownable()
        mc._attrs = {
            "accountHolderKey": "09876fedcba",
            "accountHolderType": "CLIENT",
        }

        self.assertEqual(mc._assignEntObjs(), mock_assign.return_value)
        mock_assign.assert_any_call(
            mc._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mc._entities[-1],
            ("accountHolderKey", "mambuclient.MambuClient", "accountHolder"))

        # link type GROUP
        mock_assign.reset_mock()
        mc = self.child_class_ownable()
        mc._attrs = {
            "accountHolderKey": "09876fedcba",
            "accountHolderType": "GROUP",
        }

        self.assertEqual(mc._assignEntObjs(), mock_assign.return_value)
        mock_assign.assert_any_call(
            mc._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mc._entities[-1],
            ("accountHolderKey", "mambugroup.MambuGroup", "accountHolder"))

        # link type INVALID
        mock_assign.reset_mock()
        mc = self.child_class_ownable()
        mc._attrs = {
            "accountHolderKey": "09876fedcba",
            "accountHolderType": "",
        }

        self.assertEqual(mc._assignEntObjs(), mock_assign.return_value)
        mock_assign.assert_any_call(
            mc._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mc._entities[-1],
            ("accountHolderKey", "", "accountHolder"))

        # custom entities
        mock_assign.reset_mock()
        mc = self.child_class_ownable()
        mc._attrs = {
            "accountHolderKey": "09876fedcba",
            "accountHolderType": "",
        }
        self.assertEqual(
            mc._assignEntObjs([("accountHolderKey", "", "accountHolder")]),
            mock_assign.return_value)
        mock_assign.assert_any_call(
            [("accountHolderKey", "", "accountHolder")],
            detailsLevel="BASIC",
            get_entities=False, debug=False)
        self.assertEqual(
            mc._entities[-1],
            ("accountHolderKey", "", "accountHolder"))

        # not looking for account holder
        mock_assign.reset_mock()
        mc = self.child_class_ownable()
        mc._attrs = {
            "accountHolderKey": "09876fedcba",
            "accountHolderType": "",
        }
        self.assertEqual(mc._assignEntObjs([]), mock_assign.return_value)
        mock_assign.assert_any_call(
            [],
            detailsLevel="BASIC",
            get_entities=False, debug=False)


if __name__ == "__main__":
    unittest.main()
