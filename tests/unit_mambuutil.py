# coding: utf-8

from datetime import datetime
import logging
import os
import sys
import unittest

logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy import mambuutil, mambugeturl

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead




class MambuUtilTests(unittest.TestCase):
    def test_attrs(self):
        for atr in ["apiurl",
                    "apiuser",
                    "apipwd",
                    "OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE",
                    "PAGINATIONDETAILS", "DETAILSLEVEL",
                    "MAX_UPLOAD_SIZE",
                    "UPLOAD_FILENAME_INVALID_CHARS",
                    "ALLOWED_UPLOAD_MIMETYPES",
                    "SEARCH_OPERATORS",
                    "MambuPyError",
                    "MambuError",
                    "MambuCommError",
                    ]:
            try:
                getattr(mambuutil, atr)
            except AttributeError:
                self.fail("attribute missing on mambuutil: {}".format(atr))

    def test_constants(self):
        self.assertEqual(mambuutil.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, 50)

    def test_error_attrs(self):
        self.assertEqual(mambuutil.MambuPyError.__bases__, (Exception,))
        self.assertEqual(mambuutil.MambuError.__bases__,
                         (mambuutil.MambuPyError,))
        self.assertEqual(mambuutil.MambuCommError.__bases__,
                         (mambuutil.MambuError,))

    def test_strip_tags(self):
        self.assertEqual(mambuutil.strip_tags(
            "<html>some text</html>"), "some text")
        self.assertEqual(mambuutil.strip_tags(
            "<html>some&nbsp;text</html>"), "some text")

    def test_strip_consecutive_repeated_chars(self):
        self.assertEqual(
            mambuutil.strip_consecutive_repeated_char("TEST   STRING", " "),
            "TEST STRING",
        )
        self.assertEqual(
            mambuutil.strip_consecutive_repeated_char("TTTEST STRING", "T"),
            "TEST STRING",
        )
        self.assertEqual(
            mambuutil.strip_consecutive_repeated_char("TEST STRINGGG", "G"),
            "TEST STRING",
        )
        self.assertEqual(
            mambuutil.strip_consecutive_repeated_char("TTTT", "T"), "T")

    def test_iri_to_uri(self):
        self.assertEqual(
            mambuutil.iri_to_uri("https://domain.mambu.com/some_url"),
            "https://domain.mambu.com/some_url",
        )
        self.assertEqual(
            mambuutil.iri_to_uri(
                "https://domain.mambu.com/some_url/strange_name/having_ñ"
            ),
            "https://domain.mambu.com/some_url/strange_name/having_ñ",
        )

    def test_encoded_dict(self):
        d = {
            "a": "no-utf",
            "b": "yes-utf",
            "c": "strange-char-ñ",
        }
        d2 = mambuutil.encoded_dict(d)
        self.assertEqual(d2["a"], "no-utf")
        self.assertEqual(d2["b"], "yes-utf")
        self.assertEqual(d2["c"], "strange-char-ñ")

    def test_date_format(self):
        """Test date_format"""
        format = "%Y-%m-%dT%H:%M:%S-06:00"
        today = datetime.now()
        # default date_format
        self.assertEqual(
            mambuutil.date_format(field=today.strftime(
                format)).strftime("%Y%m%d%H%M%S"),
            today.strftime("%Y%m%d%H%M%S"),
        )
        # given format
        self.assertEqual(
            mambuutil.date_format(field=today.strftime(format), formato="%Y%m%d").strftime(
                "%Y%m%d"),
            today.strftime("%Y%m%d"),
        )

    @mock.patch("MambuPy.mambuutil.requests")
    @mock.patch("MambuPy.mambuutil.sleep")
    def test_backup_db(self, mock_sleep, mock_requests):
        import os

        try:
            os.remove("/tmp/out_test")
        except OSError:
            pass

        class request:
            def __init__(self, url, body, headers):
                self.url = url
                self.body = body
                self.headers = headers

        class response:
            def __init__(self, code, content, request):
                self.status_code = code
                self.content = content
                self.request = request
        mock_requests.post.return_value = response(
            code=202, content="hello world",
            request=request("url", "body", {"headers": "value"}))
        mock_requests.get.return_value = response(
            code=200, content=b"hello world",
            request=request("url", "body", {"headers": "value"}))
        d = mambuutil.backup_db(
            callback="da-callback", bool_func=lambda: True, output_fname="/tmp/out_test"
        )
        # API is called with these arguments using GET method
        mock_requests.get.assert_called_with(
            mambuutil.iri_to_uri(mambugeturl.getmambuurl() +
                                 "database/backup/LATEST"),
            auth=(mambuconfig.apiuser, mambuconfig.apipwd),
            headers={
                "Accept": "application/vnd.mambu.v2+zip",
            },
        )
        self.assertEqual(mock_requests.post.call_count, 1)
        self.assertEqual(mock_requests.get.call_count, 1)

        self.assertEqual(d["callback"], "da-callback")
        self.assertTrue(d["latest"])
        d = mambuutil.backup_db(
            callback="da-callback",
            bool_func=lambda: False,
            retries=1,
            output_fname="/tmp/out_test",
            force_download_latest=True,
        )
        self.assertEqual(d["callback"], "da-callback")
        self.assertFalse(d["latest"])
        mock_requests.post.reset_mock()
        mock_requests.get.reset_mock()
        d = mambuutil.backup_db(
            callback="da-callback",
            bool_func=lambda: False,
            retries=1,
            justbackup=True,
            output_fname="/tmp/out_test",
            force_download_latest=True,
        )
        self.assertEqual(mock_requests.post.call_count, 0)
        self.assertEqual(mock_requests.get.call_count, 1)
        self.assertEqual(d["callback"], "da-callback")
        self.assertTrue(d["latest"])
        d = mambuutil.backup_db(
            callback="da-callback",
            bool_func=lambda: True,
            output_fname="/tmp/out_test",
            verbose=True,
        )
        self.assertEqual(d["callback"], "da-callback")
        self.assertTrue(d["latest"])
        with self.assertRaisesRegexp(
            mambuutil.MambuError, r"Tired of waiting, giving up..."
        ):
            d = mambuutil.backup_db(
                callback="da-callback",
                bool_func=lambda: False,
                retries=5,
                output_fname="/tmp/out_test",
                verbose=True,
            )

        mock_requests.post.return_value = response(
            code=404, content="hello world (not found)",
            request=request("url", "body", {"headers": "value"})
        )
        with self.assertRaisesRegexp(
            mambuutil.MambuCommError,
            r"Error posting request for backup: hello world \(not found\)$",
        ):
            d = mambuutil.backup_db(
                callback="da-callback",
                bool_func=lambda: True,
                output_fname="/tmp/out_test",
                verbose=True,
            )

        mock_requests.post.side_effect = Exception("something wrong")
        with self.assertRaisesRegexp(
            mambuutil.MambuError,
            r"Error requesting backup: Exception\('something wrong'",
        ):
            d = mambuutil.backup_db(
                callback="da-callback",
                bool_func=lambda: True,
                output_fname="/tmp/out_test",
                verbose=True,
            )

        mock_requests.post.side_effect = [
            response(code=202, content="hello world",
                     request=request("url", "body", {"headers": "value"}))]
        mock_requests.get.return_value = response(
            code=404, content="hello world (not found)",
            request=request("url", "body", "headers")
        )
        with self.assertRaisesRegexp(
            mambuutil.MambuCommError,
            r"Error getting database backup: hello world \(not found\)$",
        ):
            d = mambuutil.backup_db(
                callback="da-callback",
                bool_func=lambda: True,
                output_fname="/tmp/out_test",
                verbose=True,
            )


if __name__ == "__main__":
    unittest.main()
