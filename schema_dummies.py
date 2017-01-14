"""Dummy ORM objects.

DO NOT TRY to persist  this to the DB.
"""

from datetime import datetime as dt

from schema_mambu import *


def empty_table(instance, relations={}):
    init_data = {
        'DATETIME'        : dt.strptime('1901-01-01','%Y-%m-%d'),
        'VARCHAR'         : "",
        'INTEGER'         : 0,
        'NUMERIC(50, 10)' : 0.0,
        }

    table = type(instance)

    for col in table.__table__.columns:
        setattr(instance, col.name, init_data[str(col.type)])

    for k,v in relations.iteritems():
        setattr(instance, k, v[0])
        try:
            setattr(v[0], v[1], [ instance ])
        except:
            pass

    return instance

# branches
branch = empty_table(branches.Branch())

# users
role = empty_table(users.Role())
user = empty_table(users.User(), relations={'branch' : (branch,'users'), 'role' : (role,'users')})

# groups
group = empty_table(groups.Group(), relations={'branch' : (branch, 'groups'), ' user' : (user, 'groups')})

# clients
client        = empty_table(clients.Client(), relations={'branch' : (branch, 'clients')})
client.loans  = []
client.groups = [ group ]
group.clients = [ client ]

identificationdocument = empty_table(clients.IdentificationDocument(), relations={'client' : (client, 'identificationdocuments')})

# loan accounts
loanproduct         = empty_table(loans.LoanProduct())
disbursementdetails = empty_table(loans.DisbursementDetails())
loanaccount         = empty_table(loans.LoanAccount(), relations={'product'             : (loanproduct, None),
                                                                  'disbursementdetails' : (disbursementdetails, None),
                                                                  'branch'              : (branch, None),
                                                                  'user'                : (user, 'loans'),
                                                                  'holder_group'        : (group, 'loans'),
                                                                  'holder_client'       : (None, None)
                                                                 })
repayment           = empty_table(loans.Repayment(),       relations={'account' : (loanaccount, 'repayments')})
loantransaction     = empty_table(loans.LoanTransaction(), relations={'account' : (loanaccount, 'transactions')})

# custom fields
custominformation = empty_table(customfields.CustomField())
customfieldvalue  = empty_table(customfields.CustomFieldValue(), relations={'customfield' : (custominformation, 'customfieldvalues'),
                                                                            'branch'      : (branch      , 'cusotminformation'),
                                                                            'user'        : (user        , 'custominformation'),
                                                                            'group'       : (group       , 'custominformation'),
                                                                            'client'      : (client      , 'custominformation'),
                                                                            'loan'        : (loanaccount , 'custominformation')
                                                                           })

# addresses
address = empty_table(addresses.Address(), relations={'branch' : (branch , 'addresses'),
                                                      'group'  : (group  , 'addresses'),
                                                      'client' : (client , 'addresses')
                                                     })

# activities
activity = empty_table(activities.Activity(), relations={'loan' : (loanaccount, 'activities'),
                                                         'branch' : (branch, 'activities'),
                                                         'client' : (client, 'activities'),
                                                         'group' : (group, 'activities'),
                                                         'user' : (user, 'activities'),
                                                         'assigneduser' : (user, 'assignedactivities')
                                                        })
