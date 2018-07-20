# coding: utf-8

import mock
import unittest
from datetime import datetime

import mambuutil


class MambuUtilTests(unittest.TestCase):
    def test_attrs(self):
        for atr in ["apiurl", "apiuser", "apipwd", "dbname", "dbuser", "dbpwd", "dbhost", "dbport", "dbeng",
                    "OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE",
                    "MambuError", "MambuCommError"]:
            try:
                getattr(mambuutil, atr)
            except AttributeError:
                self.fail("attribute missing on mambuutil: {}".format(atr))

    def test_constants(self):
        self.assertEqual(mambuutil.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE, 500)

    def test_error_attrs(self):
        self.assertEqual(mambuutil.MambuError.__bases__, (Exception,))
        self.assertEqual(mambuutil.MambuCommError.__bases__, (mambuutil.MambuError,))

    @mock.patch("mambuutil.create_engine")
    def test_connectDB(self, mock_create_engine):
        mock_create_engine.return_value = "test_connectDB"
        en = mambuutil.connectDb()
        self.assertEqual(en, "test_connectDB")
        mock_create_engine.assert_called_once_with("mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db?charset=utf8&use_unicode=1", echo=False)

        mambuutil.connectDb(echoopt=True, params="")
        mock_create_engine.assert_called_with("mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db", echo=True)

        mambuutil.connectDb(engine="myeng", params="")
        mock_create_engine.assert_called_with("myeng://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db", echo=False)
        mambuutil.connectDb(user="myuser", params="")
        mock_create_engine.assert_called_with("mysql://myuser:mambu_db_pwd@localhost:3306/mambu_db", echo=False)
        mambuutil.connectDb(password="mypass", params="")
        mock_create_engine.assert_called_with("mysql://mambu_db_user:mypass@localhost:3306/mambu_db", echo=False)
        mambuutil.connectDb(host="myhost", params="")
        mock_create_engine.assert_called_with("mysql://mambu_db_user:mambu_db_pwd@myhost:3306/mambu_db", echo=False)
        mambuutil.connectDb(port="myport", params="")
        mock_create_engine.assert_called_with("mysql://mambu_db_user:mambu_db_pwd@localhost:myport/mambu_db", echo=False)
        mambuutil.connectDb(database="mydb", params="")
        mock_create_engine.assert_called_with("mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mydb", echo=False)

    def test_strip_tags(self):
        self.assertEqual(mambuutil.strip_tags("<html>some text</html>"), "some text")
        self.assertEqual(mambuutil.strip_tags("<html>some&nbsp;text</html>"), "some text")

    def test_strip_consecutive_repeated_chars(self):
        self.assertEqual(mambuutil.strip_consecutive_repeated_char("TEST   STRING", ' '), "TEST STRING")
        self.assertEqual(mambuutil.strip_consecutive_repeated_char("TTTEST STRING", 'T'), "TEST STRING")
        self.assertEqual(mambuutil.strip_consecutive_repeated_char("TEST STRINGGG", 'G'), "TEST STRING")
        self.assertEqual(mambuutil.strip_consecutive_repeated_char("TTTT", 'T'), "T")

    def test_iriToUri(self):
        self.assertEqual(mambuutil.iriToUri(u"https://domain.mambu.com/some_url"), "https://domain.mambu.com/some_url")
        self.assertEqual(mambuutil.iriToUri(u"https://domain.mambu.com/some_url/strange_name/having_ñ"), "https://domain.mambu.com/some_url/strange_name/having_%c3%b1")

    def test_encoded_dict(self):
        d = {
            'a' : 'no-utf',
            'b' : u'yes-utf',
            'c' : u'strange-char-ñ',
            }
        d2 = mambuutil.encoded_dict(d)
        self.assertEqual(d2['a'], 'no-utf')
        self.assertEqual(d2['b'], 'yes-utf')
        self.assertEqual(d2['c'], 'strange-char-ñ')

    @mock.patch('mambuutil.requests')
    @mock.patch('mambuutil.sleep')
    def test_backup_db(self, mock_sleep, mock_requests):
        import os
        try:
            os.remove("/tmp/out_test")
        except OSError:
            pass

        class response():
            def __init__(self, code, content):
                self.status_code = code
                self.content = content

        mock_requests.post.return_value = response(code=200, content="hello world")
        mock_requests.get.return_value = response(code=200, content="hello world")

        d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : True, output_fname="/tmp/out_test")
        self.assertEqual(d['callback'], 'da-callback')
        self.assertTrue(d['latest'])

        d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : False, retries=1, output_fname="/tmp/out_test", force_download_latest=True)
        self.assertEqual(d['callback'], 'da-callback')
        self.assertFalse(d['latest'])

        d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : True, output_fname="/tmp/out_test", verbose=True)
        self.assertEqual(d['callback'], 'da-callback')
        self.assertTrue(d['latest'])

        with self.assertRaisesRegexp(mambuutil.MambuError, r'Tired of waiting, giving up...') as e:
            d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : False, retries=5, output_fname="/tmp/out_test", verbose=True)

        mock_requests.post.return_value = response(code=404, content="hello world (not found)")
        with self.assertRaisesRegexp(mambuutil.MambuCommError, r'Error posting request for backup: hello world \(not found\)$') as e:
            d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : True, output_fname="/tmp/out_test", verbose=True)

        mock_requests.post.side_effect = Exception("something wrong")
        with self.assertRaisesRegexp(mambuutil.MambuError, r"Error requesting backup: Exception\('something wrong',\)") as e:
            d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : True, output_fname="/tmp/out_test", verbose=True)

        mock_requests.post.side_effect = [response(code=200, content="hello world")]
        mock_requests.get.return_value = response(code=404, content="hello world (not found)")
        with self.assertRaisesRegexp(mambuutil.MambuCommError, r'Error getting database backup: hello world \(not found\)$') as e:
            d = mambuutil.backup_db(callback="da-callback", bool_func=lambda : True, output_fname="/tmp/out_test", verbose=True)


