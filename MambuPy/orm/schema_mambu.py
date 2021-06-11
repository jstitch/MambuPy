"""This file imports all ORM schemas.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

..
  ejemplos de intersphinx...
  :py:class:`zipfile.ZipFile`
  :py:func:`sqlalchemy.create_engine`
  :py:func:`sqlalchemy.create_engine`

To use the ORM you MUST import schema_mambu, if you try to use the schemas
individualy you will get some relationship() errors, for example,
if you use schema_loans, you will get an error like this::

 from mambupy.schema_loans import *
 loan = session.query(LoanAccount).filter(LoanAccount.id=="12345").one()

... When initializing mapper Mapper|Branch|branch, expression ...

Instead, if you use schema_mambu the query executes correctly::

 from mambupy.schema_mambu import *
 loan = session.query(LoanAccount).filter(LoanAccount.id=="12345").one()
"""

from .schema_activities import *
from .schema_addresses import *
from .schema_branches import *
from .schema_centres import *
from .schema_clients import *
from .schema_customfields import *
from .schema_groups import *
from .schema_loans import *
from .schema_tasks import *
from .schema_users import *
