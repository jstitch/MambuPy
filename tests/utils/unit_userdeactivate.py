import os
import sys
import unittest
import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.utils import userdeactivate
from MambuPy.api import mambuloan
from MambuPy.api import mambugroup
from MambuPy.api import mambuuser

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

    @mock.patch('MambuPy.api.mambuuser.MambuUser.patch')
    @mock.patch('MambuPy.api.mambugroup.MambuGroup.patch')
    @mock.patch('MambuPy.utils.userdeactivate.mambuuser.MambuUser.get')
    @mock.patch('MambuPy.utils.userdeactivate.mambugroup.MambuGroup.get_all')
    @mock.patch('MambuPy.utils.userdeactivate.verify_loans')
    def test_deactivate_user(
        self,
        mock_verify_loans,
        mock_group_get_all,
        mock_user_get,
        mock_group_patch,
        mock_user_patch
    ):
        mg_1 = mambugroup.MambuGroup(
            id=12345,
            assignedUserKey='userkey',
        )

        mg_2 = mambugroup.MambuGroup(
            id=12346,
            assignedUserKey='userkey',
        )

        mg_3 = mambugroup.MambuGroup(
            id=12347,
            assignedUserKey='userkey',
        )

        mu = mambuuser.MambuUser(
            id=123456,
            username='amlo',
            userState='ACTIVE',
        )

        mock_verify_loans.return_value = True
        mock_group_get_all.return_value = [mg_1, mg_2, mg_3]
        mock_user_get.return_value = mu

        self.assertTrue(userdeactivate.deactivate_user('amlo'))
        mock_group_get_all.assert_called_with(
            filters={'creditOfficerUsername':'amlo'},
            detailsLevel='FULL'
        )
        self.assertEqual(mock_group_patch.call_count, 3)

        mock_user_get.assert_called_with(
            'amlo', detailsLevel="FULL"
        )
        mock_group_patch.assert_called_with(autodetect_remove=True)
        mock_user_patch.assert_called_with(['userState'])

        mock_verify_loans.return_value = False
        self.assertFalse(userdeactivate.deactivate_user('amlo'))


if __name__ == '__main__':
    unittest.main()
