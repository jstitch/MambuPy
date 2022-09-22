"""Deactivate multiple users in a csv list.
"""
import argparse
import csv

from mambupy.mambuconfig import apiuser, apipwd, apiurl
from mambupy.api import mambuloan

def verify_loans(username):
    """Verify the loans wallet of given username. 
    
    If user does meet the conditions: 
    User has loans with state equal to 'ACTIVE' or 'ACTIVE_IN_ARREARS' and its 
    loans balance are mayor than 0 the method returns False, if not returns True.

    Args:
        username (str): the username of the user to deactivate.
    
    Returns:
        (bool): depending on user's loans satisfying or not the given conditions.
    """
    
    loans = mambuloan.MambuLoan().get_all(
        filters={'creditOfficerUsername':username}, 
        detailsLevel='FULL')

    balanceSum = 0
    accountState = False
    for loan in loans:
        balanceSum += loan.balances['principalBalance'] \
                    + loan.balances['interestBalance'] \
                    + loan.balances['feesBalance'] \
                    + loan.balances['penaltyBalance'] 
        if loan.accountState in ['ACTIVE', 'ACTIVE_IN_ARREARS']:
            accountState = True
    
    if balanceSum > 0 and accountState:
        return False
    else:
        return True


def main(csv_file, mambu_user=apiuser, mambu_pwd=apipwd, mambu_url=apiurl):
    """"""

if __name__ == "__main__":
    """"""
