# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import unittest
from datetime import datetime

from MambuPy import mambuconfig
from MambuPy import mambugeturl

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy import mambugeturl

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


class UrlFuncTests(unittest.TestCase):
    def url_to_compare(self, result_of_functions, params_of_functions):
        return [parameter for parameter in params_of_functions if parameter in result_of_functions]

    def setUp(self):
        self.prefix = "https://domain.mambu.com"

    def test_getmambuurl(self):
        self.assertEqual(mambugeturl.getmambuurl(), self.prefix + "/api/")

    def test_getbranchesurl(self):
        result_getbranchesurl = mambugeturl.getbranchesurl(idbranch="CCCC", fullDetails=True, limit=0, offset=2)
        self.assertEqual(
            mambugeturl.getbranchesurl(idbranch="CCCC"),
            self.prefix + "/api/" + "branches/CCCC",
        )
        self.assertEqual(
            mambugeturl.getbranchesurl(
                "CCCC"), self.prefix + "/api/" + "branches/CCCC"
        )
        self.assertEqual(
            mambugeturl.getbranchesurl(
                idbranch=""), self.prefix + "/api/" + "branches"
        )
        self.assertTrue("fullDetails=true" in result_getbranchesurl)
        self.assertTrue("limit=0" in result_getbranchesurl)
        self.assertTrue("offset=2" in result_getbranchesurl)

        params_branchesurl = ["fullDetails=true", "limit=0", "offset=2"]
        x = self.url_to_compare(result_getbranchesurl, params_branchesurl)
        self.assertEqual(self.prefix + "/api/" + "branches/CCCC?"+x[0]+"&"+x[1]+"&"+x[2],
            self.prefix + "/api/" + "branches/CCCC?fullDetails=true&limit=0&offset=2"
        )

    def test_getcentresurl(self):
        result_getcentresurl = mambugeturl.getcentresurl(idcentre="CCCC", fullDetails=True,limit=0,offset=2)
        self.assertEqual(
            mambugeturl.getcentresurl(idcentre="CCCC"),
            self.prefix + "/api/" + "centres/CCCC",
        )
        self.assertEqual(
            mambugeturl.getcentresurl("CCCC"), self.prefix +
            "/api/" + "centres/CCCC"
        )
        self.assertEqual(
            mambugeturl.getcentresurl(
                idcentre=""), self.prefix + "/api/" + "centres"
        )
        self.assertTrue("fullDetails=true" in result_getcentresurl)
        self.assertTrue("limit=0" in result_getcentresurl)
        self.assertTrue("offset=2" in result_getcentresurl)

        params_centresurl = ["fullDetails=true", "limit=0", "offset=2"]
        x = self.url_to_compare(result_getcentresurl, params_centresurl)
        self.assertEqual(self.prefix + "/api/" + "branches/CCCC?"+x[0]+"&"+x[1]+"&"+x[2],
            self.prefix + "/api/" + "branches/CCCC?fullDetails=true&limit=0&offset=2"
        )

    def test_getrepaymentsurl(self):
        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred="12345"),
            self.prefix + "/api/" + "loans/12345/repayments",
        )
        self.assertEqual(
            mambugeturl.getrepaymentsurl("12345"),
            self.prefix + "/api/" + "loans/12345/repayments",
        )
        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred=""),
            self.prefix + "/api/" + "loans//repayments",
        )

        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred="12345", fullDetails=True),
            self.prefix + "/api/" + "loans/12345/repayments?fullDetails=true",
        )
        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred="12345", fullDetails=False),
            self.prefix + "/api/" + "loans/12345/repayments?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred="12345", offset=10),
            self.prefix + "/api/" + "loans/12345/repayments?offset=10",
        )
        self.assertEqual(
            mambugeturl.getrepaymentsurl(idcred="12345", limit=10),
            self.prefix + "/api/" + "loans/12345/repayments?limit=10",
        )

    def test_getloansurl(self):
        result_getloansurl = mambugeturl.getrepaymentsurl(idcred="12345", fullDetails=False, accountState="ACTIVE",
            branchId="CCCC", centreId="DDDD", creditOfficerUsername="fulanito", limit=0,offset=1)
        self.assertEqual(
            mambugeturl.getloansurl(
                idcred="12345"), self.prefix + "/api/" + "loans/12345"
        )
        self.assertEqual(
            mambugeturl.getloansurl("12345"), self.prefix +
            "/api/" + "loans/12345"
        )
        self.assertEqual(
            mambugeturl.getloansurl(idcred=""), self.prefix + "/api/" + "loans"
        )
        self.assertTrue("fullDetails=false" in result_getloansurl)
        self.assertTrue("accountState=ACTIVE" in result_getloansurl)
        self.assertTrue("limit=0" in result_getloansurl)
        self.assertTrue("offset=1" in result_getloansurl)

        params_loansurl = ["fullDetails=false", "accountState=ACTIVE", "branchId=CCCC", "centreId=DDDD",
            "creditOfficerUsername=fulanito", "limit=0","offset=1"]
        x = self.url_to_compare(result_getloansurl, params_loansurl)
        self.assertEqual(self.prefix + "/api/" + "loans/12345/repayments?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3]+"&"+x[4]+
            "&"+x[5]+"&"+x[6],
            self.prefix + "/api/" + "loans/12345/repayments?fullDetails=false&accountState=ACTIVE&branchId=CCCC&centre\
Id=DDDD&creditOfficerUsername=fulanito&limit=0&offset=1")

    def test_getloanscustominformationurl(self):
        self.assertEqual(
            mambugeturl.getloanscustominformationurl("loanID123"),
            self.prefix + "/api/" + "loans/loanID123/custominformation",
        )
        self.assertEqual(
            mambugeturl.getloanscustominformationurl(
                "loanID123", customfield="bla"),
            self.prefix + "/api/" + "loans/loanID123/custominformation/bla",
        )

    def test_getgroupurl(self):
        result_getgroupurl = mambugeturl.getgroupurl(idgroup="XY890",fullDetails=True,creditOfficerUsername="fulanito",
            branchId="BRANCH",centreId="CENTRE",limit=0,offset=1,
        )
        self.assertEqual(
            mambugeturl.getgroupurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890",
        )
        self.assertEqual(
            mambugeturl.getgroupurl("XY890"), self.prefix +
            "/api/" + "groups/XY890"
        )
        self.assertEqual(
            mambugeturl.getgroupurl(idgroup=""), self.prefix + "/api/" + "groups"
        )
        self.assertTrue("fullDetails=true" in result_getgroupurl)
        self.assertTrue("creditOfficerUsername=fulanito" in result_getgroupurl)
        self.assertTrue("branchId=BRANCH" in result_getgroupurl)
        self.assertTrue("centreId=CENTRE" in result_getgroupurl)
        self.assertTrue("limit=0" in result_getgroupurl)
        self.assertTrue("offset=1" in result_getgroupurl)

        params_groupurl = ["fullDetails=true","creditOfficerUsername=fulanito","branchId=BRANCH","centreId=CENTRE",
            "limit=0","offset=1"]
        x = self.url_to_compare(result_getgroupurl, params_groupurl)
        self.assertEqual(self.prefix + "/api/" + "groups/XY890?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3]+"&"+x[4]+"&"+x[5],
                         self.prefix + "/api/" + "groups/XY890?fullDetails=true&creditOfficerUsername=fulanito&branchI\
d=BRANCH&centreId=CENTRE&limit=0&offset=1",
        )

    def test_getgrouploansurl(self):
        result_getgrouploansurl = mambugeturl.getgrouploansurl(idgroup="XY890", fullDetails=True, accountState="CLOSED")
        self.assertEqual(
            mambugeturl.getgrouploansurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890/loans",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl("XY890"),
            self.prefix + "/api/" + "groups/XY890/loans",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl(idgroup=""),
            self.prefix + "/api/" + "groups//loans",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl(idgroup="XY890", fullDetails=True),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=true",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl(idgroup="XY890", fullDetails=False),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl(idgroup="XY890", fullDetails=None),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getgrouploansurl(
                idgroup="XY890", fullDetails="whatever"),
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=false",
        )
        self.assertTrue("fullDetails=true" in result_getgrouploansurl)
        self.assertTrue("accountState=CLOSED" in result_getgrouploansurl)

        params_grouploansurl = ["fullDetails=true", "accountState=CLOSED"]
        x = self.url_to_compare(result_getgrouploansurl, params_grouploansurl)
        self.assertEqual(self.prefix + "/api/" + "groups/XY890/loans?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "groups/XY890/loans?fullDetails=true&accountState=CLOSED",
        )

    def test_getgroupcustominformationurl(self):
        self.assertEqual(
            mambugeturl.getgroupcustominformationurl(idgroup="XY890"),
            self.prefix + "/api/" + "groups/XY890/custominformation",
        )
        self.assertEqual(
            mambugeturl.getgroupcustominformationurl(
                idgroup="XY890", customfield="bla"),
            self.prefix + "/api/" + "groups/XY890/custominformation/bla",
        )

    def test_gettransactionsurl(self):
        rest_gettransactionsurl = mambugeturl.gettransactionsurl(idcred="12345", offset=2, limit=0)
        self.assertEqual(
            mambugeturl.gettransactionsurl(idcred="12345"),
            self.prefix + "/api/" + "loans/12345/transactions",
        )
        self.assertEqual(
            mambugeturl.gettransactionsurl("12345"),
            self.prefix + "/api/" + "loans/12345/transactions",
        )
        self.assertTrue("offset=2" in rest_gettransactionsurl)
        self.assertTrue("limit=0" in rest_gettransactionsurl)

        params_gettransactionsurl = ["offset=2", "limit=0"]
        x = self.url_to_compare(rest_gettransactionsurl, params_gettransactionsurl)
        self.assertEqual(self.prefix + "/api/" + "loans/12345/transactions?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "loans/12345/transactions?offset=2&limit=0",
        )

    def test_getclienturl(self):
        result_getclienturl = mambugeturl.getclienturl(idclient="ABC123",fullDetails=True,firstName="FULANO",
        lastName="DE TAL",idDocument="ABCD123456HDFABC00",birthdate="1980-01-01",state="ACTIVE",offset=10,limit=10,)
        self.assertEqual(
            mambugeturl.getclienturl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123",
        )
        self.assertEqual(
            mambugeturl.getclienturl("ABC123"), self.prefix +
            "/api/" + "clients/ABC123"
        )
        self.assertEqual(
            mambugeturl.getclienturl(
                idclient=""), self.prefix + "/api/" + "clients"
        )
        self.assertEqual(
            mambugeturl.getclienturl(idclient="ABC123", anything="whatever"),
            self.prefix + "/api/" + "clients/ABC123?anything=whatever",
        )
        self.assertTrue("fullDetails=true" in result_getclienturl)
        self.assertTrue("offset=10" in result_getclienturl)
        self.assertTrue("limit=10" in result_getclienturl)
        self.assertTrue("firstName=FULANO" in result_getclienturl)
        self.assertTrue("lastName=DE TAL" in result_getclienturl)
        self.assertTrue("idDocument=ABCD123456HDFABC00" in result_getclienturl)
        self.assertTrue("birthdate=1980-01-01" in result_getclienturl)
        self.assertTrue("state=ACTIVE" in result_getclienturl)

        params_clienturl = ["fullDetails=true","firstName=FULANO","lastName=DE TAL","idDocument=ABCD123456HDFABC00",
            "birthdate=1980-01-01","state=ACTIVE","offset=10","limit=10"]
        x = self.url_to_compare(result_getclienturl, params_clienturl)
        self.assertEqual(self.prefix + "/api/" + "clients/ABC123?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3]+"&"+x[4]+"&"+x[5]+
            "&"+x[6]+"&"+x[7],
            self.prefix
            + "/api/"
            + "clients/ABC123?fullDetails=true&firstName=FULANO&lastName=DE TAL&idDocument=ABCD123456HDFABC00&birthdat\
e=1980-01-01&state=ACTIVE&offset=10&limit=10",
        )

    def test_getclientcustominformationurl(self):
        self.assertEqual(
            mambugeturl.getclientcustominformationurl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123/custominformation",
        )
        self.assertEqual(
            mambugeturl.getclientcustominformationurl(
                idclient="ABC123", customfield="bla"),
            self.prefix + "/api/" + "clients/ABC123/custominformation/bla",
        )

    def test_getclientloansurl(self):
        result_getclientloansurl = mambugeturl.getclientloansurl(
            idclient="ABC123",
            fullDetails=True,
            accountState="CLOSED_WRITTEN_OFF"
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(idclient="ABC123"),
            self.prefix + "/api/" + "clients/ABC123/loans",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl("ABC123"),
            self.prefix + "/api/" + "clients/ABC123/loans",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(idclient=""),
            self.prefix + "/api/" + "clients//loans",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(idclient="ABC123", fullDetails=True),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=true",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(idclient="ABC123", fullDetails=False),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(idclient="ABC123", fullDetails=None),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(
                idclient="ABC123", fullDetails="whatever"),
            self.prefix + "/api/" + "clients/ABC123/loans?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(
                idclient="ABC123", accountState="ACTIVE"),
            self.prefix + "/api/" + "clients/ABC123/loans?accountState=ACTIVE",
        )
        self.assertEqual(
            mambugeturl.getclientloansurl(
                idclient="ABC123", anything="whatever"),
            self.prefix + "/api/" + "clients/ABC123/loans?anything=whatever",
        )

        params_clientloansurl = ["fullDetails=true", "accountState=CLOSED_WRITTEN_OFF"]
        x = self.url_to_compare(result_getclientloansurl, params_clientloansurl)
        self.assertEqual(self.prefix
            + "/api/"
            + "clients/ABC123/loans?"+x[0]+"&"+x[1],
            self.prefix
            + "/api/"
            + "clients/ABC123/loans?fullDetails=true&accountState=CLOSED_WRITTEN_OFF",
        )

    def test_getuserurl(self):
        result_getuserurl = mambugeturl.getuserurl(
            iduser="j.doe", fullDetails=True, branchId="CCCC", offset=2, limit=0
        )
        self.assertEqual(
            mambugeturl.getuserurl(
                iduser="j.doe"), self.prefix + "/api/" + "users/j.doe"
        )
        self.assertEqual(
            mambugeturl.getuserurl("j.doe"), self.prefix +
            "/api/" + "users/j.doe"
        )
        self.assertEqual(mambugeturl.getuserurl(iduser=""), self.prefix + "/api/" + "users"
                         )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", fullDetails=True),
            self.prefix + "/api/" + "users/j.doe?fullDetails=true",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", fullDetails=False),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", fullDetails=None),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", fullDetails="whatever"),
            self.prefix + "/api/" + "users/j.doe?fullDetails=false",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", offset=10),
            self.prefix + "/api/" + "users/j.doe?offset=10",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", limit=10),
            self.prefix + "/api/" + "users/j.doe?limit=10",)
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", branchId="CCCC"),
            self.prefix + "/api/" + "users/j.doe?branchId=CCCC",
        )
        self.assertEqual(
            mambugeturl.getuserurl(iduser="j.doe", anything="whatever"),
            self.prefix + "/api/" + "users/j.doe?anything=whatever",
        )
        params_userurl = ["fullDetails=true", "branchId=CCCC", "offset=2", "limit=0"]
        x = self.url_to_compare(result_getuserurl, params_userurl)
        self.assertEqual(self.prefix + "/api/" + "users/j.doe?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3],
            self.prefix + "/api/" + "users/j.doe?fullDetails=true&branchId=CCCC&offset=2&limit=0",
        )

    def test_getproductsurl(self):
        self.assertEqual(
            mambugeturl.getproductsurl(idproduct="PROD-1"),
            self.prefix + "/api/" + "loanproducts/PROD-1",
        )
        self.assertEqual(
            mambugeturl.getproductsurl("PROD-1"),
            self.prefix + "/api/" + "loanproducts/PROD-1",
        )
        self.assertEqual(
            mambugeturl.getproductsurl(idproduct=""),
            self.prefix + "/api/" + "loanproducts",
        )

    def test_gettasksurl(self):
        self.assertEqual(mambugeturl.gettasksurl(), self.prefix + "/api/" + "tasks")
        result_gettasksurl = mambugeturl.gettasksurl(username="auser", status="OPEN",)
        params_tasksurl = ["username=auser","status=OPEN"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "tasks?username=auser&status=OPEN",
        )
        result_gettasksurl = mambugeturl.gettasksurl(status="COMPLETED")
        params_tasksurl = ["status=COMPLETED"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0],
            self.prefix + "/api/" + "tasks?status=COMPLETED",
        )
        result_gettasksurl = mambugeturl.gettasksurl(status="OPEN",offset=10)
        params_tasksurl = ["status=OPEN","offset=10"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "tasks?status=OPEN&offset=10",
        )
        result_gettasksurl = mambugeturl.gettasksurl(status="OPEN",limit=10,)
        params_tasksurl = ["status=OPEN","limit=10"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "tasks?status=OPEN&limit=10",
        )
        result_gettasksurl = mambugeturl.gettasksurl(clientId="ABC123", status="OVERDUE")
        params_tasksurl = ["clientId=ABC123", "status=OVERDUE"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0]+"&"+x[1],
            self.prefix + "/api/" + "tasks?clientId=ABC123&status=OVERDUE",)
        result_gettasksurl = mambugeturl.gettasksurl(username="auser", clientId="ABC123", groupId="XY890",
            status="OVERDUE",offset=2, limit=0,)
        params_tasksurl = ["username=auser","clientId=ABC123", "groupId=XY890","status=OVERDUE","offset=2","limit=0"]
        x = self.url_to_compare(result_gettasksurl, params_tasksurl)
        self.assertEqual(self.prefix + "/api/" + "tasks?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3]+"&"+x[4]+"&"+x[5],
            self.prefix + "/api/" + "tasks?username=auser&clientId=ABC123&groupId=XY890&status=OVERDUE&offset=2&limit\
=0",
        )
    def test_getactivitiesurl(self):
        result_getactivitiesurl = mambugeturl.getactivitiesurl(fromDate="2018-01-01",toDate="2018-01-31",
            branchId="CCCC",clientId="ABC123",centreId="CCCC",userId="j.doe",loanAccountId="12345",groupId="XYZ890",
            limit=0
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(
                dummyId=""), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(
                ""), self.prefix + "/api/" + "activities"
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(dummyId="whatever"),
            self.prefix + "/api/" + "activities",
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(
                fromDate="2018-01-01", toDate=datetime.now().strftime("%Y-%m-%d")),
            self.prefix
            + "/api/"
            + "activities?from=2018-01-01&to={}".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(
                fromDate="1900-01-01", toDate="2018-01-31"),
            self.prefix + "/api/" + "activities?from=1900-01-01&to=2018-01-31",
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       branchId="CCCC"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&branchId=CCCC".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       clientId="ABC123"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&clientId=ABC123".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       centreId="CCCC"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&centreId=CCCC".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       userId="j.doe"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&userId=j.doe".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       loanAccountId="12345"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&loanAccountId=12345".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"),
                                       groupId="XYZ890"),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&groupId=XYZ890".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        self.assertEqual(
            mambugeturl.getactivitiesurl(
                fromDate="1900-01-01", toDate=datetime.now().strftime("%Y-%m-%d"), limit=10),
            self.prefix
            + "/api/"
            + "activities?from=1900-01-01&to={}&limit=10".format(
                datetime.now().strftime("%Y-%m-%d")),
        )
        params_activitiesurl = ["from=2018-01-01", "to=2018-01-31","branchId=CCCC","clientId=ABC123",
        "centreId=CCCC", "userId=j.doe", "loanAccountId=12345","groupId=XYZ890", "limit=0"]
        x = self.url_to_compare(result_getactivitiesurl, params_activitiesurl)
        self.assertEqual(self.prefix
            + "/api/"
            + "activities?"+x[0]+"&"+x[1]+"&"+x[2]+"&"+x[3]+"&"+x[4]+"&"+x[5]+"&"+x[6]+"&"+x[7]+"&"+x[8],
            self.prefix
            + "/api/"
            + "activities?from=2018-01-01&to=2018-01-31&branchId=CCCC&clientId=ABC123&centreId=CCCC&userId=j.doe&loanA\
ccountId=12345&groupId=XYZ890&limit=0",
        )

    def test_getrolesurl(self):
        self.assertEqual(mambugeturl.getrolesurl(), self.prefix + "/api/" + "userroles"
                         )
        self.assertEqual(
            mambugeturl.getrolesurl("ABC123"), self.prefix +
            "/api/" + "userroles/ABC123"
        )
        self.assertEqual(
            mambugeturl.getrolesurl(idrole="ABC123"),
            self.prefix + "/api/" + "userroles/ABC123",
        )

    def test_getpostdocumentsurl(self):
        self.assertEqual(
            mambugeturl.getpostdocumentsurl(), self.prefix + "/api/" + "documents"
        )
        self.assertEqual(
            mambugeturl.getpostdocumentsurl(
                "123"), self.prefix + "/api/" + "documents"
        )

    def test_getusercustominformationurl(self):
        self.assertEqual(
            mambugeturl.getusercustominformationurl("456"),
            self.prefix + "/api/" + "users/456/custominformation",
        )
        self.assertEqual(
            mambugeturl.getusercustominformationurl("456", customfield="test"),
            self.prefix + "/api/" + "users/456/custominformation/test",
        )

    def test_getsavingsurl(self):
        try:
            self.assertEqual(
                mambugeturl.getsavingssurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/12345?fullDetails=true&offset=0&limit=0",
            )
        except Exception:
            self.assertEqual(
                mambugeturl.getsavingssurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/12345?fullDetails=true&limit=0&offset=0",
            )

    def test_getsavingfundingrepaymentsurl(self):
        try:
            self.assertEqual(
                mambugeturl.getsavingfundingrepaymentsurl(
                    "12345", "54321", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" +
                "savings/12345/funding/54321/repayments?fullDetails=true&offset=0&limit=0",
            )
        except Exception:
            self.assertEqual(
                mambugeturl.getsavingfundingrepaymentsurl(
                    "12345", "54321", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" +
                "savings/12345/funding/54321/repayments?fullDetails=true&limit=0&offset=0",
            )

    def test_getsavingstransactionsurl(self):
        try:
            self.assertEqual(
                mambugeturl.getsavingstransactionsurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/12345/transactions/?fullDetails=true&offset=0&limit=0",
            )
        except Exception:
            self.assertEqual(
                mambugeturl.getsavingstransactionsurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/12345/transactions/?fullDetails=true&limit=0&offset=0",
            )

    def test_getsavingstransactionssearchurl(self):
        try:
            self.assertEqual(
                mambugeturl.getsavingstransactionssearchurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/transactions/search?fullDetails=true&offset=0&limit=0",
            )
        except Exception:
            self.assertEqual(
                mambugeturl.getsavingstransactionssearchurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "savings/transactions/search?fullDetails=true&limit=0&offset=0",
            )

    def test_gettransactionchannelsurl(self):
        try:
            self.assertEqual(
                mambugeturl.gettransactionchannelsurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "transactionchannels/12345?fullDetails=true&offset=0&limit=0",
            )
        except Exception:
            self.assertEqual(
                mambugeturl.gettransactionchannelsurl(
                    "12345", **{"fullDetails": True, "offset": 0, "limit": 0}),
                self.prefix + "/api/" + "transactionchannels/12345?fullDetails=true&limit=0&offset=0",
            )


if __name__ == "__main__":
    unittest.main()
