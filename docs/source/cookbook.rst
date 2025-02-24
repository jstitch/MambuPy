MambuPy Cookbook
================

.. tip::
   This guide offers a complete collection of recipes and practical
   examples for working with MambuPy. It covers everything from
   initial installation and setup to advanced operations with the
   Mambu API. Whether you're starting with integration or looking to
   implement specific functions, you'll find clear code examples and
   detailed explanations for each key aspect of the library.

Installation of MambuPy
-----------------------

MambuPy works on Python >3.8

.. warning::
   Currently MambuPy for Mambu's REST API v2 is in BETA phase. Mambu
   has announced the complete deprecation of v1 of their REST API,
   therefore it is NOT RECOMMENDED to use MambuPy modules that use
   that version of the Mambu API.

Installation using pip
~~~~~~~~~~~~~~~~~~~~~~

.. note:: Since the latest version of MambuPy is in beta, you can use
   the `--pre` argument to tell pip to use the latest prerelease
   version. The stable version does not support Mambu's API v2.

.. code-block:: bash

   pip install --pre MambuPy

Similarly, MambuPy covers other aspects for interacting with
Mambu. There is an ORM module with SQLAlchemy mappings for querying a
backup of Mambu's database dump. However, you may not want to install
that feature. You may access this features by installing:

.. code-block:: bash

   pip install --pre MambuPy[full]

Installation using uv
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv pip install --pre MambuPy


Configuration of MambuPy
------------------------

There are four ways to configure MambuPy, listed here in order of
priority (highest to lowest)

1. Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~

Environment variables have the highest priority and will override any
other configuration:

.. code-block:: bash

   export MAMBU_API_URL=yourtenant.sandbox.mambu.com
   export MAMBU_API_USER=yourapiuser
   export MAMBU_API_PWD=your_secret_password

2. Configuration via RC File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MambuPy will search for `RC files
<https://medium.com/@aadishazzam/rc-files-403a2b7c80a9>`_ in this
order, overwriting values as it finds consecutive files containing the
same configuration variables:

1. In the system's global directory: ``/etc/mambupy.rc``
2. In the user's home directory: ``~/.mambupy.rc`` (this is a hidden
   file in your account's ``$HOME`` directory)

The RC file must have the following format:

.. code-block:: ini

   [API]
   apiurl=yourtenant.sandbox.mambu.com
   apiuser=yourapiuser
   apipwd=your_secret_password

   # comments can be included
   # and there may be more configurations not mentioned here
   # See mambuconfig documentation for more details

If a variable value exists in ``/etc/mambupy.rc``, and then another
value for the same variable exists in ``~/.mambupy.rc``, the value
from the latter file is used. In any other case, both files complement
each other.

3. Configuration via Code
~~~~~~~~~~~~~~~~~~~~~~~~~

If no environment variables or RC files are found, you can use values
for these variables programmatically using MambuPy's configuration
module:

.. code-block:: python

   from mambupy import mambuconfig

   # Basic configuration
   mambuconfig.apiurl = "yourtenant.sandbox.mambu.com"
   mambuconfig.apiuser = "yourapiuser"
   mambuconfig.apipwd = "your_secret_password"

.. note::
   Configuration priority order:
   
   1. Code configuration (using ``mambuconfig``)
   2. Environment variables (``MAMBU_*``)
   3. ``.mambupy.rc`` file in HOME directory
   4. ``mambupy.rc`` file in ``/etc``

.. warning::
  **SECURITY NOTE**: When using multiple configuration methods, ensure
   credentials are properly protected in all storage locations. For
   the file in ``/etc``, it's recommended to set restrictive
   permissions (``600``) and root ownership. For code configurations,
   ensure proper versioning, or no versioning, of credentials that
   must remain private.


Basic Recipes
-------------

