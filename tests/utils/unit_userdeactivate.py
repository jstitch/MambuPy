import os
import sys
import unittest
import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.utils import userdeactivate
from MambuPy.api import mambuloan

class UserDeactivate(unittest.TestCase):
    @mock.patch('MambuPy.utils.userdeactivate.mambuloan.MambuLoan.get_all')
    def test_verify_loans(self, mock_get_all):
        ml = mambuloan.MambuLoan(
            id=1234,
            accountState='CLOSED',
            balances={
                'principalBalance': 0,
                'interestBalance': 0,
                'feesBalance': 0,
                'penaltyBalance': 0
            }
        )

        mock_get_all.return_value = [ml]

        self.assertTrue(userdeactivate.verify_loans('b.miranda'))
        mock_get_all.assert_called_with(
            filters={'creditOfficerUsername':'b.miranda'},
            detailsLevel='FULL'
        )

        ml.accountState = 'ACTIVE'
        self.assertFalse(userdeactivate.verify_loans('b.miranda'))

        ml.accountState = 'ACTIVE_IN_ARREARS'
        self.assertFalse(userdeactivate.verify_loans('b.miranda'))

        ml.balances['principalBalance'] = 1
        self.assertFalse(userdeactivate.verify_loans('b.miranda'))


if __name__ == '__main__':
    unittest.main()