class UrlFuncTests(unittest.TestCase):
    def setUp(self):
        self.prefix = "https://domain.mambu.com"

    def test_getmambuurl(self):
        self.assertEqual(mambuutil.getmambuurl(), self.prefix + "/api/")

    def test_getbranchesurl(self):
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC"), self.prefix + "/api/" + "branches/CCCC")
        self.assertEqual(mambuutil.getbranchesurl("CCCC"), self.prefix + "/api/" + "branches/CCCC")
        self.assertEqual(mambuutil.getbranchesurl(idbranch=""), self.prefix + "/api/" + "branches")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=True), self.prefix + "/api/" + "branches/CCCC?fullDetails=true")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=False), self.prefix + "/api/" + "branches/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=None), self.prefix + "/api/" + "branches/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", fullDetails="whatever"), self.prefix + "/api/" + "branches/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", offset=10), self.prefix + "/api/" + "branches/CCCC?offset=10")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", limit=10), self.prefix + "/api/" + "branches/CCCC?limit=10")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", anything="whatever"), self.prefix + "/api/" + "branches/CCCC")
        self.assertEqual(mambuutil.getbranchesurl(idbranch="CCCC", fullDetails=True, offset=2, limit=0), self.prefix + "/api/" + "branches/CCCC?fullDetails=true&offset=2&limit=0")

    def test_getcentresurl(self):
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC"), self.prefix + "/api/" + "centres/CCCC")
        self.assertEqual(mambuutil.getcentresurl("CCCC"), self.prefix + "/api/" + "centres/CCCC")
        self.assertEqual(mambuutil.getcentresurl(idcentre=""), self.prefix + "/api/" + "centres")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", fullDetails=True), self.prefix + "/api/" + "centres/CCCC?fullDetails=true")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", fullDetails=False), self.prefix + "/api/" + "centres/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", fullDetails=None), self.prefix + "/api/" + "centres/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", fullDetails="whatever"), self.prefix + "/api/" + "centres/CCCC?fullDetails=false")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", offset=10), self.prefix + "/api/" + "centres/CCCC?offset=10")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", limit=10), self.prefix + "/api/" + "centres/CCCC?limit=10")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", anything="whatever"), self.prefix + "/api/" + "centres/CCCC")
        self.assertEqual(mambuutil.getcentresurl(idcentre="CCCC", fullDetails=True, offset=2, limit=0), self.prefix + "/api/" + "centres/CCCC?fullDetails=true&offset=2&limit=0")

    def test_getrepaymentsurl(self):
        self.assertEqual(mambuutil.getrepaymentsurl(idcred="12345"), self.prefix + "/api/" + "loans/12345/repayments")
        self.assertEqual(mambuutil.getrepaymentsurl("12345"), self.prefix + "/api/" + "loans/12345/repayments")
        self.assertEqual(mambuutil.getrepaymentsurl(idcred=""), self.prefix + "/api/" + "loans//repayments")

    def test_getloansurl(self):
        self.assertEqual(mambuutil.getloansurl(idcred="12345"), self.prefix + "/api/" + "loans/12345")
        self.assertEqual(mambuutil.getloansurl("12345"), self.prefix + "/api/" + "loans/12345")
        self.assertEqual(mambuutil.getloansurl(idcred=""), self.prefix + "/api/" + "loans")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", fullDetails=True), self.prefix + "/api/" + "loans/12345?fullDetails=true")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", fullDetails=False), self.prefix + "/api/" + "loans/12345?fullDetails=false")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", fullDetails=None), self.prefix + "/api/" + "loans/12345?fullDetails=false")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", fullDetails="whatever"), self.prefix + "/api/" + "loans/12345?fullDetails=false")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", offset=10), self.prefix + "/api/" + "loans/12345?offset=10")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", limit=10), self.prefix + "/api/" + "loans/12345?limit=10")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", accountState="ACTIVE"), self.prefix + "/api/" + "loans/12345?accountState=ACTIVE")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", branchId="CCCC"), self.prefix + "/api/" + "loans/12345?branchId=CCCC")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", centreId="CCCC"), self.prefix + "/api/" + "loans/12345?centreId=CCCC")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", creditOfficerUsername="fulanito"), self.prefix + "/api/" + "loans/12345?creditOfficerUsername=fulanito")
        self.assertEqual(mambuutil.getloansurl(idcred="12345", fullDetails=True, accountState="ACTIVE_IN_ARREARS", branchId="CCCC", centreId="CCCC", creditOfficerUsername="fulanito", offset=2, limit=0), self.prefix + "/api/" + "loans/12345?fullDetails=true&accountState=ACTIVE_IN_ARREARS&branchId=CCCC&centreId=CCCC&creditOfficerUsername=fulanito&offset=2&limit=0")

        self.assertEqual(mambuutil.getloansurl(idcred="12345", anything="whatever"), self.prefix + "/api/" + "loans/12345")

    def test_getgroupurl(self):
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890"), self.prefix + "/api/" + "groups/XY890")
        self.assertEqual(mambuutil.getgroupurl("XY890"), self.prefix + "/api/" + "groups/XY890")
        self.assertEqual(mambuutil.getgroupurl(idgroup=""), self.prefix + "/api/" + "groups")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", fullDetails=True), self.prefix + "/api/" + "groups/XY890?fullDetails=true")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", fullDetails=False), self.prefix + "/api/" + "groups/XY890?fullDetails=false")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", fullDetails=None), self.prefix + "/api/" + "groups/XY890?fullDetails=false")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", fullDetails="whatever"), self.prefix + "/api/" + "groups/XY890?fullDetails=false")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", offset=10), self.prefix + "/api/" + "groups/XY890?offset=10")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", limit=10), self.prefix + "/api/" + "groups/XY890?limit=10")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", creditOfficerUsername="fulanito"), self.prefix + "/api/" + "groups/XY890?creditOfficerUsername=fulanito")
        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", fullDetails=True, creditOfficerUsername="fulanito", offset=2, limit=0), self.prefix + "/api/" + "groups/XY890?fullDetails=true&creditOfficerUsername=fulanito&limit=0&offset=2")

        self.assertEqual(mambuutil.getgroupurl(idgroup="XY890", anything="whatever"), self.prefix + "/api/" + "groups/XY890")

    def test_getgrouploansurl(self):
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890"), self.prefix + "/api/" + "groups/XY890/loans")
        self.assertEqual(mambuutil.getgrouploansurl("XY890"), self.prefix + "/api/" + "groups/XY890/loans")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup=""), self.prefix + "/api/" + "groups//loans")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=True), self.prefix + "/api/" + "groups/XY890/loans?fullDetails=true")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=False), self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=None), self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", fullDetails="whatever"), self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", accountState="ACTIVE"), self.prefix + "/api/" + "groups/XY890/loans?accountState=ACTIVE")
        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", fullDetails=True, accountState="CLOSED"), self.prefix + "/api/" + "groups/XY890/loans?fullDetails=true&accountState=CLOSED")

        self.assertEqual(mambuutil.getgrouploansurl(idgroup="XY890", anything="whatever"), self.prefix + "/api/" + "groups/XY890/loans")

    def test_getgroupcustominformationurl(self):
        self.assertEqual(mambuutil.getgroupcustominformationurl(idgroup="XY890"), self.prefix + "/api/"+ "groups/XY890/custominformation")
        self.assertEqual(mambuutil.getgroupcustominformationurl(idgroup="XY890", customfield="bla"), self.prefix + "/api/"+ "groups/XY890/custominformation/bla")

    def test_gettransactionsurl(self):
        self.assertEqual(mambuutil.gettransactionsurl(idcred="12345"), self.prefix + "/api/" + "loans/12345/transactions")
        self.assertEqual(mambuutil.gettransactionsurl("12345"), self.prefix + "/api/" + "loans/12345/transactions")
        self.assertEqual(mambuutil.gettransactionsurl(idcred="12345", offset=10), self.prefix + "/api/" + "loans/12345/transactions?offset=10")
        self.assertEqual(mambuutil.gettransactionsurl(idcred="12345", limit=10), self.prefix + "/api/" + "loans/12345/transactions?limit=10")
        self.assertEqual(mambuutil.gettransactionsurl(idcred="12345", offset=2, limit=0), self.prefix + "/api/" + "loans/12345/transactions?offset=2&limit=0")

        self.assertEqual(mambuutil.gettransactionsurl(idcred="12345", anything="whatever"), self.prefix + "/api/" + "loans/12345/transactions")

    def test_getclienturl(self):
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123"), self.prefix + "/api/" + "clients/ABC123")
        self.assertEqual(mambuutil.getclienturl("ABC123"), self.prefix + "/api/" + "clients/ABC123")
        self.assertEqual(mambuutil.getclienturl(idclient=""), self.prefix + "/api/" + "clients")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", fullDetails=True), self.prefix + "/api/" + "clients/ABC123?fullDetails=true")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", fullDetails=False), self.prefix + "/api/" + "clients/ABC123?fullDetails=false")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", fullDetails=None), self.prefix + "/api/" + "clients/ABC123?fullDetails=false")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", fullDetails="whatever"), self.prefix + "/api/" + "clients/ABC123?fullDetails=false")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", offset=10), self.prefix + "/api/" + "clients/ABC123?offset=10")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", limit=10), self.prefix + "/api/" + "clients/ABC123?limit=10")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", firstName="FULANO"), self.prefix + "/api/" + "clients/ABC123?firstName=FULANO")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", lastName="DE TAL"), self.prefix + "/api/" + "clients/ABC123?lastName=DE TAL")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", idDocument="ABCD123456HDFABC00"), self.prefix + "/api/" + "clients/ABC123?idDocument=ABCD123456HDFABC00")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", birthdate="1980-01-01"), self.prefix + "/api/" + "clients/ABC123?birthdate=1980-01-01")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", state="ACTIVE"), self.prefix + "/api/" + "clients/ABC123?state=ACTIVE")
        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", fullDetails=True, state="INACTIVE", firstName="FULANA", lastName="DE TAL", idDocument="WXYZ098765MDFXYZ99", birthdate="1981-12-31", offset=2, limit=0), self.prefix + "/api/" + "clients/ABC123?fullDetails=true&firstName=FULANA&lastName=DE TAL&idDocument=WXYZ098765MDFXYZ99&birthdate=1981-12-31&state=INACTIVE&offset=2&limit=0")

        self.assertEqual(mambuutil.getclienturl(idclient="ABC123", anything="whatever"), self.prefix + "/api/" + "clients/ABC123")

    def test_getgroupcustominformationurl(self):
        self.assertEqual(mambuutil.getclientcustominformationurl(idclient="ABC123"), self.prefix + "/api/"+ "clients/ABC123/custominformation")
        self.assertEqual(mambuutil.getclientcustominformationurl(idclient="ABC123", customfield="bla"), self.prefix + "/api/"+ "clients/ABC123/custominformation/bla")

    def test_getclientloansurl(self):
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123"), self.prefix + "/api/" + "clients/ABC123/loans")
        self.assertEqual(mambuutil.getclientloansurl("ABC123"), self.prefix + "/api/" + "clients/ABC123/loans")
        self.assertEqual(mambuutil.getclientloansurl(idclient=""), self.prefix + "/api/" + "clients//loans")
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", fullDetails=True), self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=true")
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", fullDetails=False), self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false")
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", fullDetails=None), self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false")
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", fullDetails="whatever"), self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false")
        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", accountState="ACTIVE"), self.prefix + "/api/" + "clients/ABC123/loans?accountState=ACTIVE")

        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", fullDetails=True, accountState="CLOSED_WRITTEN_OFF"), self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=true&accountState=CLOSED_WRITTEN_OFF")

        self.assertEqual(mambuutil.getclientloansurl(idclient="ABC123", anything="whatever"), self.prefix + "/api/" + "clients/ABC123/loans")

    def test_getuserurl(self):
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe"), self.prefix + "/api/" + "users/j.doe")
        self.assertEqual(mambuutil.getuserurl("j.doe"), self.prefix + "/api/" + "users/j.doe")
        self.assertEqual(mambuutil.getuserurl(iduser=""), self.prefix + "/api/" + "users")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", fullDetails=True), self.prefix + "/api/" + "users/j.doe?fullDetails=true")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", fullDetails=False), self.prefix + "/api/" + "users/j.doe?fullDetails=false")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", fullDetails=None), self.prefix + "/api/" + "users/j.doe?fullDetails=false")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", fullDetails="whatever"), self.prefix + "/api/" + "users/j.doe?fullDetails=false")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", offset=10), self.prefix + "/api/" + "users/j.doe?offset=10")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", limit=10), self.prefix + "/api/" + "users/j.doe?limit=10")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", branchId="CCCC"), self.prefix + "/api/" + "users/j.doe?branchId=CCCC")
        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", fullDetails=True, branchId="CCCC", offset=2, limit=0), self.prefix + "/api/" + "users/j.doe?fullDetails=true&branchId=CCCC&offset=2&limit=0")

        self.assertEqual(mambuutil.getuserurl(iduser="j.doe", anything="whatever"), self.prefix + "/api/" + "users/j.doe")

    def test_getproductsurl(self):
        self.assertEqual(mambuutil.getproductsurl(idproduct="PROD-1"), self.prefix + "/api/" + "loanproducts/PROD-1")
        self.assertEqual(mambuutil.getproductsurl("PROD-1"), self.prefix + "/api/" + "loanproducts/PROD-1")
        self.assertEqual(mambuutil.getproductsurl(idproduct=""), self.prefix + "/api/" + "loanproducts")

    def test_gettasksurl(self):
        self.assertEqual(mambuutil.gettasksurl(), self.prefix + "/api/" + "tasks")
        self.assertEqual(mambuutil.gettasksurl(username='auser'), self.prefix + "/api/" + "tasks?username=auser&status=OPEN")
        self.assertEqual(mambuutil.gettasksurl(clientId='ABC123'), self.prefix + "/api/" + "tasks?clientid=ABC123&status=OPEN")
        self.assertEqual(mambuutil.gettasksurl(groupId='XY890'), self.prefix + "/api/" + "tasks?groupid=XY890&status=OPEN")
        self.assertEqual(mambuutil.gettasksurl(status='COMPLETED'), self.prefix + "/api/" + "tasks?status=COMPLETED")
        self.assertEqual(mambuutil.gettasksurl(username='auser', clientId='ABC123', groupId='XY890', status='OVERDUE'), self.prefix + "/api/" + "tasks?username=auser&clientid=ABC123&groupid=XY890&status=OVERDUE")

    def test_getactivitiesurl(self):
        self.assertEqual(mambuutil.getactivitiesurl(), self.prefix + "/api/" + "activities")
        self.assertEqual(mambuutil.getactivitiesurl(dummyId=""), self.prefix + "/api/" + "activities")
        self.assertEqual(mambuutil.getactivitiesurl(""), self.prefix + "/api/" + "activities")
        self.assertEqual(mambuutil.getactivitiesurl(dummyId="whatever"), self.prefix + "/api/" + "activities")
        self.assertEqual(mambuutil.getactivitiesurl(fromDate="2018-01-01"), self.prefix + "/api/" + "activities?from=2018-01-01&to={}".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(toDate="2018-01-31"), self.prefix + "/api/" + "activities?from=1900-01-01&to=2018-01-31")
        self.assertEqual(mambuutil.getactivitiesurl(branchId="CCCC"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&branchID=CCCC".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(clientId="ABC123"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&clientID=ABC123".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(centreId="CCCC"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&centreID=CCCC".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(userId="j.doe"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&userID=j.doe".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(loanAccountId="12345"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&loanAccountID=12345".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(groupId="XYZ890"), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&groupID=XYZ890".format(datetime.now().strftime("%Y-%m-%d")))
        self.assertEqual(mambuutil.getactivitiesurl(limit=10), self.prefix + "/api/" + "activities?from=1900-01-01&to={}&limit=10".format(datetime.now().strftime("%Y-%m-%d")))

        self.assertEqual(mambuutil.getactivitiesurl(fromDate="2018-01-01", toDate="2018-01-31", branchId="CCCC", clientId="ABC123", centreId="CCCC", userId="j.doe", loanAccountId="12345", groupId="XYZ890", limit=0), self.prefix + "/api/" + "activities?from=2018-01-01&to=2018-01-31&branchID=CCCC&clientID=ABC123&centreID=CCCC&userID=j.doe&loanAccountID=12345&groupID=XYZ890&limit=0")

    def test_getrolesurl(self):
        self.assertEqual(mambuutil.getrolesurl(), self.prefix + "/api/" + "userroles")
        self.assertEqual(mambuutil.getrolesurl("ABC123"), self.prefix + "/api/" + "userroles/ABC123")
        self.assertEqual(mambuutil.getrolesurl(idrole="ABC123"), self.prefix + "/api/" + "userroles/ABC123")


if __name__ == '__main__':
    unittest.main()
