import base64
import json
import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.connector import rest
from MambuPy.mambuutil import MAX_UPLOAD_SIZE, MambuError, apiurl

from unit_rest import app_default_headers, app_json_headers


class MambuConnectorWriterREST(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        # Reset the singleton instance before each test
        rest.SessionSingleton._SessionSingleton__instance = None
        rest.SessionSingleton._SessionSingleton__session = None

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_update(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_update("entid", "prefix", {"oneattr": "123"})

        mock_requests.Session().request.assert_called_with(
            "PUT",
            "https://{}/api/prefix/entid".format(apiurl),
            params={},
            data='{"oneattr": "123"}',
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_update_auth(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Authorization"] = "Basic {}".format(
            base64.b64encode(b"myuser:mypass").decode("utf-8")
        )
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_update(
            "entid", "prefix", {"oneattr": "123"},
            user="myuser", pwd="mypass", url="myurl"
        )

        mock_requests.Session().request.assert_called_with(
            "PUT",
            "https://myurl/api/prefix/entid",
            params={},
            data='{"oneattr": "123"}',
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_create(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_create("prefix", {"oneattr": "123"})

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/prefix".format(apiurl),
            params={},
            data='{"oneattr": "123"}',
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_create_auth(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Authorization"] = "Basic {}".format(
            base64.b64encode(b"myuser:mypass").decode("utf-8")
        )
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_create(
            "prefix", {"oneattr": "123"},
            user="myuser", pwd="mypass", url="myurl"
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://myurl/api/prefix",
            params={},
            data='{"oneattr": "123"}',
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_delete(self, mock_requests):
        mock_requests.Session().request().status_code = 200
        headers = app_default_headers()

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_delete("12345", "prefix")

        mock_requests.Session().request.assert_called_with(
            "DELETE",
            "https://{}/api/prefix/12345".format(apiurl),
            params={},
            data=None,
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_delete_auth(self, mock_requests):
        mock_requests.Session().request().status_code = 200
        headers = app_default_headers()
        headers["Authorization"] = "Basic {}".format(
            base64.b64encode(b"myuser:mypass").decode("utf-8")
        )

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_delete(
            "12345", "prefix",
            user="myuser", pwd="mypass", url="myurl"
        )

        mock_requests.Session().request.assert_called_with(
            "DELETE",
            "https://myurl/api/prefix/12345",
            params={},
            data=None,
            headers=headers,
        )

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_patch(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_patch(
            "entid",
            "prefix",
            [
                ("ADD", "/onepath", "12345"),
                ("REPLACE", "/otherpath/asubpath", "54321"),
                ("REMOVE", "/somepath"),
            ],
        )

        mock_requests.Session().request.assert_called_with(
            "PATCH",
            "https://{}/api/prefix/entid".format(apiurl),
            params={},
            data='[{"op": "add", "path": "/onepath", "value": "12345"}, \
{"op": "replace", "path": "/otherpath/asubpath", "value": "54321"}, \
{"op": "remove", "path": "/somepath"}]',
            headers=headers,
        )

        mock_requests.Session().reset_mock()
        mcrest.mambu_patch("entid", "prefix", [])
        self.assertEqual(mock_requests.request.call_count, 0)

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_patch_auth(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200
        headers = app_json_headers()
        headers["Authorization"] = "Basic {}".format(
            base64.b64encode(b"myuser:mypass").decode("utf-8")
        )
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_patch(
            "entid",
            "prefix",
            [
                ("ADD", "/onepath", "12345"),
                ("REPLACE", "/otherpath/asubpath", "54321"),
                ("REMOVE", "/somepath"),
            ],
            user="myuser", pwd="mypass", url="myurl"
        )

        mock_requests.Session().request.assert_called_with(
            "PATCH",
            "https://myurl/api/prefix/entid",
            params={},
            data='[{"op": "add", "path": "/onepath", "value": "12345"}, \
{"op": "replace", "path": "/otherpath/asubpath", "value": "54321"}, \
{"op": "remove", "path": "/somepath"}]',
            headers=headers,
        )

        mock_requests.Session().reset_mock()
        mcrest.mambu_patch("entid", "prefix", [])
        self.assertEqual(mock_requests.request.call_count, 0)

    @mock.patch("MambuPy.api.connector.rest.open")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.MultipartEncoder")
    def test_mambu_upload_document(
        self, mock_multipartencoder, mock_requests, mock_uuid, mock_open
    ):
        with open("/tmp/selfie.png", "w") as f:
            f.write("yoda yo yo")
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO"
        mock_requests.Session().request().status_code = 200
        encoder = lambda: None
        encoder.content_type = "multipart/form-data; boundary=outer_rim"
        mock_multipartencoder.return_value = encoder

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_upload_document(
            "JEDI_ORDER", "Yoda", "/tmp/selfie.png", "my_selfie.png", "Some selfie"
        )

        headers = app_json_headers()
        headers["Idempotency-Key"] = "r2d2-n-c3pO"
        headers["Content-Type"] = "multipart/form-data; boundary=outer_rim"
        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/documents".format(apiurl),
            params={},
            data=encoder,
            headers=headers,
        )
        mock_multipartencoder.assert_called_with(
            fields={
                "ownerType": "JEDI_ORDER",
                "id": "Yoda",
                "name": "my_selfie.png",
                "notes": "Some selfie",
                "file": ("selfie.png", mock_open("/tmp/selfie.png", "rb"), "image/png"),
            }
        )

    def test_mambu_upload_document_mambu_restrictions(self):
        mcrest = rest.MambuConnectorREST()

        # invalid chars in filename
        with self.assertRaisesRegex(MambuError, r"/tmp/selfie<>.png name not allowed"):
            mcrest.mambu_upload_document(
                "JEDI_ORDER", "Yoda", "/tmp/selfie<>.png", "my_selfie.png", "Some selfie"
            )

        # filename should have one and just one extension
        with self.assertRaisesRegex(MambuError, r"/tmp/sel.fie.png invalid name"):
            mcrest.mambu_upload_document(
                "JEDI_ORDER", "Yoda", "/tmp/sel.fie.png", "my_selfie.png", "Some selfie"
            )

        # mimetype not allowed
        with self.assertRaisesRegex(
            MambuError, r"/tmp/selfie.exe mimetype not supported"
        ):
            mcrest.mambu_upload_document(
                "JEDI_ORDER", "Yoda", "/tmp/selfie.exe", "my_selfie.png", "Some selfie"
            )

        # max size
        rest.MAX_UPLOAD_SIZE = 1
        with self.assertRaisesRegex(MambuError, r"/tmp/selfie.png exceeds 1 bytes"):
            mcrest.mambu_upload_document(
                "JEDI_ORDER", "Yoda", "/tmp/selfie.png", "my_selfie.png", "Some selfie"
            )
        rest.MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE

        os.remove("/tmp/selfie.png")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_delete_document(self, mock_requests):
        mock_requests.Session().request().status_code = 204

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_delete_document("docId")

        mock_requests.Session().request.assert_called_with(
            "DELETE",
            "https://{}/api/documents/{}".format(apiurl, "docId"),
            params={},
            data=None,
            headers=mcrest._headers)

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_change_state(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_change_state(
            entid="12345",
            prefix="loans",
            action="APPROVE",
            notes="Prueba"
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/12345:changeState".format(apiurl),
            params={},
            data='{"action": "APPROVE", "notes": "Prueba"}',
            headers=mcrest._headers
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_comment(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers.update(
            {"Content-Type": "application/json",
             "Idempotency-Key": "r2d2-n-c3pO-BB8"})

        for owner_type in [
                "CLIENT",
                "GROUP",
                "LOAN_PRODUCT",
                "SAVINGS_PRODUCT",
                "CENTRE",
                "BRANCH",
                "USER",
                "LOAN_ACCOUNT",
                "DEPOSIT_ACCOUNT",
                "ID_DOCUMENT",
                "LINE_OF_CREDIT",
                "GL_JOURNAL_ENTRY"
        ]:
            mock_requests.Session().reset_mock()
            mcrest.mambu_comment(
                "OWNER_ID", owner_type, "My Comment")
            mock_requests.Session().request.assert_called_with(
                "POST",
                "https://{}/api/comments".format(apiurl),
                params={},
                data=json.dumps(
                    {"ownerKey": "OWNER_ID",
                     "ownerType": owner_type,
                     "text": "My Comment"}),
                headers=mcrest._headers)

        with self.assertRaisesRegex(
                MambuError, r"Owner MY_OWNER_TYPE not allowed"):
            mcrest.mambu_comment("OWNER_ID", "MY_OWNER_TYPE", "My Comment")

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_make_disbursement(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_make_disbursement(
            loan_id="12345",
            notes="My Notes",
            firstRepaymentDate="my-repayment-date",
            valueDate="my-value-date",
            allowed_fields=["hello"],
            **{"hello": "world", "bye bye": "miss american pie"}
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/12345/disbursement-transactions".format(apiurl),
            params={},
            data='{"firstRepaymentDate": "my-repayment-date", \
"notes": "My Notes", \
"valueDate": "my-value-date", \
"hello": "world"}',
            headers=mcrest._headers
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_make_repayment(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_make_repayment(
            loan_id="12345",
            amount=100.0,
            notes="My Notes",
            valueDate="my-value-date",
            allowed_fields=["hello", "transactionDetails"],
            loantransaction_allowed_fields=["transactionChannelId"],
            **{
                "hello": "world",
                "goodbye": "stranger",  # ignored parameter
                "transactionDetails": {
                    "transactionChannelId": "rock&roll",
                    "nothing": "else matters",  # ignored parameter
                },
                "_music_died_day": {
                    "buddy": "holly",
                    "bye bye": "miss american pie"
                },
            },
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/12345/repayment-transactions".format(apiurl),
            params={},
            data='{"amount": 100.0, \
"notes": "My Notes", \
"valueDate": "my-value-date", \
"hello": "world", \
"transactionDetails": {"transactionChannelId": "rock&roll"}, \
"_music_died_day": {"buddy": "holly", "bye bye": "miss american pie"}}',
            headers=mcrest._headers
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_make_fee(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_make_fee(
            loan_id="12345",
            amount=100.0,
            installmentNumber=15,
            notes="My Notes",
            valueDate="my-value-date",
            allowed_fields=["hello"],
            **{"hello": "world", "bye bye": "miss american pie"}
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/12345/fee-transactions".format(apiurl),
            params={},
            data='{"amount": 100.0, \
"installmentNumber": 15, \
"notes": "My Notes", \
"valueDate": "my-value-date", \
"hello": "world"}',
            headers=mcrest._headers
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_loanaccount_writeoff(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_loanaccount_writeoff(
            loanid="12345",
            notes="My Notes"
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/12345:writeOff".format(apiurl),
            params={},
            data='{"notes": "My Notes"}',
            headers=mcrest._headers
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    @mock.patch("MambuPy.api.connector.rest.uuid")
    def test_mambu_loantransaction_adjust(self, mock_uuid, mock_requests):
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO-BB8"
        mock_requests.Session().request().status_code = 200

        mcrest = rest.MambuConnectorREST()
        mcrest._headers["Content-Type"] = "application/json"
        mcrest._headers["Idempotency-Key"] = "r2d2-n-c3pO-BB8"

        mcrest.mambu_loantransaction_adjust(
            transactionid="12345678",
            notes="My Notes",
        )

        mock_requests.Session().request.assert_called_with(
            "POST",
            "https://{}/api/loans/transactions/12345678:adjust".format(apiurl),
            params={},
            data='{"notes": "My Notes"}',
            headers=mcrest._headers
        )


if __name__ == "__main__":
    unittest.main()
