import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambutask
from MambuPy.mambuutil import MambuPyError


class MambuTask(unittest.TestCase):
    def test_implements_interfaces(self):
        mt = mambutask.MambuTask()
        self.assertTrue(isinstance(mt, mambutask.MambuEntity))
        self.assertTrue(isinstance(mt, mambutask.MambuEntityWritable))

    def test_has_properties(self):
        mt = mambutask.MambuTask()
        self.assertEqual(mt._prefix, "tasks")
        self.assertEqual(
            mt._filter_keys,
            [
             "username",
             "clientId",
             "groupId",
             "status",
            ],
        )
        self.assertEqual(
            mt._sortBy_fields,
            [],
        )
        self.assertEqual(
            mt._entities,
            [("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
             ("taskLinkKey", "", "taskLink")])

    @mock.patch("MambuPy.api.entities.MambuEntity.get")
    def test_get(self, mock_get):
        mock_get.return_value = "SupGet"

        mt = mambutask.MambuTask.get(taskId="MY TASK", parameter="random")
        self.assertEqual(mt, "SupGet")
        mock_get.assert_called_once_with(entid="MY TASK", parameter="random")

        with self.assertRaises(TypeError):
            mambutask.MambuTask.get(detailsLevel="BASIC")

    @mock.patch("MambuPy.api.mambustruct.MambuStruct._assignEntObjs")
    def test__assignEntObjs(self, mock_assign):
        # link type CLIENT
        mt = mambutask.MambuTask()
        mt._attrs = {
            "assignedUserKey": "abcdef12345",
            "taskLinkKey": "09876fedcba",
            "taskLinkType": "CLIENT",
        }

        mt._assignEntObjs()
        mock_assign.assert_any_call(
            mt._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mt._entities[-1],
            ("taskLinkKey", "mambuclient.MambuClient", "taskLink"))

        mt._assignEntObjs(
            [("assignedUserKey", "mambuuser.MambuUser", "assignedUser")])
        mock_assign.assert_called_with(
            [("assignedUserKey", "mambuuser.MambuUser", "assignedUser")],
            detailsLevel="BASIC", get_entities=False, debug=False)

        # link type GROUP
        mock_assign.reset_mock()
        mt = mambutask.MambuTask()
        mt._attrs = {
            "assignedUserKey": "abcdef12345",
            "taskLinkKey": "09876fedcba",
            "taskLinkType": "GROUP",
        }

        mt._assignEntObjs()
        mock_assign.assert_any_call(
            mt._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mt._entities[-1],
            ("taskLinkKey", "mambugroup.MambuGroup", "taskLink"))

        # link type INVALID
        mock_assign.reset_mock()
        mt = mambutask.MambuTask()
        mt._attrs = {
            "assignedUserKey": "abcdef12345",
            "taskLinkKey": "09876fedcba",
            "taskLinkType": "",
        }

        mt._assignEntObjs()
        mock_assign.assert_any_call(
            mt._entities, detailsLevel="BASIC", get_entities=False, debug=False)
        self.assertEqual(
            mt._entities[-1],
            ("taskLinkKey", "", "taskLink"))


if __name__ == "__main__":
    unittest.main()
