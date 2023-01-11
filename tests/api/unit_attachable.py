import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.mambuutil import MambuPyError


class MambuAttachableEntityTests(unittest.TestCase):
    def setUp(self):
        class child_class_attachable(
            entities.MambuEntity, entities.MambuEntityAttachable
        ):
            _prefix = "un_prefix"
            _ownerType = "MY_ENTITY"
            _connector = mock.Mock()

            def __init__(self, **kwargs):
                super().__init__(connector=self._connector, **kwargs)
                self._attrs = {"id": "12345"}
                self._attachments = {}

        self.child_class_attachable = child_class_attachable

    def test_attach_document(self):
        child = self.child_class_attachable()
        mock_connector = child._connector
        mock_connector.mambu_upload_document.return_value = b"""{
        "encodedKey":"0123456789abcdef","id":"12345","ownerType":"MY_ENTITY",
        "type":"png","fileName":"someImage.png"
        }"""

        upl = child.attach_document("/tmp/someImage.png", "MyImage", "this is a test")

        self.assertEqual(list(child._attachments.keys()), ["12345"])
        self.assertEqual(
            child._attachments["12345"]._attrs,
            {
                "encodedKey": "0123456789abcdef",
                "id": "12345",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "someImage.png",
            },
        )
        self.assertEqual(upl, mock_connector.mambu_upload_document.return_value)
        mock_connector.mambu_upload_document.assert_called_with(
            owner_type="MY_ENTITY",
            entid="12345",
            filename="/tmp/someImage.png",
            name="MyImage",
            notes="this is a test",
        )

    def test_get_attachments_metadata(self):
        child = self.child_class_attachable()
        mock_connector = child._connector
        mock_connector.mambu_get_documents_metadata.return_value = b"""[{
        "encodedKey":"0123456789abcdef","id":"67890","ownerType":"MY_ENTITY",
        "type":"png","fileName":"someImage.png"
        },
        {
        "encodedKey":"fedcba9876543210","id":"09876","ownerType":"MY_ENTITY",
        "type":"png","fileName":"anotherImage.png"
        }]"""

        metadata = child.get_attachments_metadata()

        self.assertEqual(list(child._attachments.keys()), ["67890", "09876"])
        self.assertEqual(
            child._attachments["67890"]._attrs,
            {
                "encodedKey": "0123456789abcdef",
                "id": "67890",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "someImage.png",
            },
        )
        self.assertEqual(
            child._attachments["09876"]._attrs,
            {
                "encodedKey": "fedcba9876543210",
                "id": "09876",
                "ownerType": "MY_ENTITY",
                "type": "png",
                "fileName": "anotherImage.png",
            },
        )
        self.assertEqual(
            metadata,
            mock_connector.mambu_get_documents_metadata.return_value)
        mock_connector.mambu_get_documents_metadata.assert_called_with(
            entid="12345",
            owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF"
        )
        mock_connector.mambu_get_documents_metadata.assert_called_with(
            entid="12345",
            owner_type="MY_ENTITY",
            limit=None, offset=None, paginationDetails="OFF"
        )

    def test_del_attachment(self):
        child = self.child_class_attachable()
        mock_connector = child._connector
        mock_connector.mambu_delete_document.return_value = None

        child._attachments = {
            "67890": {
                "encodedKey": "0123456789abcdef",
                "id": "67890",
                "ownerType": "MY_ENTITY",
                "name": "someImage",
                "type": "png",
                "fileName": "someImage.png"
            },
            "09876": {
                "encodedKey": "fedcba9876543210",
                "id": "09876",
                "ownerType": "MY_ENTITY",
                "name": "anotherImage",
                "type": "png",
                "fileName": "anotherImage.png"
            },
            "75310": {
                "encodedKey": "fedcba9876543210",
                "id": "75310",
                "ownerType": "MY_ENTITY",
                "name": "yaImage",
                "type": "png",
                "fileName": "yaImage.png"
            },
        }

        with self.assertRaisesRegex(
            MambuPyError,
            r"^You must provide a documentId or a documentName$"
        ):
            child.del_attachment()

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document name 'aName' is not an attachment of child_class_attachable - id: 12345$"
        ):
            child.del_attachment(documentName="aName")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document id 'anId' is not an attachment of child_class_attachable - id: 12345$"
        ):
            child.del_attachment(documentId="anId")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^Document with name 'anotherImage' does not has id '67890'$"
        ):
            child.del_attachment(documentId="67890", documentName="anotherImage")

        child.del_attachment(documentId="67890")
        self.assertEqual(
            sorted(list(child._attachments.keys())),
            ["09876", "75310"])
        mock_connector.mambu_delete_document.assert_called_with("67890")

        child.del_attachment(documentName="anotherImage")
        self.assertEqual(list(child._attachments.keys()), ["75310"])
        mock_connector.mambu_delete_document.assert_called_with("09876")

        child.del_attachment(documentId="75310", documentName="yaImage")
        self.assertEqual(list(child._attachments.keys()), [])
        mock_connector.mambu_delete_document.assert_called_with("75310")


if __name__ == "__main__":
    unittest.main()
