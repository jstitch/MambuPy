# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock
import unittest
from datetime import datetime

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
                    "dbname",
                    "dbuser",
                    "dbpwd",
                    "dbhost",
                    "dbport",
                    "dbeng",
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
        self.assertEqual(mambuutil.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, 1000)

    def test_error_attrs(self):
        self.assertEqual(mambuutil.MambuPyError.__bases__, (Exception,))
        self.assertEqual(mambuutil.MambuError.__bases__,
                         (mambuutil.MambuPyError,))
        self.assertEqual(mambuutil.MambuCommError.__bases__,
                         (mambuutil.MambuError,))

    @mock.patch("MambuPy.mambuutil.create_engine")
    def test_connect_dB(self, mock_create_engine):
        mock_create_engine.return_value = "test_connect_dB"
        en = mambuutil.connect_db()
        self.assertEqual(en, "test_connect_dB")
        mock_create_engine.assert_called_once_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db?charset=utf8&use_unicode=1",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(echoopt=True, params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=True,
        )
        mambuutil.connect_db(engine="myeng", params="")
        mock_create_engine.assert_called_with(
            "myeng://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(user="myuser", params="")
        mock_create_engine.assert_called_with(
            "mysql://myuser:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(password="mypass", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mypass@localhost:3306/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(host="myhost", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@myhost:3306/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(port="myport", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:myport/mambu_db",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        mambuutil.connect_db(database="mydb", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mydb",
            poolclass=mambuutil.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )

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
        if sys.version_info < (3, 0):
            url = "https://domain.mambu.com/some_url/strange_ñame/having_ñ"
            resUrl = "https://domain.mambu.com/some_url/strange_%c3%b1ame/having_%c3%b1"
            self.assertEqual(mambuutil.iri_to_uri(url), resUrl
                             )
        else:
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
        from datetime import datetime
        if sys.version_info < (3, 0):
            format = "%Y-%m-%dT%H:%M:%S+0000"
        else:
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
            code=200, content="hello world",
            request=request("url", "body", "headers"))
        mock_requests.get.return_value = response(
            code=200, content=b"hello world",
            request=request("url", "body", "headers"))
        d = mambuutil.backup_db(
            callback="da-callback", bool_func=lambda: True, output_fname="/tmp/out_test"
        )
        # API is called with these arguments using GET method
        mock_requests.get.assert_called_with(
            mambuutil.iri_to_uri(mambugeturl.getmambuurl() +
                                 "database/backup/LATEST"),
            auth=(mambuconfig.apiuser, mambuconfig.apipwd),
            headers={
                "content-type": "application/json",
                "Accept": "application/vnd.mambu.v1+zip",
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
            request=request("url", "body", "headers")
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
            response(code=200, content="hello world",
                     request=request("url", "body", "headers"))]
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
