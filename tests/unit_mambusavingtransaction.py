# coding: utf-8

import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambusavingtransaction

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuSavingTransactionTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getsavingstransactionssearchurl, getsavingstransactionsurl

        self.assertEqual(mambusavingtransaction.mod_urlfunc_search, getsavingstransactionssearchurl)
        self.assertEqual(mambusavingtransaction.mod_urlfunc_saving, getsavingstransactionsurl)

    def test_class(self):
        a = mambusavingtransaction.MambuSavingTransaction(urlfunc=None)
        self.assertTrue(mambusavingtransaction.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambusavingtransaction.MambuSavingTransaction(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")


class MambuSavingTransactionsTests(unittest.TestCase):
    def test_class(self):
        acs = mambusavingtransaction.MambuSavingTransactions(urlfunc=None)
        self.assertTrue(mambusavingtransaction.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambusavingtransaction.MambuSavingTransactions(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):

        acs = mambusavingtransaction.MambuSavingTransactions(urlfunc=None)
        acs.attrs = [
            {"saving_transaction": "my_saving_transaction"},
            {"saving_transaction": "my_2_saving_transaction"},
        ]
        with self.assertRaisesRegex(
            AttributeError,
            "'MambuSavingTransactions' object has no attribute 'transaction_channel'",
        ):
            acs.transaction_channel
        acs.convert_dict_to_attrs()
        self.assertEqual(
            str(acs.itemclass),
            "<class 'MambuPy.rest.mambusavingtransaction.MambuSavingTransaction'>",
        )
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuSavingTransaction")
            self.assertEqual(a._MambuStruct__urlfunc, None)

class MambuSavingsTransactionSearchTests(unittest.TestCase):
    def test_class(self):
        acs = mambusavingtransaction.MambuSavingsTransactionSearch(urlfunc=None)
        self.assertTrue(mambusavingtransaction.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambusavingtransaction.MambuSavingsTransactionSearch(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import getsavingstransactionsurl

        acs = mambusavingtransaction.MambuSavingsTransactionSearch(urlfunc=None)
        acs.attrs = [
            {"saving_transaction": "my_saving_transaction"},
            {"saving_transaction": "my_2_saving_transaction"},
        ]
        with self.assertRaisesRegex(
            AttributeError,
            "'MambuSavingsTransactionSearch' object has no attribute 'transaction_channel'",
        ):
            acs.transaction_channel
        acs.convert_dict_to_attrs()
        self.assertEqual(
            str(acs.itemclass),
            "<class 'MambuPy.rest.mambusavingtransaction.MambuSavingTransaction'>",
        )
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuSavingTransaction")
            self.assertEqual(a._MambuStruct__urlfunc, getsavingstransactionsurl)


if __name__ == "__main__":
    unittest.main()
