"""Make Dummy ORM objects.

Sample dummies are created here. Please DO NOT TRY to persist them to the DB.
"""

def make_dummy(instance, relations={}):
    """Make an instance to look like an empty dummy.

    Every field of the table is set with zeroes/empty strings.
    Date fields are set to 01/01/1901.

    * relations is a dictionary to set properties for relationships on
    the instance.

    The keys of the relations dictionary are the name of the fields to
    be set at the instance.

    The values of the relations dictionary must be 2 dimension tuples:

      - first element will be the element to be related.

      - second element will be the name of the backref set on the previous
      first element of the tuple, as a list containing the instance.

    If you wish that no backref to be set you may use any invalid value
    for a property name, anything other than a string, for example a
    number. Preferably, use None.

    TODO further field types may be set at the init_data dictionary.
    """
    from datetime import datetime as dt

    # init_data knows how to put an init value depending on data type
    init_data = {
        'DATETIME'        : dt.strptime('1901-01-01','%Y-%m-%d'),
        'VARCHAR'         : "",
        'INTEGER'         : 0,
        'NUMERIC(50, 10)' : 0.0,
        }

    # the type of the instance is the SQLAlchemy Table
    table = type(instance)

    for col in table.__table__.columns:
        # declarative base tables have a columns property useful for reflection
        setattr(instance, col.name, init_data[str(col.type)])

    for k,v in relations.iteritems():
        # set the relationship property with the first element of the tuple
        setattr(instance, k, v[0])
        try:
            # set the relationship backref on the first element of the tuple
            # with a property named according to the second element of the
            # tuple, pointing to a list with the instance itself (assumes a
            # one-to-many relationship)
            # in case you don't want a backref, just send a None as v[1]
            setattr(v[0], v[1], [ instance ])
        except:
            pass

    return instance


# Sample DUMMIES

# Some sample dummies with all the current tables mapped on MambuPy.
# When creating new tables, please add them here.

# Current relationships are also dummified here, please add new relations when
# existing tables are updated with further relationships
from schema_mambu import *

# branches
branch = make_dummy(branches.Branch())

# users
role = make_dummy(users.Role())
user = make_dummy(users.User(),
                  relations={'branch' : (branch , 'users'),
                             'role'   : (role   , 'users'),
                            })

# groups
group = make_dummy(groups.Group(),
                   relations={'branch' : (branch , 'groups'),
                              'user'   : (user   , 'groups'),
                             })

# clients
iddoc  = make_dummy(clients.IdentificationDocument())
client = make_dummy(clients.Client(),
                    relations={'branch'                  : (branch    , 'clients'),
                               'groups'                  : ([ group ] , 'clients'),
                               'identificationdocuments' : ([ iddoc ] , 'client'),
                              })

# loan accounts
loanproduct         = make_dummy(loans.LoanProduct())
disbursementdetails = make_dummy(loans.DisbursementDetails())
repayment           = make_dummy(loans.Repayment())
loantransaction     = make_dummy(loans.LoanTransaction())
loanaccount         = make_dummy(loans.LoanAccount(),
                                 relations={'product'             : (loanproduct         , None),
                                            'disbursementdetails' : (disbursementdetails , None),
                                            'branch'              : (branch              , None),
                                            'user'                : (user                , 'loans'),
                                            'holder_group'        : (group               , 'loans'),
                                            'holder_client'       : (client              , 'loans'),
                                            'repayments'          : ([ repayment ]       , 'account'),
                                            'transactions'        : ([ loantransaction ] , 'account'),
                                           })

# custom fields
custominformation = make_dummy(customfields.CustomField())
customfieldvalue  = make_dummy(customfields.CustomFieldValue(),
                               relations={'customfield' : (custominformation , 'customfieldvalues'),
                                          'branch'      : (branch            , 'cusotminformation'),
                                          'user'        : (user              , 'custominformation'),
                                          'group'       : (group             , 'custominformation'),
                                          'client'      : (client            , 'custominformation'),
                                          'loan'        : (loanaccount       , 'custominformation'),
                                         })

# addresses
address = make_dummy(addresses.Address(),
                     relations={'branch' : (branch , 'addresses'),
                                'group'  : (group  , 'addresses'),
                                'client' : (client , 'addresses'),
                               })

# activities
activity = make_dummy(activities.Activity(),
                      relations={'loan'         : (loanaccount , 'activities'),
                                 'branch'       : (branch      , 'activities'),
                                 'client'       : (client      , 'activities'),
                                 'group'        : (group       , 'activities'),
                                 'user'         : (user        , 'activities'),
                                 'assigneduser' : (user        , 'assignedactivities'),
                                })
