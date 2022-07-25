import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities


class MambuSearchableEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class_searchable(
            entities.MambuEntity, entities.MambuEntitySearchable
        ):
            """"""

        self.child_class_searchable = child_class_searchable

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_search(self, mock_connector):
        mock_connector.mambu_search.return_value = b"""[
        {"encodedKey":"abc123","id":"12345"},
        {"encodedKey":"def456","id":"67890"}
        ]"""

        ms = self.child_class_searchable.search()

        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})

        ms = self.child_class_searchable.search(
            filterCriteria={"one": "two"}, otherParam="random")

        mock_connector.mambu_search.assert_called_with(
            "",
            filterCriteria={"one": "two"},
            sortingCriteria=None,
            offset=0,
            limit=1000,
            paginationDetails="OFF",
            detailsLevel="BASIC",
            otherParam="random")
        self.assertEqual(len(ms), 2)
        self.assertEqual(ms[0].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[0]._attrs, {"encodedKey": "abc123", "id": "12345"})
        self.assertEqual(ms[1].__class__.__name__, "child_class_searchable")
        self.assertEqual(ms[1]._attrs, {"encodedKey": "def456", "id": "67890"})


if __name__ == "__main__":
    unittest.main()
