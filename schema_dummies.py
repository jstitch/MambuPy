"""Dummy ORM objects.

DO NOT TRY to persist  this to the DB.
"""

from datetime import datetime as dt

from schema_mambu import *


def empty_table(instance):
    init_data = {
        'DATETIME'        : dt.strptime('1901-01-01','%Y-%m-%d'),
        'VARCHAR'         : "",
        'INTEGER'         : 0,
        'NUMERIC(50, 10)' : 0.0,
        }

    table = type(instance)

    for col in table.__table__.columns:
        setattr(instance, col.name, init_data[str(col.type)])

    return instance

# branches
branch = empty_table(branches.Branch())

# users
role                   = empty_table(users.Role())
user                   = empty_table(users.User())
user.branch            = branch               ; branch.users          = [ user ]
user.role              = role                 ; role.users            = [ user ]

# groups
group        = empty_table(groups.Group())
group.branch = branch ; branch.groups = [ group ]
group.user   = user   ; user.groups   = [ group ]

# clients
client        = empty_table(clients.Client())
client.branch = branch ; branch.clients = [ client ]
client.loans  = []
client.groups = [ group ]
group.clients = [ client ]

identificationdocument         = empty_table(clients.IdentificationDocument())
identificationdocument.client  = client
client.identificationdocuments = [ identificationdocument ]

# loan accounts
loanproduct                     = empty_table(loans.LoanProduct())
disbursementdetails             = empty_table(loans.DisbursementDetails())
loanaccount                     = empty_table(loans.LoanAccount())
repayment                       = empty_table(loans.Repayment())
loantransaction                 = empty_table(loans.LoanTransaction())
loanaccount.product             = loanproduct
loanaccount.disbursementdetails = disbursementdetails
loanaccount.branch              = branch
loanaccount.user                = user        ; user.loans               = [ loanaccount ]
repayment.account               = loanaccount ; loanaccount.repayments   = [ repayment ]
loantransaction.account         = loanaccount ; loanaccount.transactions = [ loantransaction ]
loanaccount.holder_group        = group       ; group.loans              = [ loanaccount ]
loanaccount.holder_client       = None

# custom fields
custominformation            = empty_table(customfields.CustomField())
customfieldvalue             = empty_table(customfields.CustomFieldValue())
customfieldvalue.customfield = custominformation ; custominformation.customfieldvalues = [ customfieldvalue ]
customfieldvalue.branch      = branch            ; branch.custominformation            = [ customfieldvalue ]
customfieldvalue.user        = user              ; user.custominformation              = [ customfieldvalue ]
customfieldvalue.group       = group             ; group.custominformation             = [ customfieldvalue ]
customfieldvalue.client      = client            ; client.custominformation            = [ customfieldvalue ]
customfieldvalue.loan        = loanaccount       ; loanaccount.custominformation       = [ customfieldvalue ]

# addresses
address        = empty_table(addresses.Address())
address.branch = branch ; branch.addresses = [ address ]
address.group  = group  ; group.addresses  = [ address ]
address.client = client ; client.addresses = [ address ]

# activities
activity              = empty_table(activities.Activity())
activity.loan         = loanaccount ; loanaccount.activities  = [ activity ]
activity.branch       = branch      ; branch.activities       = [ activity ]
activity.client       = client      ; client.activities       = [ activity ]
activity.group        = group       ; group.activities        = [ activity ]
activity.user         = user        ; user.activities         = [ activity ]
activity.assigneduser = user        ; user.assignedactivities = [ activity ]
