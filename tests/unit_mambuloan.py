# coding: utf-8

import json
import logging
import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import requests
import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambuloan

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


logging.disable(logging.CRITICAL)


class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text

    def raise_for_status(self):
        return


class MambuLoanTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getloansurl

        self.assertEqual(mambuloan.mod_urlfunc, getloansurl)

    def test_class(self):
        l = mambuloan.MambuLoan(urlfunc=None)
        self.assertTrue(mambuloan.MambuStruct in l.__class__.__bases__)

    def test___init__(self):
        l = mambuloan.MambuLoan(urlfunc=None, getClientDetails=lambda x:x)
        self.assertEqual(l.custom_field_name, "customFieldValues")

    def test_getDebt(self):  # , mambustruct):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {
                "principalBalance": 0.0,
                "interestBalance": 0.0,
                "feesBalance": 0.0,
                "penaltyBalance": 0.0,
            }

        with mock.patch.object(mambuloan.MambuStruct, "connect", mock_connect):
            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertEqual(l.getDebt(), 0)
            l["principalBalance"] = 1
            l["interestBalance"] = 1
            l["feesBalance"] = 1
            l["penaltyBalance"] = 1
            self.assertEqual(l.getDebt(), 4)

    def test_preprocess(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"notes": " notes "}

        def mock_preprocess(*args, **kwargs):
            args[0]["notes"] = args[0]["notes"].strip()

        def mock_loan_preprocess(*args, **kwargs):
            return args[0].capitalize()

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch.object(mambuloan.MambuStruct, "preprocess", mock_preprocess):
            mambuloan.strip_tags = mock.Mock()
            mambuloan.strip_tags.side_effect = mock_loan_preprocess
            l = mambuloan.MambuLoan(urlfunc=lambda x: x)

            l.preprocess()
            self.assertEqual(l["notes"], "Notes")
            mambuloan.strip_tags.assert_called_once_with("notes")

    def test_setRepayments(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345"}

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch(
            "MambuPy.rest.mamburepayment.MambuRepayments"
        ) as mock_mamburepayments:
            reps = mock.Mock(
                return_value=[{"dueDate": "2018-10-23"}, {"dueDate": "2018-01-01"}]
            )
            reps.__iter__ = mock.Mock(
                return_value=iter([{"dueDate": "2018-01-01"}, {"dueDate": "2018-10-23"}])
            )
            reps.attrs = [{"dueDate": "2018-10-23"}, {"dueDate": "2018-01-01"}]
            mock_mamburepayments.return_value = reps
            mock_mamburepayments.attrs = [
                {"dueDate": "2018-10-23"},
                {"dueDate": "2018-01-01"},
            ]

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("repayments"))
            self.assertFalse(l.has_key("mamburepaymentsclass"))

            # no mamburepyamentsclass yet
            l.setRepayments()
            self.assertTrue(l.has_key("repayments"))
            self.assertTrue(l.has_key("mamburepaymentsclass"))
            mock_mamburepayments.assert_called_once_with(entid="12345")
            self.assertEqual(list(l["repayments"]), reps.attrs)

            # already with mamburepaymentsclass
            mock_mamburepayments.reset_mock()
            l.setRepayments()
            self.assertTrue(l.has_key("repayments"))
            self.assertTrue(l.has_key("mamburepaymentsclass"))
            mock_mamburepayments.assert_called_once_with(entid="12345")

    def test_setTransactions(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345"}

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch(
            "MambuPy.rest.mambutransaction.MambuTransactions"
        ) as mock_mambutransactions:
            trans = mock.Mock(
                return_value=[
                    {"transactionId": "9912356"},
                    {"transactionId": "9912345"},
                ]
            )
            trans.__iter__ = mock.Mock(
                return_value=iter(
                    [{"transactionId": "9912345"}, {"transactionId": "9912356"}]
                )
            )
            trans.attrs = [{"transactionId": "9912356"}, {"transactionId": "9912345"}]
            mock_mambutransactions.return_value = trans
            mock_mambutransactions.attrs = [
                {"transactionId": "9912356"},
                {"transactionId": "9912345"},
            ]

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("transactions"))
            self.assertFalse(l.has_key("mambutransactionsclass"))

            # no mambutransactionsclass yet
            l.setTransactions()
            self.assertTrue(l.has_key("transactions"))
            self.assertTrue(l.has_key("mambutransactionsclass"))
            mock_mambutransactions.assert_called_once_with(entid="12345")
            self.assertEqual(list(l["transactions"]), trans.attrs)

            # already with mambutransactionsclass
            mock_mambutransactions.reset_mock()
            l.setTransactions()
            self.assertTrue(l.has_key("transactions"))
            self.assertTrue(l.has_key("mambutransactionsclass"))
            mock_mambutransactions.assert_called_once_with(entid="12345")

    def test_setBranch(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "assignedBranchKey": "brnch12345"}

        class my_branch(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambubranch.MambuBranch") as mock_mambubranch:
            my_branch_instance = my_branch(id="dummyBranchId", name="myBranchName")
            mock_mambubranch.return_value = my_branch_instance

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("assignedBranch"))
            self.assertFalse(l.has_key("assignedBranchName"))
            self.assertFalse(l.has_key("mambubranchclass"))

            # no mambubranchclass yet
            l.setBranch()
            self.assertTrue(l.has_key("assignedBranch"))
            self.assertTrue(l.has_key("assignedBranchName"))
            self.assertTrue(l.has_key("mambubranchclass"))
            mock_mambubranch.assert_called_once_with(entid="brnch12345")
            self.assertEqual(l["assignedBranch"], my_branch_instance)
            self.assertEqual(l["assignedBranchName"], "myBranchName")

            # already with mambubranchclass
            mock_mambubranch.reset_mock()
            l.setBranch()
            self.assertTrue(l.has_key("assignedBranch"))
            self.assertTrue(l.has_key("assignedBranchName"))
            self.assertTrue(l.has_key("mambubranchclass"))
            mock_mambubranch.assert_called_once_with(entid="brnch12345")

    def test_setCentre(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "assignedCentreKey": "cntr12345"}

        class my_centre(object):
            def __init__(self, id, name):
                self.attrs = {"id": id, "name": name}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambucentre.MambuCentre") as mock_mambucentre:
            my_centre_instance = my_centre(id="dummyCentreId", name="myCentreName")
            mock_mambucentre.return_value = my_centre_instance

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("assignedCentre"))
            self.assertFalse(l.has_key("assignedCentreName"))
            self.assertFalse(l.has_key("mambucentreclass"))

            # no mambucentreclass yet
            l.setCentre()
            self.assertTrue(l.has_key("assignedCentre"))
            self.assertTrue(l.has_key("assignedCentreName"))
            self.assertTrue(l.has_key("mambucentreclass"))
            mock_mambucentre.assert_called_once_with(entid="cntr12345")
            self.assertEqual(l["assignedCentre"], my_centre_instance)
            self.assertEqual(l["assignedCentreName"], "myCentreName")

            # already with mambucentreclass
            mock_mambucentre.reset_mock()
            l.setCentre()
            self.assertTrue(l.has_key("assignedCentre"))
            self.assertTrue(l.has_key("assignedCentreName"))
            self.assertTrue(l.has_key("mambucentreclass"))
            mock_mambucentre.assert_called_once_with(entid="cntr12345")

    def test_setUser(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "assignedUserKey": "user12345"}

        def mock_connect_2(*args, **kwargs):
            args[0].attrs = {"id": "12345"}

        class my_user(object):
            def __init__(self, id):
                self.attrs = {"id": id}

            def __getitem__(self, item):
                return self.attrs[item]

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch("MambuPy.rest.mambuuser.MambuUser") as mock_mambuuser:
            my_user_instance = my_user(id="dummyCentreId")
            mock_mambuuser.return_value = my_user_instance

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("assignedUser"))
            self.assertFalse(l.has_key("mambuuserclass"))

            # no mambuuserclass yet
            l.setUser()
            self.assertTrue(l.has_key("user"))
            self.assertTrue(l.has_key("mambuuserclass"))
            mock_mambuuser.assert_called_once_with(entid="user12345")
            self.assertEqual(l["user"], my_user_instance)

            # already with mambuuserclass
            mock_mambuuser.reset_mock()
            l.setUser()
            self.assertTrue(l.has_key("user"))
            self.assertTrue(l.has_key("mambuuserclass"))
            mock_mambuuser.assert_called_once_with(entid="user12345")

        # no user assigned to account
        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect_2
        ), mock.patch("MambuPy.rest.mambuuser.MambuUser") as mock_mambuuser:
            my_user_instance = my_user(id="dummyCentreId")
            mock_mambuuser.return_value = my_user_instance

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("assignedUser"))
            with self.assertRaisesRegexp(
                mambuloan.MambuError, r"Loan Account 12345 has no assigned user"
            ):
                l.setUser()
            self.assertFalse(l.has_key("user"))

    def test_setProduct(self):
        from future.utils import implements_iterator

        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "productTypeKey": "prodEk12345"}

        class my_product(object):
            def __init__(self, id, encodedKey):
                self.attrs = {"id": id, "encodedKey": encodedKey}

            def __getitem__(self, item):
                return self.attrs[item]

        my_product_instance = my_product(id="dummyProductId", encodedKey="prodEk12345")

        @implements_iterator
        class all_mambu_products(object):
            __instance = None

            def __new__(cls, *args, **kwargs):
                if not cls.__instance:
                    cls.__instance = super(all_mambu_products, cls).__new__(
                        cls, *args, **kwargs
                    )
                else:
                    cls.__instance.noinit = True
                return cls.__instance

            def __init__(self, *args, **kwargs):
                self.attrs = [my_product_instance]
                self.offset = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.offset >= len(self.attrs):
                    raise StopIteration
                else:
                    item = self.attrs[self.offset]
                    self.offset += 1
                    return item

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch(
            "MambuPy.rest.mambuproduct.MambuProduct"
        ) as mock_mambuproduct, mock.patch(
            "MambuPy.rest.mambuproduct.AllMambuProducts"
        ) as mock_all_mambu_products:
            mock_mambuproduct.return_value = my_product_instance
            mock_all_mambu_products.return_value = all_mambu_products()

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("product"))
            self.assertFalse(l.has_key("mambuproductclass"))

            # no mambuproductclass yet
            l.setProduct()
            self.assertTrue(l.has_key("product"))
            self.assertTrue(l.has_key("mambuproductclass"))
            mock_mambuproduct.assert_called_once_with(entid="prodEk12345")
            self.assertEqual(l["product"], my_product_instance)

            # already with mambuproductclass
            mock_mambuproduct.reset_mock()
            l.setProduct()
            self.assertTrue(l.has_key("product"))
            self.assertTrue(l.has_key("mambuproductclass"))
            mock_mambuproduct.assert_called_once_with(entid="prodEk12345")

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("product"))
            self.assertFalse(l.has_key("allmambuproductsclass"))

            # no allmambuproductsclass yet
            ret = l.setProduct(cache=True)
            self.assertEqual(ret, 1)
            self.assertTrue(l.has_key("product"))
            self.assertTrue(l.has_key("allmambuproductsclass"))
            self.assertEqual(l["product"], my_product_instance)

            # already with allmambuproductsclass
            ret = l.setProduct(cache=True)
            self.assertEqual(ret, 1)
            self.assertTrue(l.has_key("product"))
            self.assertTrue(l.has_key("allmambuproductsclass"))
            self.assertEqual(l["product"], my_product_instance)

            mock_all_mambu_products.return_value = all_mambu_products()
            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            ret = l.setProduct(cache=True)
            self.assertEqual(ret, 0)
            self.assertTrue(l.has_key("product"))
            self.assertEqual(l["product"], my_product_instance)

    def test_setActivities(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "encodedKey": "encKeyLoan12345"}

        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect
        ), mock.patch(
            "MambuPy.rest.mambuactivity.MambuActivities"
        ) as mock_mambuactivities:
            acts = mock.Mock(
                return_value=[
                    {"activity": {"encodedKey": "54321", "timestamp": 2}},
                    {"activity": {"encodedKey": "12345", "timestamp": 1}},
                ]
            )
            acts.__iter__ = mock.Mock(
                return_value=iter(
                    [
                        {"activity": {"encodedKey": "12345", "timestamp": 1}},
                        {"activity": {"encodedKey": "54321", "timestamp": 2}},
                    ]
                )
            )
            acts.attrs = [
                {"activity": {"encodedKey": "54321", "timestamp": 2}},
                {"activity": {"encodedKey": "12345", "timestamp": 1}},
            ]
            mock_mambuactivities.return_value = acts
            mock_mambuactivities.attrs = [
                {"activity": {"encodedKey": "54321", "timestamp": 2}},
                {"activity": {"encodedKey": "12345", "timestamp": 1}},
            ]

            l = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(l.has_key("activities"))
            self.assertFalse(l.has_key("mambuactivitiesclass"))

            # no mambuactivitiesclass yet
            l.setActivities()
            self.assertTrue(l.has_key("activities"))
            self.assertTrue(l.has_key("mambuactivitiesclass"))
            mock_mambuactivities.assert_called_once_with(loanAccountId="encKeyLoan12345")
            self.assertEqual(list(l["activities"]), acts.attrs)

            # already with mambuactivitiesclass
            mock_mambuactivities.reset_mock()
            l.setActivities()
            self.assertTrue(l.has_key("activities"))
            self.assertTrue(l.has_key("mambuactivitiesclass"))
            mock_mambuactivities.assert_called_once_with(loanAccountId="encKeyLoan12345")

    def test_getClientDetails(self):
        def mock_connect(*args, **kwargs):
            args[0].attrs = {"id": "12345", "loanAmount": 10000.0}

        holder = {
            "clients": [
                {"id": 1, "name": "ONE"},
                {"id": 2, "name": "TWO"},
                {"id": 3, "name": "THREE"},
            ]
        }
        with mock.patch.object(mambuloan.MambuStruct, "connect", mock_connect):
            ln = mambuloan.MambuLoan(urlfunc=lambda x: x)
            loannames = ln.getClientDetails(holder=holder)

            self.assertEqual(len(loannames), 3)
            for c, l in zip(holder["clients"], loannames):
                self.assertEqual(c["id"], l["id"])
                self.assertEqual(c["name"], l["name"])
                self.assertEqual(c, l["client"])
                self.assertEqual(10000.0, l["amount"])

    def test_setHolder(self):
        def mock_connect_client(*args, **kwargs):
            args[0].attrs = {
                "id": "12345",
                "loanAmount": 10000.0,
                "repaymentInstallments": 2,
                "accountHolderKey": "ABC123",
                "accountHolderType": "CLIENT",
            }

        def mock_connect_group(*args, **kwargs):
            args[0].attrs = {
                "id": "12345",
                "loanAmount": 10000.0,
                "repaymentInstallments": 2,
                "accountHolderKey": "ABC123",
                "accountHolderType": "GROUP",
            }

        # setHolder with accountHolderType=CLIENT
        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect_client
        ), mock.patch("MambuPy.rest.mambuclient.MambuClient") as mock_mambuclient:

            mock_cliente = {"name": "FULANITA"}
            mock_mambuclient.return_value = mock_cliente

            # getClients=False
            ln = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(ln.has_key("holderType"))
            self.assertFalse(ln.has_key("mambuclientclass"))

            # no mambuclientclass yet
            self.assertEqual(ln.setHolder(), 1)
            mock_mambuclient.assert_called_once_with(entid="ABC123", fullDetails=True)
            self.assertEqual(ln["holder"], mock_cliente)
            self.assertTrue(ln.has_key("holderType"))
            self.assertTrue(ln.has_key("mambuclientclass"))
            self.assertEqual(ln["holderType"], "Cliente")
            self.assertFalse(ln.has_key("clients"))

            # already with mambuclientclass
            mock_mambuclient.reset_mock()
            self.assertEqual(ln.setHolder(), 1)
            mock_mambuclient.assert_called_once_with(entid="ABC123", fullDetails=True)

            # getClients=True
            mock_mambuclient.reset_mock()
            ln = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertEqual(ln.setHolder(getClients=True), 1)
            self.assertTrue(ln.has_key("clients"))
            self.assertEqual(
                ln["clients"],
                {
                    "FULANITA": {
                        "client": mock_cliente,
                        "loan": ln,
                        "amount": 10000.0,
                        "montoPago": 5000.0,
                        "porcentaje": 1.0,
                    }
                },
            )

            # fullDetails param
            mock_mambuclient.reset_mock()
            ln = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertEqual(ln.setHolder(fullDetails=False), 1)
            mock_mambuclient.assert_called_once_with(entid="ABC123", fullDetails=False)

            mock_mambuclient.reset_mock()
            self.assertEqual(ln.setHolder(fullDetails=True), 1)
            mock_mambuclient.assert_called_once_with(entid="ABC123", fullDetails=True)

        # setHolder with accountHolderType=GROUP
        with mock.patch.object(
            mambuloan.MambuStruct, "connect", mock_connect_group
        ), mock.patch(
            "MambuPy.rest.mambugroup.MambuGroup"
        ) as mock_mambugroup, mock.patch(
            "MambuPy.rest.mambuclient.MambuClient"
        ) as mock_mambuclient:

            mock_grupo = {
                "groupRoles": [
                    {"roleName": "ROLE1", "clientKey": "clRoleKey1"},
                    {"roleName": "ROLE2", "clientKey": "clRoleKey2"},
                ]
            }
            mock_mambugroup.return_value = mock_grupo
            mock_mambuclient.side_effect = [
                {"id": "clRole1"},
                {"id": "clRole2"},
                {"id": "clRole1"},
                {"id": "clRole2"},
            ]

            # getClients=False, getRoles=False
            ln = mambuloan.MambuLoan(urlfunc=lambda x: x)
            self.assertFalse(ln.has_key("holderType"))
            self.assertFalse(ln.has_key("mambugroupclass"))

            # no mambugroupclass yet
            self.assertEqual(ln.setHolder(), 1)
            mock_mambugroup.assert_called_once_with(entid="ABC123", fullDetails=True)
            self.assertEqual(ln["holder"], mock_grupo)
            self.assertTrue(ln.has_key("holderType"))
            self.assertTrue(ln.has_key("mambugroupclass"))
            self.assertEqual(ln["holderType"], "Grupo")
            self.assertFalse(ln.has_key("clients"))

            # already with mambugroupclass
            mock_mambugroup.reset_mock()
            self.assertEqual(ln.setHolder(), 1)
            mock_mambugroup.assert_called_once_with(entid="ABC123", fullDetails=True)

            # getClients=False, getRoles=True
            mock_mambugroup.reset_mock()
            mock_mambuclient.reset_mock()

            # no mambuclientclass yet
            self.assertFalse(ln.has_key("mambuclientclass"))
            self.assertEqual(ln.setHolder(getRoles=True), 3)
            self.assertTrue(ln.has_key("mambuclientclass"))
            self.assertTrue("roles" in ln["holder"].keys())
            self.assertEqual(len(ln["holder"]["roles"]), 2)
            self.assertEqual(ln["holder"]["roles"][0]["role"], "ROLE1")
            self.assertEqual(ln["holder"]["roles"][1]["role"], "ROLE2")
            self.assertEqual(ln["holder"]["roles"][0]["client"], {"id": "clRole1"})
            self.assertEqual(ln["holder"]["roles"][1]["client"], {"id": "clRole2"})
            self.assertEqual(mock_mambuclient.call_count, 2)

            # already with mambuclientclass
            mock_mambuclient.reset_mock()
            self.assertEqual(ln.setHolder(getRoles=True), 3)
            self.assertEqual(mock_mambuclient.call_count, 2)

            # getClients=True, getRoles=False
            mock_grupo = mock.Mock()
            mock_grupo.setClients.return_value = 5
            mock_grupo.setClients.side_effect
            mock_mambugroup.return_value = mock_grupo
            mock_mambugroup.reset_mock()
            mock_mambuclient.reset_mock()
            ln.getClientDetails = mock.Mock()
            ln.getClientDetails.return_value = [
                {
                    "id": "clKey1",
                    "client": "client1",
                    "name": "CLIENT1",
                    "amount": 2000.0,
                    "extradata": "THIS IS ONE",
                },
                {
                    "id": "clKey2",
                    "client": "client2",
                    "name": "CLIENT2",
                    "amount": 2000.0,
                    "extradata": "THIS IS TWO",
                },
                {
                    "id": "clKey3",
                    "client": "client3",
                    "name": "CLIENT3",
                    "amount": 2000.0,
                    "extradata": "THIS IS THREE",
                },
                {
                    "id": "clKey4",
                    "client": "client4",
                    "name": "CLIENT4",
                    "amount": 2000.0,
                    "extradata": "THIS IS FOUR",
                },
                {
                    "id": "clKey5",
                    "client": "client5",
                    "name": "CLIENT5",
                    "amount": 2000.0,
                    "extradata": "THIS IS FIVE",
                },
            ]

            self.assertFalse(ln.has_key("clients"))
            self.assertEqual(ln.setHolder(getClients=True), 6)
            self.assertTrue(ln.has_key("clients"))
            mock_grupo.setClients.assert_called_once_with(
                fullDetails=True, mambuclientclass=mock_mambuclient
            )
            ln.getClientDetails.assert_called_once_with(holder=ln["holder"])
            self.assertEqual(len(ln["clients"]), 5)
            self.assertEqual(
                ln["clients"]["clKey1"],
                {
                    "id": "clKey1",
                    "client": "client1",
                    "name": "CLIENT1",
                    "loan": ln,
                    "amount": 2000.0,
                    "montoPago": 1000.0,
                    "porcentaje": 0.2,
                    "extradata": "THIS IS ONE",
                },
            )
            self.assertEqual(
                ln["clients"]["clKey2"],
                {
                    "id": "clKey2",
                    "client": "client2",
                    "name": "CLIENT2",
                    "loan": ln,
                    "amount": 2000.0,
                    "montoPago": 1000.0,
                    "porcentaje": 0.2,
                    "extradata": "THIS IS TWO",
                },
            )
            self.assertEqual(
                ln["clients"]["clKey3"],
                {
                    "id": "clKey3",
                    "client": "client3",
                    "name": "CLIENT3",
                    "loan": ln,
                    "amount": 2000.0,
                    "montoPago": 1000.0,
                    "porcentaje": 0.2,
                    "extradata": "THIS IS THREE",
                },
            )
            self.assertEqual(
                ln["clients"]["clKey4"],
                {
                    "id": "clKey4",
                    "client": "client4",
                    "name": "CLIENT4",
                    "loan": ln,
                    "amount": 2000.0,
                    "montoPago": 1000.0,
                    "porcentaje": 0.2,
                    "extradata": "THIS IS FOUR",
                },
            )
            self.assertEqual(
                ln["clients"]["clKey5"],
                {
                    "id": "clKey5",
                    "client": "client5",
                    "name": "CLIENT5",
                    "loan": ln,
                    "amount": 2000.0,
                    "montoPago": 1000.0,
                    "porcentaje": 0.2,
                    "extradata": "THIS IS FIVE",
                },
            )

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update(self, mock_requests):
        """Test update"""
        # set data response
        mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.exceptions.RetryError = requests.exceptions.RetryError

        mock_requests.Session().patch.return_value = Response(
            '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        mambuloan.MambuStruct.update = mock.Mock()
        mambuloan.MambuStruct.update.return_value = 1
        l = mambuloan.MambuLoan(connect=False)
        l.attrs = {}
        lData = {}
        # send none data
        lData["customInformation"] = {"f1": "v1"}
        self.assertEqual(l.update(lData), 2)

        mock_requests.Session().patch.return_value = Response(
            '{"returnCode":903,"returnStatus":"INVALID_CUSTOM_FIELD_ID"}'
        )
        mock_requests.Session().patch().raise_for_status = mock.Mock()
        mock_requests.Session().patch().raise_for_status.side_effect = requests.exceptions.HTTPError("")
        with self.assertRaisesRegexp(mambuloan.MambuError, "INVALID_CUSTOM_FIELD_ID"):
            l.update(lData)

        mambuloan.MambuStruct.update.assert_called()

    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_upload_document(self, mock_requests):
        """Test upload"""
        mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.exceptions.RetryError = requests.exceptions.RetryError
        # set data response
        mock_requests.Session().post.return_value = Response(
            '{"encodedKey":"8a818660727120000172722ce8396e1e",\
"id":48391,\
"creationDate":"2020-06-01T23:17:25+0000",\
"lastModifiedDate":"2020-06-01T23:17:25+0000",\
"documentHolderKey":"8a818ff870c4d7a30170c6d76ad20fef",\
"documentHolderType":"LOAN_ACCOUNT",\
"name":"otro PDF",\
"type":"pdf",\
"fileSize":718905,\
"originalFilename":"otro_PDF.pdf",\
"location":"ZLUBRCUJTWKQZFBDRCNCPUVAXXODDW",\
"createdByUserKey":"8a43a79f3664edaa0136a7ab14d4281c"}'
        )

        l = mambuloan.MambuLoan(connect=False)
        l.attrs = {"id": "ABC123"}
        lData = {
            "document": {
                "documentHolderType": "LOAN_ACCOUNT",
                "type": "pdf",
                "name": "otro PDF",
                "documentHolderKey": "8a818ff870c4d7a30170c6d76ad20fef",
            },
            "documentContent": "['encodedeBase64_file']",
        }
        # upload data
        self.assertEqual(l.upload_document(lData), 1)
        self.assertEqual(l.id, "ABC123")

        # exception
        mock_requests.Session().post.return_value = Response(
            '{"returnCode":4,"returnStatus":"INVALID_PARAMETERS","errorSource":"OwnerType"}'
        )
        mock_requests.Session().post().raise_for_status = mock.Mock()
        mock_requests.Session().post().raise_for_status.side_effect = requests.exceptions.HTTPError("")
        with self.assertRaisesRegexp(mambuloan.MambuError, "INVALID_PARAMETERS"):
            l.upload_document(lData)


class MambuLoansTests(unittest.TestCase):
    def test_class(self):
        ln = mambuloan.MambuLoans(urlfunc=None, getClientDetails=lambda x:x)
        self.assertTrue(mambuloan.MambuStruct in ln.__class__.__bases__)

    def test_iterator(self):
        ln = mambuloan.MambuLoans(urlfunc=None)
        ln.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(ln), 3)
        for n, a in enumerate(ln):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getloansurl

        ln = mambuloan.MambuLoans(urlfunc=None)
        ln.attrs = [
            {"username": "a_user"},
            {"username": "other_user"},
        ]
        with self.assertRaisesRegexp(
            AttributeError, "'MambuLoans' object has no attribute 'mambuloanclass'"
        ):
            ln.mambuloanclass
        ln.convert_dict_to_attrs()
        self.assertEqual(
            str(ln.mambuloanclass), "<class 'MambuPy.rest.mambuloan.MambuLoan'>"
        )
        for l in ln:
            self.assertEqual(l.__class__.__name__, "MambuLoan")
            self.assertEqual(l._MambuStruct__urlfunc, getloansurl)


if __name__ == "__main__":
    unittest.main()