1. Working with Clients (``MambuClient``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clients in Mambu represent individual persons. Here are some usage
examples:

.. code-block:: python

   from mambupy.api.mambuclient import MambuClient

   # Get a specific client by ID
   client = MambuClient.get("0512N0025")  # detailsLevel="BASIC" by default

   # Read basic client information
   print(f"Name: {client.firstName} {client.lastName}")
   print(f"ID: {client.id}")
   print(f"State: {client.state}")

   # MambuPy entity properties can also be accessed using dictionary-style interface:
   print(f"Name: {client['firstName']} {client['lastName']}")
   print(f"ID: {client['id']}")
   print(f"State: {client['state']}")

   # You can get the same entity using its Mambu encodedKey:
   client = MambuClient.get("8a099a673f1f25a0013f1fd0a1c318a5")

   # Get all client details, including custom fields:
   client = MambuClient.get("24N12345", detailsLevel="FULL")
   print(f"ID: {client.id}")
   print(f"Addresses: {client.addresses}")  # list of MambuAddress VOs
   print(f"ID Documents: {client.idDocuments}")  # list of MambuIDDocument VOs
   print(f"A custom fields group: {client._customfields_integrante}")  # as they come from Mambu
   print(f"Another custom fields group: {client._datoscrediticios_integrante}")
   # MambuPy extracts each field,
   # and converts it to a MambuPy object and sets it as an entity property:
   print(
       f"One of the fields from _customfields_integrante group:
       {client.Actividad_economica_Clients}"
   )  # MambuEntityCF VO

   # Get multiple clients with filters
   clients = MambuClient.get_all(
       limit=50,  # Results limit
       offset=0,  # Page start
       filters={
           "firstName": "JOSEFA",
           "state": "ACTIVE"
       }
   )
   for client in clients:
       print(f"Client {client.id}: {client.firstName} {client.lastName}")

   # Search clients with advanced search
   clients = MambuClient.search(
       filterCriteria=[
           {"field": "firstName", "operator": "EQUALS", "value": "JOSEFA"}
       ]
   )

.. note::
   About pagination: if you don't send a ``limit`` argument, BY
   DEFAULT MambuPy will handle downloading ALL entities that match the
   criteria (and there could be MANY) by properly paginating Mambu
   requests in chunks given by the ``apipagination`` config
   (``default=50``). BE CAREFUL with resource usage in these cases!

2. Working with Groups (``MambuGroup``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Groups allow grouping clients and managing group loans. Usage
examples:

.. code-block:: python

   from mambupy.api.mambuclient import MambuClient
   from mambupy.api.mambugroup import MambuGroup

   # Get a specific group by ID
   group = MambuGroup.get("24G23446")

   # View group information
   print(f"Group name: {group.groupName}")
   print(f"ID: {group.id}")

   # Get multiple groups with filters
   groups = MambuGroup.get_all(
       limit=20,
       offset=0,
       filters={
           "creditOfficerUsername": "a.alas"
       }
   )
   for group in groups:
       print(f"Group: {group.groupName}")
       print(f"Status: {group.loanCycle}")

   # To get details like group members,
   # the group must be instantiated using detailsLevel="FULL"
   group = MambuGroup.get("25G54321", detailsLevel="FULL")
   members = group.groupMembers
   for member in members:  # MambuClient instances still need to be instantiated one by one
       client = MambuClient.get(member.clientKey)
       print(f"Member {client.id}: {client.firstName} {client.lastName}")


3. Working with Loans (``MambuLoan``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loans represent loan accounts. Usage examples:

.. code-block:: python

   from mambupy.api.mambuloan import MambuLoan

   # Get a specific loan by ID
   loan = MambuLoan.get("54321")

   # View basic loan information
   print(f"Loan ID: {loan.id}")
   print(f"Status: {loan.accountState}")

   # MambuPy automatically converts data types obtained via REST:
   print(f"Disbursement date: {loan.disbursementDetails.disbursementDate}")  # datetime object
   print(f"Amount: {loan.loanAmount}")  # float

   # Get multiple loans with filters
   loans = MambuLoan.get_all(
       limit=100,
       offset=0,
       filters={
           "accountState": "ACTIVE_IN_ARREARS",
           "creditOfficerUsername": "a.alas",
       }
   )
   for loan in loans:
       print(f"Loan ID: {loan.id}")
       print(f"Amount: {loan.loanAmount}")
       print(f"Status: {loan.accountState}")

   # Get the loan holder (can be client or group)
   holder = loan.get_accountHolder()  # instantiates a MambuPy entity
   if loan.accountHolderType == 'GROUP':
       print(f"Holder (Group) {holder.id}: {holder.groupName}")
   else:
       print(f"Holder (Client) {holder.id}: {holder.firstName} {holder.lastName}")

   # Get payment schedule
   loan.get_schedule()  # loan.schedule property doesn't exist before this
   installments = loan.schedule
   for installment in installments:
       print(f"Installment: {installment.number}")
       print(f"Status: {installment.state}")
       print(f"Due date: {installment.dueDate}")
       print(f"Principal paid: {installment.principal['amount']['paid']}")

   # Get transactions
   loan.get_transactions()  # loan.transactions property doesn't exist before this
   transactions = loan.transactions
   for transaction in transactions:
       print(f"Transaction: {transaction.id}")
       print(f"Type: {transaction.type}")
       print(f"Date: {transaction.valueDate}")
       print(f"Amount: {transaction.amount}")


4. Working with Branches, Centres and Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Branches, centres and users are important organizational elements in
Mambu. Here are some examples of how to work with them:

``MambuBranch``
+++++++++++++++

.. code-block:: python

   from mambupy.api.mambubranch import MambuBranch

   # Get a specific branch
   branch = MambuBranch.get("CCAZ")
   print(f"Branch: {branch.name}")
   print(f"State: {branch.state}")

   # Get all branches
   branches = MambuBranch.get_all()
   for branch in branches:
       print(f"ID: {branch.id}, Name: {branch.name}")

``MambuCentre``
+++++++++++++++

.. code-block:: python

   from mambupy.api.mambucentre import MambuCentre

   # Get a specific unit
   centre = MambuCentre.get("TribeAZ-1")
   print(f"Unit: {centre.name}")
   print(f"Branch: {centre.assignedBranchKey}")

   # Get all units
   centres = MambuCentre.get_all()
   for centre in centres:
       print(f"ID: {centre.id}, Name: {centre.name}")
       
   # Get units belonging to a specific branch:
   centres = MambuCentre.get_all(
       filters={
           "branchId": "CCAZ",
       }
   )

``MambuUser``
+++++++++++++

.. code-block:: python

   from mambupy.api.mambuuser import MambuUser

   # Get a specific user
   user = MambuUser.get("a.alas", detailsLevel="FULL")
   print(f"User: {user.firstName} {user.lastName}")
   print(f"Role: {user.role}")  # role doesn't come with detailsLevel "BASIC"

   # instantiate user's role in a MambuRole entity,
   # replacing the role property with the instantiated object:
   user.get_role()
   print(f"Role: {user.role}")  # MambuRole object

   # Get all users from a specific branch
   users = MambuUser.get_all(
       filters={"branchId": "CCAZ"}
   )  # BEWARE of missing limit parameter!
   # MambuPy will download by pages according to mambuconfig.apipagination config
   # but without a limit, it will make as many requests as needed
   # to exhaust all entities from Mambu


Assignments and Relationships
+++++++++++++++++++++++++++++

.. code-block:: python

   from mambupy.api.mambuclient import MambuClient
   from mambupy.api.mambugroup import MambuGroup
   from mambupy.api.mambuloan import MambuLoan

   # Check client assignments
   client = MambuClient.get("0512N0025")

   # Branch
   print(f"Assigned branch: {client.assignedBranchKey}")
   # instantiate the branch assigned to the client:
   client.get_assignedBranch()
   print(f"Assigned branch: {client.assignedBranch}")  # MambuBranch object

   # Centre
   print(f"Assigned centre: {client.assignedCentreKey}")
   # instantiate the centre assigned to the client:
   client.get_assignedCentre()
   print(f"Assigned centre: {client.assignedCentre}")  # MambuCentre object

   # NOTE: if an entity doesn't have an assignment level, e.g. user,
   # MambuPy would raise an exception

   # Also works with Groups
   group = MambuGroup.get("24G23446")
   print(f"Assigned officer: {group.assignedUserKey}")
   # instantiate the user assigned to the group
   group.get_assignedUser()
   print(f"Assigned officer: {group.assignedUser}")  # MambuUser object

   # And also works with Loans
   loan = MambuLoan.get("54321")
   print(f"Assigned branch: {loan.assignedBranchKey}")
   print(f"Assigned centre: {loan.assignedCentreKey}")
   print(f"Assigned officer: {loan.assignedUserKey}")

   loan.get_assignedBranch()
   loan.get_assignedCentre()
   loan.get_assignedUser()

.. note::
   These ``get_assigned*`` methods create properties in the object and
   contain the complete instance of the related entity. It's more
   efficient than creating instances manually, avoiding the need to
   remember the property with the related encodedKey, and allows
   direct access to all attributes of the related object.

.. important::
   Assignments are crucial for hierarchical organization in Mambu. A
   client must always be assigned to a branch and can be assigned to a
   centre and a credit officer. The same applies to groups. These
   assignments are automatically inherited by the loan accounts of the
   client or group owner of the account.

5. Advanced Searches
~~~~~~~~~~~~~~~~~~~~

Examples of more complex searches. See more information about their
usage in the `Mambu API documentation
<https://api.mambu.com/#searching-for-records>`_:

.. code-block:: python

   from mambupy.api.mambugroup import MambuGroup
   from mambupy.api.mambuloan import MambuLoan

   # Search loans by specific criteria
   loans = MambuLoan.search(
       filterCriteria=[
           {"field": "accountState", "operator": "EQUALS", "value": "ACTIVE_IN_ARREARS"},
           {"field": "amount", "operator": "MORE_THAN", "value": 750000}
       ],
       limit=20
   )  # here we are limiting the maximum results, no matter how many there are in
   # Mambu, it will only bring 20. You can use this argument along with offset to
   # paginate on your own. If you omit the limit parameter, MambuPy will handle
   # this bringing ALL entities that meet the criteria in chunks of
   # mambuconfig.apipagination, which may delay an excessive time to load, or even
   # fill your computer's RAM after a while


6. Exception Handling
~~~~~~~~~~~~~~~~~~~~~

MambuPy maintains an exception handling scheme for most error
conditions. While this handling decision is opinionated, the exception
structure maintains consistency regarding the meaning of thrown
exceptions, and also responds to the library's objective of
abstracting low-level details of the way it communicates with the
Mambu API, including details such as format (json), protocol (HTTP),
and therefore also response codes.

.. note::
   * An exception from Mambu whose response includes an ``errorCode``
     is handled as ``MambuError``.  All ``errorCodes`` handled by
     Mambu are documented `here
     <https://support.mambu.com/docs/api-response-error-codes>`_.  See
     more information in the `Mambu API documentation
     <https://api.mambu.com/#responses>`_.

   * An exception derived from the inability to contact the Mambu API
     is handled as ``MambuCommError``.  A ``MambuCommError`` is a type
     of ``MambuError``.

   * Any other exception thrown directly by MambuPy is handled as
     ``MambuPyError``.  All exceptions thrown by MambuPy, including
     ``MambuError`` and therefore ``MambuCommError`` are
     ``MambuPyError``.

Generic MambuPy error, in this case for sending an argument with an
invalid type

.. code-block:: python

   from mambupy.api.mambuclient import MambuClient

   clients = MambuClient.get_all(
       limit=10,
       offset="0"  # offset parameter must be an int
   )

Would throw the following exception

.. code-block:: bash   

   MambuPyError: offset must be integer

Tries to instantiate a client that doesn't exist in Mambu:

.. code-block:: python

   from mambupy.api.mambuclient import MambuClient

   client = MambuClient.get("I DONT EXIST")

Exception (note the ``errorCode: 301``, and the response code also
included: ``404``)

.. code-block:: bash

   MambuError: 301 (404) - INVALID_CLIENT_ID

log:

.. code-block:: bash

   404 Client Error:  for url: https://podemos.sandbox.mambu.com/api/clients/NOEXISTO?detailsLevel=BASIC on GET request: params {'detailsLevel': 'BASIC'}, data None, headers [('Accept', 'application/vnd.mambu.v2+json'))]
   HTTPError, resp content: b'{"errors":[{"errorCode":301,"errorReason":"INVALID_CLIENT_ID"}]}'

Invalid credentials

.. code-block:: python

   mambuconfig.apipwd="BLAHBLAHBLAH"  # assuming there's no environment variable or mambupy.rc file with this configuration set
   client = MambuClient.get("0512N0025")

Exception (``errorCode: 2, response code: 401``)

.. code-block:: bash

   MambuError: 2 (401) - INVALID_CREDENTIALS (credentials)

log:

.. code-block:: bash

   401 Client Error:  for url: https://podemos.sandbox.mambu.com/api/clients/0512N0025?detailsLevel=BASIC on GET request: params {'detailsLevel': 'BASIC'}, data None, headers [('Accept', 'application/vnd.mambu.v2+json')]
   HTTPError, resp content: b'{"errors":[{"errorCode":2,"errorSource":"credentials","errorReason":"INVALID_CREDENTIALS"}]}'

Invalid URL

.. code-block:: python

   mambuconfig.apiurl="BLAHBLAHBLAH"  # assuming there's no environment variable or mambupy.rc file with this configuration set
   client = MambuClient.get("0512N0025")

Exception

.. code-block:: bash

   MambuCommError: Unknown comm error with Mambu: HTTPSConnectionPool(host='BLAHBLAHBLAH', port=443): Max retries exceeded with url: /api/clients/0512N0025?detailsLevel=BASIC (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x706a6a2cb4d0>: Failed to resolve 'BLAHBLAHBLAH' ([Errno -2] Name or service not known)"))

log:

.. code-block:: bash

   HTTPSConnectionPool(host='BLAHBLAHBLAH', port=443): Max retries exceeded with url: /api/clients/0512N0025?detailsLevel=BASIC (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x706a6a2cb4d0>: Failed to resolve 'BLAHBLAHBLAH' ([Errno -2] Name or service not known)")) Exception () on GET request: url https://BLAHBLAHBLAH/api/clients/0512N0025, params {'detailsLevel': 'BASIC'}, data None, headers [('Accept', 'application/vnd.mambu.v2+json')]

.. note::
   By the way, MambuPy performs up to 5 retry attempts to contact Mambu in case of failure (response codes 429, 502, 503 or 504)


Next Recipes
~~~~~~~~~~~~
.. todo::
   * Custom Fields Search
   * Entity Updates
   * Updating Custom Fields
   * Entity Creation
   * Approving, Disbursing, Paying and Closing a Loan Account
   * Account and Group Reassignment
   * Reassignment of Users with Assigned Accounts and Groups
   * Using an Entity with Different Authentication Credentials than the ones Configured by default
   * How to configure logging for MambuPy
