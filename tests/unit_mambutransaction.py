# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock
import unittest

from MambuPy import mambuconfig
for k,v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambutransaction

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex # python3
except Exception as e:
    pass # DeprecationWarning: Please use assertRaisesRegex instead

class MambuTransactionTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambuutil import gettransactionsurl
        self.assertEqual(mambutransaction.mod_urlfunc, gettransactionsurl)

    def test_class(self):
        tran = mambutransaction.MambuTransaction(urlfunc=None)
        self.assertTrue(mambutransaction.MambuStruct in tran.__class__.__bases__)

    def test___init__(self):
        tran = mambutransaction.MambuTransaction(urlfunc=None, entid="anything")
        self.assertEqual(tran.entid, "anything")

    def test___repr__(self):
        from datetime import date
        from MambuPy.mambuutil import gettransactionsurl
        def build_mock_tran_1(self, *args, **kwargs):
            self.attrs = {
                'transactionId' : args[1],
                'entryDate'     : date.today(),
                }

        with mock.patch.object(mambutransaction.MambuStruct, "__init__", build_mock_tran_1):
            tran = mambutransaction.MambuTransaction(urlfunc=gettransactionsurl, entid="mocktransaction")
            self.assertRegexpMatches(repr(tran), r"^MambuTransaction - transactionid: mocktransaction")


class MambuTransactionsTests(unittest.TestCase):
    def test_class(self):
        trans = mambutransaction.MambuTransactions(urlfunc=None)
        self.assertTrue(mambutransaction.MambuStruct in trans.__class__.__bases__)

    def test_iterator(self):
        trans = mambutransaction.MambuTransactions(urlfunc=None)
        trans.attrs = [{'0':0}, {'1':1}, {'2':2}]
        self.assertEqual(len(trans), 3)
        for n,t in enumerate(trans):
            self.assertEqual(str(n), [k for k in t][0])
            self.assertEqual(n, t[str(n)])

    def test_convertDict2Attrs(self):
        trans = mambutransaction.MambuTransactions(urlfunc=None)
        trans.attrs = [
            {'transactionId':"1", 'entryDate':"1979-10-23"},
            {'transactionId':"2", 'entryDate':"1981-06-08"},
            ]
        with self.assertRaisesRegexp(AttributeError,"'MambuTransactions' object has no attribute 'mambutransactionclass'"):
            trans.mambutransactionclass
        trans.convertDict2Attrs()
        self.assertEqual(str(trans.mambutransactionclass), "<class 'MambuPy.rest.mambutransaction.MambuTransaction'>")
        for t in trans:
            self.assertEqual(t.__class__.__name__, 'MambuTransaction')


if __name__ == '__main__':
    unittest.main()
