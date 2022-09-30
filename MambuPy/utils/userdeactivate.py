"""Deactivate multiple users in a csv list."""
import argparse
import csv

from mambupy.api import mambugroup
from mambupy.api import mambuloan
from mambupy.api import mambuuser


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
        filters={'creditOfficerUsername': username},
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

    if balanceSum > 0 or accountState:
        return False
    else:
        return True


def deactivate_user(username):
    """Deactivate the given username.

    Calls to verify_loans to check if the user is deactivatable. If it not
    returns False.

    Unassign user's groups by changing the assignedCentreKey and assignedUserKey
    fields to None for each group that user has.

    Change userState field value to INACTIVE to deactivate user and returns True.

    Args:
        username (str): Username of the user to deactivate.

    Returns:
        (bool): depending on verify_loan's verification.
    """
    if verify_loans(username=username):

        groups = mambugroup.MambuGroup().get_all(
            filters={'creditOfficerUsername': username},
            detailsLevel='FULL')

        for group in groups:
            del group['assignedUserKey']
            group.patch(autodetect_remove=True)

        user = mambuuser.MambuUser().get(
            username, detailsLevel="FULL")
        user.userState = 'INACTIVE'
        user.patch(['userState'])

        return True

    else:
        return False


def main(csv_file):
    users = []
    with open(csv_file) as f:
        reader = csv.reader(f, delimiter=',')
        for us in reader:
            users.append(tuple(us))

    usersCanNotDeactivate = []
    for user in users:
        if deactivate_user(user):
            print('{0} user deactivated.'.format(user))
        else:
            usersCanNotDeactivate.append(user)

    if usersCanNotDeactivate:
        print("Users that could not be deactivated:")
        print(usersCanNotDeactivate)


if __name__ == "__main__":  # pragma: no cover
    argparser = argparse.ArgumentParser(
        description='Deactivates users from a list.'
    )
    argparser.add_argument(
        'users_list',
        help='CSV holding the usernames to deactivate.'
        '(col1: username)'
    )

    args = argparser.parse_args()

    csv_file = args.users_list

    main(csv_file)
