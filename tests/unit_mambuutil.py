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
from MambuPy import mambuutil

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


class MambuUtilTests(unittest.TestCase):
    def test_attrs(self):
        for atr in [
            "apiurl",
            "apiuser",
            "apipwd",
            "dbname",
            "dbuser",
            "dbpwd",
            "dbhost",
            "dbport",
            "dbeng",
            "OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE",
            "PAGINATIONDETAILS",
            "DETAILSLEVEL",
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
        self.assertEqual(mambuutil.MambuError.__bases__, (mambuutil.MambuPyError,))
        self.assertEqual(mambuutil.MambuCommError.__bases__, (mambuutil.MambuError,))

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
        self.assertEqual(mambuutil.strip_tags("<html>some text</html>"), "some text")
        self.assertEqual(mambuutil.strip_tags("<html>some&nbsp;text</html>"), "some text")

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
        self.assertEqual(mambuutil.strip_consecutive_repeated_char("TTTT", "T"), "T")

    def test_iri_to_uri(self):
        self.assertEqual(
            mambuutil.iri_to_uri("https://domain.mambu.com/some_url"),
            "https://domain.mambu.com/some_url",
        )
        if sys.version_info < (3, 0):
            url = "https://domain.mambu.com/some_url/strange_ñame/having_ñ"
            resUrl = "https://domain.mambu.com/some_url/strange_%c3%b1ame/having_%c3%b1"
            self.assertEqual(mambuutil.iri_to_uri(url), resUrl)
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
            mambuutil.date_format(field=today.strftime(format)).strftime("%Y%m%d%H%M%S"),
            today.strftime("%Y%m%d%H%M%S"),
        )
        # given format
        self.assertEqual(
            mambuutil.date_format(field=today.strftime(format), formato="%Y%m%d").strftime(
                "%Y%m%d"
            ),
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
            mambuutil.iri_to_uri(mambuutil.getmambuurl() + "database/backup/LATEST"),
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


class UrlFuncTests(unittest.TestCase):
    def setUp(self):
        self.prefix = "https://domain.mambu.com"

    def test_getmambuurl(self):
        self.assertEqual(mambuutil.getmambuurl(), self.prefix + "/api/")

    def test_getbranchesurl(self):
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC"),
            self.prefix + "/api/" + "branches/CCCC",
        )
        self.assertEqual(
            mambuutil.getbranchesurl("CCCC"), self.prefix + "/api/" + "branches/CCCC"
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch=""), self.prefix + "/api/" + "branches"
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=True),
            self.prefix + "/api/" + "branches/CCCC?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=False),
            self.prefix + "/api/" + "branches/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=None),
            self.prefix + "/api/" + "branches/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", fullDetails="whatever"),
            self.prefix + "/api/" + "branches/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", offset=10),
            self.prefix + "/api/" + "branches/CCCC?offset=10",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", limit=10),
            self.prefix + "/api/" + "branches/CCCC?limit=10",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(idbranch="CCCC", anything="whatever"),
            self.prefix + "/api/" + "branches/CCCC",
        )
        self.assertEqual(
            mambuutil.getbranchesurl(
                idbranch="CCCC", fullDetails=True, offset=2, limit=0
            ),
            self.prefix + "/api/" + "branches/CCCC?fullDetails=true&offset=2&limit=0",
        )

    def test_getcentresurl(self):
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC"),
            self.prefix + "/api/" + "centres/CCCC",
        )
        self.assertEqual(
            mambuutil.getcentresurl("CCCC"), self.prefix + "/api/" + "centres/CCCC"
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre=""), self.prefix + "/api/" + "centres"
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", fullDetails=True),
            self.prefix + "/api/" + "centres/CCCC?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", fullDetails=False),
            self.prefix + "/api/" + "centres/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", fullDetails=None),
            self.prefix + "/api/" + "centres/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", fullDetails="whatever"),
            self.prefix + "/api/" + "centres/CCCC?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", offset=10),
            self.prefix + "/api/" + "centres/CCCC?offset=10",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", limit=10),
            self.prefix + "/api/" + "centres/CCCC?limit=10",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", anything="whatever"),
            self.prefix + "/api/" + "centres/CCCC",
        )
        self.assertEqual(
            mambuutil.getcentresurl(idcentre="CCCC", fullDetails=True, offset=2, limit=0),
            self.prefix + "/api/" + "centres/CCCC?fullDetails=true&offset=2&limit=0",
        )

    def test_getrepaymentsurl(self):
        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred="12345"),
            self.prefix + "/api/" + "loans/12345/repayments",
        )
        self.assertEqual(
            mambuutil.getrepaymentsurl("12345"),
            self.prefix + "/api/" + "loans/12345/repayments",
        )
        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred=""),
            self.prefix + "/api/" + "loans//repayments",
        )

        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred="12345", fullDetails=True),
            self.prefix + "/api/" + "loans/12345/repayments?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred="12345", fullDetails=False),
            self.prefix + "/api/" + "loans/12345/repayments?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred="12345", offset=10),
            self.prefix + "/api/" + "loans/12345/repayments?offset=10",
        )
        self.assertEqual(
            mambuutil.getrepaymentsurl(idcred="12345", limit=10),
            self.prefix + "/api/" + "loans/12345/repayments?limit=10",
        )

    def test_getloansurl(self):
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345"), self.prefix + "/api/" + "loans/12345"
        )
        self.assertEqual(
            mambuutil.getloansurl("12345"), self.prefix + "/api/" + "loans/12345"
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred=""), self.prefix + "/api/" + "loans"
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", fullDetails=True),
            self.prefix + "/api/" + "loans/12345?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", fullDetails=False),
            self.prefix + "/api/" + "loans/12345?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", fullDetails=None),
            self.prefix + "/api/" + "loans/12345?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", fullDetails="whatever"),
            self.prefix + "/api/" + "loans/12345?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", offset=10),
            self.prefix + "/api/" + "loans/12345?offset=10",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", limit=10),
            self.prefix + "/api/" + "loans/12345?limit=10",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", accountState="ACTIVE"),
            self.prefix + "/api/" + "loans/12345?accountState=ACTIVE",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", branchId="CCCC"),
            self.prefix + "/api/" + "loans/12345?branchId=CCCC",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", centreId="CCCC"),
            self.prefix + "/api/" + "loans/12345?centreId=CCCC",
        )
        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", creditOfficerUsername="fulanito"),
            self.prefix + "/api/" + "loans/12345?creditOfficerUsername=fulanito",
        )
        self.assertEqual(
            mambuutil.getloansurl(
                idcred="12345",
                fullDetails=True,
                accountState="ACTIVE_IN_ARREARS",
                branchId="CCCC",
                centreId="CCCC",
                creditOfficerUsername="fulanito",
                offset=2,
                limit=0,
            ),
            self.prefix
            + "/api/"
            + "loans/12345?fullDetails=true&accountState=ACTIVE_IN_ARREARS&branchId=CCCC&centreId=CCCC&creditOfficerUs\
ername=fulanito&offset=2&limit=0",
        )

        self.assertEqual(
            mambuutil.getloansurl(idcred="12345", anything="whatever"),
            self.prefix + "/api/" + "loans/12345",
        )

    def test_getloanscustominformationurl(self):
        self.assertEqual(
            mambuutil.getloanscustominformationurl("loanID123"),
            self.prefix + "/api/" + "loans/loanID123/custominformation",
        )
        self.assertEqual(
            mambuutil.getloanscustominformationurl("loanID123", customfield="bla"),
            self.prefix + "/api/" + "loans/loanID123/custominformation/bla",
        )

    def test_getgroupurl(self):
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890",
        )
        self.assertEqual(
            mambuutil.getgroupurl("XY890"), self.prefix + "/api/" + "groups/XY890"
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup=""), self.prefix + "/api/" + "groups"
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", fullDetails=True),
            self.prefix + "/api/" + "groups/XY890?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", fullDetails=False),
            self.prefix + "/api/" + "groups/XY890?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", fullDetails=None),
            self.prefix + "/api/" + "groups/XY890?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", fullDetails="whatever"),
            self.prefix + "/api/" + "groups/XY890?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", branchId="BRANCH"),
            self.prefix + "/api/" + "groups/XY890?branchId=BRANCH",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", centreId="CENTRE"),
            self.prefix + "/api/" + "groups/XY890?centreId=CENTRE",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", offset=10),
            self.prefix + "/api/" + "groups/XY890?offset=10",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", limit=10),
            self.prefix + "/api/" + "groups/XY890?limit=10",
        )
        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", creditOfficerUsername="fulanito"),
            self.prefix + "/api/" + "groups/XY890?creditOfficerUsername=fulanito",
        )
        self.assertEqual(
            mambuutil.getgroupurl(
                idgroup="XY890",
                fullDetails=True,
                creditOfficerUsername="fulanito",
                branchId="BRANCH",
                centreId="CENTRE",
                offset=2,
                limit=0,
            ),
            self.prefix
            + "/api/"
            + "groups/XY890?fullDetails=true&creditOfficerUsername=fulanito&branchId=BRANCH&centreId=CENTRE&limit=0&of\
fset=2",
        )

        self.assertEqual(
            mambuutil.getgroupurl(idgroup="XY890", anything="whatever"),
            self.prefix + "/api/" + "groups/XY890",
        )

    def test_getgrouploansurl(self):
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890/loans",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl("XY890"),
            self.prefix + "/api/" + "groups/XY890/loans",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup=""),
            self.prefix + "/api/" + "groups//loans",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=True),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=False),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=None),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", fullDetails="whatever"),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", accountState="ACTIVE"),
            self.prefix + "/api/" + "groups/XY890/loans?accountState=ACTIVE",
        )
        self.assertEqual(
            mambuutil.getgrouploansurl(
                idgroup="XY890", fullDetails=True, accountState="CLOSED"
            ),
            self.prefix
            + "/api/"
            + "groups/XY890/loans?fullDetails=true&accountState=CLOSED",
        )

        self.assertEqual(
            mambuutil.getgrouploansurl(idgroup="XY890", anything="whatever"),
            self.prefix + "/api/" + "groups/XY890/loans",
        )

    def test_getgroupcustominformationurl(self):
        self.assertEqual(
            mambuutil.getgroupcustominformationurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890/custominformation",
        )
        self.assertEqual(
            mambuutil.getgroupcustominformationurl(idgroup="XY890", customfield="bla"),
            self.prefix + "/api/" + "groups/XY890/custominformation/bla",
        )

    def test_gettransactionsurl(self):
        self.assertEqual(
            mambuutil.gettransactionsurl(idcred="12345"),
            self.prefix + "/api/" + "loans/12345/transactions",
        )
        self.assertEqual(
            mambuutil.gettransactionsurl("12345"),
            self.prefix + "/api/" + "loans/12345/transactions",
        )
        self.assertEqual(
            mambuutil.gettransactionsurl(idcred="12345", offset=10),
            self.prefix + "/api/" + "loans/12345/transactions?offset=10",
        )
        self.assertEqual(
            mambuutil.gettransactionsurl(idcred="12345", limit=10),
            self.prefix + "/api/" + "loans/12345/transactions?limit=10",
        )
        self.assertEqual(
            mambuutil.gettransactionsurl(idcred="12345", offset=2, limit=0),
            self.prefix + "/api/" + "loans/12345/transactions?offset=2&limit=0",
        )

        self.assertEqual(
            mambuutil.gettransactionsurl(idcred="12345", anything="whatever"),
            self.prefix + "/api/" + "loans/12345/transactions",
        )

    def test_getclienturl(self):
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123",
        )
        self.assertEqual(
            mambuutil.getclienturl("ABC123"), self.prefix + "/api/" + "clients/ABC123"
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient=""), self.prefix + "/api/" + "clients"
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", fullDetails=True),
            self.prefix + "/api/" + "clients/ABC123?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", fullDetails=False),
            self.prefix + "/api/" + "clients/ABC123?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", fullDetails=None),
            self.prefix + "/api/" + "clients/ABC123?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", fullDetails="whatever"),
            self.prefix + "/api/" + "clients/ABC123?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", offset=10),
            self.prefix + "/api/" + "clients/ABC123?offset=10",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", limit=10),
            self.prefix + "/api/" + "clients/ABC123?limit=10",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", firstName="FULANO"),
            self.prefix + "/api/" + "clients/ABC123?firstName=FULANO",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", lastName="DE TAL"),
            self.prefix + "/api/" + "clients/ABC123?lastName=DE TAL",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", idDocument="ABCD123456HDFABC00"),
            self.prefix + "/api/" + "clients/ABC123?idDocument=ABCD123456HDFABC00",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", birthdate="1980-01-01"),
            self.prefix + "/api/" + "clients/ABC123?birthdate=1980-01-01",
        )
        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", state="ACTIVE"),
            self.prefix + "/api/" + "clients/ABC123?state=ACTIVE",
        )
        self.assertEqual(
            mambuutil.getclienturl(
                idclient="ABC123",
                fullDetails=True,
                state="INACTIVE",
                firstName="FULANA",
                lastName="DE TAL",
                idDocument="WXYZ098765MDFXYZ99",
                birthdate="1981-12-31",
                offset=2,
                limit=0,
            ),
            self.prefix
            + "/api/"
            + "clients/ABC123?fullDetails=true&firstName=FULANA&lastName=DE TAL&idDocument=WXYZ098765MDFXYZ99&birthdat\
e=1981-12-31&state=INACTIVE&offset=2&limit=0",
        )

        self.assertEqual(
            mambuutil.getclienturl(idclient="ABC123", anything="whatever"),
            self.prefix + "/api/" + "clients/ABC123",
        )

    def test_getclientcustominformationurl(self):
        self.assertEqual(
            mambuutil.getclientcustominformationurl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123/custominformation",
        )
        self.assertEqual(
            mambuutil.getclientcustominformationurl(idclient="ABC123", customfield="bla"),
            self.prefix + "/api/" + "clients/ABC123/custominformation/bla",
        )

    def test_getclientloansurl(self):
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123/loans",
        )
        self.assertEqual(
            mambuutil.getclientloansurl("ABC123"),
            self.prefix + "/api/" + "clients/ABC123/loans",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient=""),
            self.prefix + "/api/" + "clients//loans",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", fullDetails=True),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", fullDetails=False),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", fullDetails=None),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", fullDetails="whatever"),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", accountState="ACTIVE"),
            self.prefix + "/api/" + "clients/ABC123/loans?accountState=ACTIVE",
        )

        self.assertEqual(
            mambuutil.getclientloansurl(
                idclient="ABC123", fullDetails=True, accountState="CLOSED_WRITTEN_OFF"
            ),
            self.prefix
            + "/api/"
            + "clients/ABC123/loans?fullDetails=true&accountState=CLOSED_WRITTEN_OFF",
        )

        self.assertEqual(
            mambuutil.getclientloansurl(idclient="ABC123", anything="whatever"),
            self.prefix + "/api/" + "clients/ABC123/loans",
        )

    def test_getuserurl(self):
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe"), self.prefix + "/api/" + "users/j.doe"
        )
        self.assertEqual(
            mambuutil.getuserurl("j.doe"), self.prefix + "/api/" + "users/j.doe"
        )
        self.assertEqual(mambuutil.getuserurl(iduser=""), self.prefix + "/api/" + "users")
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", fullDetails=True),
            self.prefix + "/api/" + "users/j.doe?fullDetails=true",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", fullDetails=False),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", fullDetails=None),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", fullDetails="whatever"),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", offset=10),
            self.prefix + "/api/" + "users/j.doe?offset=10",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", limit=10),
            self.prefix + "/api/" + "users/j.doe?limit=10",
        )
        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", branchId="CCCC"),
            self.prefix + "/api/" + "users/j.doe?branchId=CCCC",
        )
        self.assertEqual(
            mambuutil.getuserurl(
                iduser="j.doe", fullDetails=True, branchId="CCCC", offset=2, limit=0
            ),
            self.prefix
            + "/api/"
            + "users/j.doe?fullDetails=true&branchId=CCCC&offset=2&limit=0",
        )

        self.assertEqual(
            mambuutil.getuserurl(iduser="j.doe", anything="whatever"),
            self.prefix + "/api/" + "users/j.doe",
        )

    def test_getproductsurl(self):
        self.assertEqual(
            mambuutil.getproductsurl(idproduct="PROD-1"),
            self.prefix + "/api/" + "loanproducts/PROD-1",
        )
        self.assertEqual(
            mambuutil.getproductsurl("PROD-1"),
            self.prefix + "/api/" + "loanproducts/PROD-1",
        )
        self.assertEqual(
            mambuutil.getproductsurl(idproduct=""),
            self.prefix + "/api/" + "loanproducts",
        )

    def test_gettasksurl(self):
        self.assertEqual(mambuutil.gettasksurl(), self.prefix + "/api/" + "tasks")
        self.assertEqual(
            mambuutil.gettasksurl(username="auser"),
            self.prefix + "/api/" + "tasks?username=auser&status=OPEN",
        )
        self.assertEqual(
            mambuutil.gettasksurl(clientId="ABC123"),
            self.prefix + "/api/" + "tasks?clientid=ABC123&status=OPEN",
        )
        self.assertEqual(
            mambuutil.gettasksurl(groupId="XY890"),
            self.prefix + "/api/" + "tasks?groupid=XY890&status=OPEN",
        )
        self.assertEqual(
            mambuutil.gettasksurl(status="COMPLETED"),
            self.prefix + "/api/" + "tasks?status=COMPLETED",
        )
        self.assertEqual(
            mambuutil.gettasksurl(offset=10),
            self.prefix + "/api/" + "tasks?status=OPEN&offset=10",
        )
        self.assertEqual(
            mambuutil.gettasksurl(limit=10),
            self.prefix + "/api/" + "tasks?status=OPEN&limit=10",
        )
        self.assertEqual(
            mambuutil.gettasksurl(
                username="auser",
                clientId="ABC123",
                groupId="XY890",
                status="OVERDUE",
                offset=2,
                limit=0,
            ),
            self.prefix
            + "/api/"
            + "tasks?username=auser&clientid=ABC123&groupid=XY890&status=OVERDUE&offset=2&limit=0",
        )

    def test_getactivitiesurl(self):
        self.assertEqual(
            mambuutil.getactivitiesurl(), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(dummyId=""), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(""), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(dummyId="whatever"),
            self.prefix + "/api/" + "activities",
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(fromDate="2018-01-01"),
            self.prefix
            + "/api/"
            + "activities?from=2018-01-01&to={}".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(toDate="2018-01-31"),
            self.prefix + "/api/" + "activities?from=1900-01-01&to=2018-01-31",
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(branchId="CCCC"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&branchID=CCCC".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(clientId="ABC123"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&clientID=ABC123".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(centreId="CCCC"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&centreID=CCCC".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(userId="j.doe"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&userID=j.doe".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(loanAccountId="12345"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&loanAccountID=12345".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(groupId="XYZ890"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&groupID=XYZ890".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )
        self.assertEqual(
            mambuutil.getactivitiesurl(limit=10),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&limit=10".format(
                datetime.now().strftime("%Y-%m-%d")
            ),
        )

        self.assertEqual(
            mambuutil.getactivitiesurl(
                fromDate="2018-01-01",
                toDate="2018-01-31",
                branchId="CCCC",
                clientId="ABC123",
                centreId="CCCC",
                userId="j.doe",
                loanAccountId="12345",
                groupId="XYZ890",
                limit=0,
            ),
            self.prefix
            + "/api/"
            + "activities?from=2018-01-01&to=2018-01-31&branchID=CCCC&clientID=ABC123&centreID=CCCC&userID=j.doe&loanA\
ccountID=12345&groupID=XYZ890&limit=0",
        )

    def test_getrolesurl(self):
        self.assertEqual(mambuutil.getrolesurl(), self.prefix + "/api/" + "userroles")
        self.assertEqual(
            mambuutil.getrolesurl("ABC123"), self.prefix + "/api/" + "userroles/ABC123"
        )
        self.assertEqual(
            mambuutil.getrolesurl(idrole="ABC123"),
            self.prefix + "/api/" + "userroles/ABC123",
        )

    def test_getpostdocumentsurl(self):
        self.assertEqual(
            mambuutil.getpostdocumentsurl(), self.prefix + "/api/" + "documents"
        )
        self.assertEqual(
            mambuutil.getpostdocumentsurl("123"), self.prefix + "/api/" + "documents"
        )

    def test_getusercustominformationurl(self):
        self.assertEqual(
            mambuutil.getusercustominformationurl("456"),
            self.prefix + "/api/" + "users/456/custominformation",
        )
        self.assertEqual(
            mambuutil.getusercustominformationurl("456", customfield="test"),
            self.prefix + "/api/" + "users/456/custominformation/test",
        )

    def test_getsavingsurl(self):
        self.assertEqual(
            mambuutil.getsavingssurl(
                "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
            self.prefix + "/api/" + "savings/12345?fullDetails=true&offset=0&limit=0",
        )

    def test_getsavingfundingrepaymentsurl(self):
        self.assertEqual(
            mambuutil.getsavingfundingrepaymentsurl(
                "12345", "54321", **{"fullDetails": True, "offset": 0, "limit": 0}),
            self.prefix + "/api/" + "savings/12345/funding/54321/repayments?fullDetails=true&offset=0&limit=0",
        )

    def test_getsavingstransactionsurl(self):
        self.assertEqual(
            mambuutil.getsavingstransactionsurl(
                "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
            self.prefix + "/api/" + "savings/12345/transactions/?fullDetails=true&offset=0&limit=0",
        )

    def test_getsavingstransactionssearchurl(self):
        self.assertEqual(
            mambuutil.getsavingstransactionssearchurl(
                "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
            self.prefix + "/api/" + "savings/transactions/search?fullDetails=true&offset=0&limit=0",
        )

    def test_gettransactionchannelsurl(self):
        self.assertEqual(
            mambuutil.gettransactionchannelsurl(
                "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
            self.prefix + "/api/" + "transactionchannels/12345?fullDetails=true&offset=0&limit=0",
        )


if __name__ == "__main__":
    unittest.main()
