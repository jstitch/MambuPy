"""Make Dummy ORM objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

Sample dummies are created here. Please DO NOT TRY to persist them to the DB.
"""

from datetime import datetime as dt


def make_dummy(
    instance,
    relations={},
    datetime_default=dt.strptime("1901-01-01", "%Y-%m-%d"),
    varchar_default="",
    integer_default=0,
    numeric_default=0.0,
    *args,
    **kwargs
):
    """Make an instance to look like an empty dummy.

    Every field of the table is set with zeroes/empty strings.
    Date fields are set to 01/01/1901.

    * relations is a dictionary to set properties for relationships
      on the instance.

    The keys of the relations dictionary are the name of the fields to
    be set at the instance.

    The values of the relations dictionary must be 2 dimension tuples:

    - first element will be the element to be related.

    - second element will be the name of the backref set on the previous
      first element of the tuple, as a list containing the instance.

    If you wish that no backref to be set you may use any invalid value
    for a property name, anything other than a string, for example a
    number. Preferably, use None.

    * datetime_default is the datetime object to use for init datetime
      fields. Defaults to 01-01-1901

    * varchar_default is the string object to use for init varchar
      fields. Defaults to ""

    * integer_default is the int object to use for init integer
      fields. Defaults to 0

    * numeric_default is the float object to use for init numeric
      fields. Defaults to 0.0

    * kwargs may have the name of a certain field you wish to initialize
      with a value other than the given by the init_data dicionary. If you
      give an unexistent name on the columns of the table, they are safely
      ignored.

    .. todo:: further field types may be set at the init_data dictionary."""

    # init_data knows how to put an init value depending on data type
    init_data = {
        "DATETIME": datetime_default,
        "VARCHAR": varchar_default,
        "INTEGER": integer_default,
        "NUMERIC(50, 10)": numeric_default,
        "TEXT": varchar_default,
    }

    # the type of the instance is the SQLAlchemy Table
    table = type(instance)

    for col in table.__table__.columns:
        # declarative base tables have a columns property useful for reflection
        try:
            setattr(instance, col.name, kwargs[col.name])
        except KeyError:
            setattr(instance, col.name, init_data[str(col.type)])

    for k, v in relations.items():
        # set the relationship property with the first element of the tuple
        setattr(instance, k, v[0])
        # try:
        #     # set the relationship backref on the first element of the tuple
        #     # with a property named according to the second element of the
        #     # tuple, pointing to a list with the instance itself (assumes a
        #     # one-to-many relationship)
        #     # in case you don't want a backref, just send a None as v[1]
        #     try:
        #         getattr(v[0], v[1]).append(instance)
        #     except:
        #         setattr(v[0], v[1], [ instance ])
        # except:
        #     pass

    return instance


# Sample DUMMIES

# Some sample dummies with all the current tables mapped on MambuPy.
# When creating new tables, please add them here.

# Current relationships are also dummified here, please add new relations when
# existing tables are updated with further relationships
from .schema_mambu import *

# branches
branch = make_dummy(Branch())

# centres
centre = make_dummy(Centre())

# users
role = make_dummy(Role())
user = make_dummy(
    User(),
    relations={
        "branch": (branch, "users"),
        "role": (role, "users"),
    },
)

# groups
group = make_dummy(
    Group(),
    relations={
        "branch": (branch, "groups"),
        "centre": (centre, "groups"),
        "user": (user, "groups"),
    },
)

# clients
iddoc = make_dummy(IdentificationDocument())
client = make_dummy(
    Client(),
    relations={
        "branch": (branch, "clients"),
        "groups": ([group], "clients"),
        "identificationDocuments": ([iddoc], "client"),
    },
)

# loan accounts
loanproduct = make_dummy(LoanProduct())
disbursementdetails = make_dummy(DisbursementDetails())
repayment = make_dummy(Repayment())
transactionchannel = make_dummy(TransactionChannel())
transactiondetails = make_dummy(
    TransactionDetails(), relations={"transactionChannel": (transactionchannel, None)}
)
loantransaction = make_dummy(
    LoanTransaction(), relations={"transactionDetails": (transactiondetails, None)}
)
loanaccount = make_dummy(
    LoanAccount(),
    relations={
        "product": (loanproduct, None),
        "disbursementDetails": (disbursementdetails, None),
        "branch": (branch, None),
        "user": (user, "loans"),
        "holder_group": (group, "loans"),
        "holder_client": (client, "loans"),
        "repayments": ([repayment], "account"),
        "transactions": ([loantransaction], "account"),
    },
)

# custom fields
custominformation = make_dummy(CustomField())
customfieldvalue = make_dummy(
    CustomFieldValue(),
    relations={
        "customField": (custominformation, "customFieldValues"),
        "branch": (branch, "customInformation"),
        "user": (user, "customInformation"),
        "group": (group, "customInformation"),
        "client": (client, "customInformation"),
        "loan": (loanaccount, "customInformation"),
    },
)

# addresses
address = make_dummy(
    Address(),
    relations={
        "branch": (branch, "addresses"),
        "group": (group, "addresses"),
        "client": (client, "addresses"),
    },
)

# activities
activity = make_dummy(
    Activity(),
    relations={
        "loan": (loanaccount, "activities"),
        "branch": (branch, "activities"),
        "client": (client, "activities"),
        "group": (group, "activities"),
        "user": (user, "activities"),
        "assignedUser": (user, "assignedActivities"),
    },
)
# tasks
tasks = make_dummy(
    Task(),
    relations={
        "createdByUser": (user, "createdTasks"),
        "assignedUser": (user, "assignedTasks"),
        "link_group": (group, "tasks"),
        "link_loan": (loanaccount, "tasks"),
    },
)
