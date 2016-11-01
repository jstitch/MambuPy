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


The DB way is currently very basic. All schemas must import schema_orm,
this is because all need to be in the same session, if you want to import
all schemas at once, just import schema_mambu, but if you want to use
schemas by separately you need to be careful because there is some kind of
dependency, by example, you use schema_groups to get groups, a group can
have loans, but, to get them you need to import schema_loans first.


Suggested actions TODO:

- Implement a lot of lacking fields on the currently available tables.

- Implement a lot of lacking tables from the Mambu DB schema.


Also, unit testing is currently very basic.

The purpose is to achive TDD when implementing features or correcting
bugs.

Please also read the TODO file for more suggestions
"""
