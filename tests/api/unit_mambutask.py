import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambutask
from MambuPy.mambuutil import MambuPyError


class MambuTask(unittest.TestCase):
    def test_implements_interfaces(self):
        mt = mambutask.MambuTask()
        self.assertTrue(isinstance(mt, mambutask.MambuEntity))
        self.assertTrue(isinstance(mt, interfaces.MambuWritable))

    def test_has_properties(self):
        mc = mambutask.MambuTask()
        self.assertEqual(mc._prefix, "tasks")
        self.assertEqual(
            mc._filter_keys,
            [
             "username",
             "clientId",
             "groupId",
             "status",
            ],
        )
        self.assertEqual(
            mc._sortBy_fields,
            [],
        )

    @mock.patch("MambuPy.api.entities.MambuEntity.get")
    def test_get(self, mock_get):
        mock_get.return_value = "SupGet"

        mp = mambutask.MambuTask.get(taskId="MY TASK")
        self.assertEqual(mp, "SupGet")
        mock_get.assert_called_once_with(entid="MY TASK")

        with self.assertRaises(TypeError):
            mambutask.MambuTask.get(detailsLevel="BASIC")


if __name__ == "__main__":
    unittest.main()
