import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.connector import mambuconnector


class MambuConnectorReader(unittest.TestCase):
    def test_mambu_get(self):
        self.assertEqual(hasattr(mambuconnector.MambuConnectorReader, "mambu_get"), True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get(None, "12345", "")

    def test_mambu_get_all(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_get_all"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get_all(
                None, "", {}, 0, 0, "OFF", "BASIC", ""
            )

    def test_mambu_search(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_search"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_search(
                [{}], {}, 0, 0, "OFF", "BASIC", ""
            )

    def test_mambu_get_documents_metadata(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader,
                    "mambu_get_documents_metadata"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get_documents_metadata(
                None, "", "")

    def test_mambu_loanaccount_getSchedule(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader,
                    "mambu_loanaccount_getSchedule"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_loanaccount_getSchedule(
                None, "")

    def test_mambu_get_customfield(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader,
                    "mambu_get_customfield"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get_customfield(
                None, "")

    def test_mambu_get_comments(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader,
                    "mambu_get_comments"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get_comments(
                None, "", "")


class MambuConnectorWriter(unittest.TestCase):
    def test_mambu_update(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_update"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_update(None, "id", "", {})

    def test_mambu_patch(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_patch"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_patch(None, "id", "", [])

    def test_mambu_create(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_create"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_create(None, "", {})

    def test_mambu_upload_document(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_upload_document"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_upload_document(
                None, "OWNER", "entid", "path/filename", "title", "notes"
            )

    def test_mambu_delete_document(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_delete_document"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_delete_document(None, "")

    def test_mambu_change_state(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_change_state"), True
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_change_state(None, "", "", "" , "")

    def test_mambu_comment(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter,
                    "mambu_comment"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_comment(
                None, "", "", "")

    def test_mambu_make_disbursement(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter,
                    "mambu_make_disbursement"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_make_disbursement(
                None, "", "", "", "", "")

    def test_mambu_make_repayment(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter,
                    "mambu_make_repayment"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_make_repayment(
                None, "", "", "", "", "")

    def test_mambu_loanaccount_writeoff(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter,
                    "mambu_loanaccount_writeoff"),
            True,
        )
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_loanaccount_writeoff(
                None, "", "")


if __name__ == "__main__":
    unittest.main()
