"""MambuPy, an API library to access Mambu objects.

Currently, there are two different ways to access Mambu objects:

1) Via Mambu REST API

2) Via a DB backup retrieved from Mambu


The REST API way is the currently most developed code on MambuPy.

It has a lot of objects which model some Mambu entity.

Every object inherits from the base MambuStruct class. Start at the
documentation there for more info on how it works.

Suggested actions TODO:

- Implement objects to make POST requests. The suggestion may be to use
MambuStruct, to default the __init__ to make a POST request (via the
data argument) and the attrs attribute to store the elements of the
response that Mambu gives when a successful POST is achieved.

- Implement a lot of other Mambu entities available through GET requests
on Mambu.

- Implement a lot of lacking GET filters on the currently available
Mambu objects, inside the urlfuncs on the mambuutil module.

A lot of TODO comments are inserted inside the pydocs of the code
itself. Please read them for suggestions on work need to be done.


On the DB way all schema modules must import schema_orm, this module
holds basic SQLAlchemy global variables, such as the Base for all
tables (which needs to be the same one for everyone), or the default
session created by importing any of this modules. If you need to
import all schemas at once, just import schema_mambu, which should
hold them all. If, on the other hand, you want to use a specific
schema module, just be careful when dependencies happen, for example
if you use schema_groups to get groups, a group can have loans, but,
to get them you need to import schema_loans too.

You can think of the schema modules structured as follows:

                              schema_orm  (holds the session)

           /           /          |           \

     schema_loans schema_clients schema_groups ...
             (holds the ORM for each table)

           \           \          |           /

              schema_mambu (utility module to import everything)


Suggested actions TODO:

- Implement a lot of lacking fields on the currently available tables.

- Implement a lot of lacking tables from the Mambu DB schema.


Also, unit testing is currently very basic.

The purpose is to achive TDD when implementing features or correcting
bugs.

Please also read the TODO file for more suggestions
"""
