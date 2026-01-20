.. _mambu_rest_v2:

MambuPy for REST V2
===================

MambuPy v2 is a design and development effort to make MambuPy
compatible with `Mambu's REST API v2 <https://api.mambu.com/>`_.

Besides the compatibility with the more recent version of Mambu's API,
the main design objective of MambuPy v2 is to have a good design and
best practices, with a KISS and DRY philosophy.

The idea behind MambuPy v2 is to implement functionality to interact
with Mambu using Mambu's REST API endpoints. Even if one of its
objectives is to implement each and every endpoint offered by the REST
API, the implementation should not be thinked about as just making
"Python endpoints" for Mambu. The idea is to **offer Mambu's
functionality, through the REST API, with python technology**.

MambuPy v2 also pretends to achieve at some stage a unification of
interfaces, so ORM and REST MambuPy modules would be managed in the
same fashion. In fact we pretend to use the very same objects for both
interfaces, specifying a specific type of connection to some Mambu
data source (may it be the API REST or a connection to a database
backup as you pick).

Current Status
--------------

MambuPy v2 is officially released

Activities is currently not supported by Mambu REST API v2, so
we are unable to implement any functionality around it, so you'll
have to rely on the old v1 rest.mambuactivities non-supported module.

What follows, is a description of how MambuPy v2 is designed and some
implementation details are given, with the purpose of explaining how
it currently works.

Class Diagrams
--------------

Every entity of Mambu inherits from
:py:class:`MambuPy.api.entities.MambuEntity` or variations of it,
which implements several interfaces to connect with Mambu.

The main (and common to all entities) interface, gives the **get** and
**get_all** endpoints to any Entity, since at least every entity
implemented in MambuPy supports both functionality.

There are also other interfaces that gives extra functionalities to
entities inheriting from them. Currently supported:

  - :py:class:`MambuPy.api.entities.MambuEntityWritable`: create,
    patch and update endpoints
  - :py:class:`MambuPy.api.entities.MambuEntitySearchable`: search endpoint
  - :py:class:`MambuPy.api.entities.MambuEntityAttachable`: attached documents support
  - :py:class:`MambuPy.api.entities.MambuEntityCommentable`: commenting support

There are also other interfaces for some extra functionality, not
directly related with endpoints at Mambu REST API. Look at
:py:mod:`MambuPy.api.entities` for further information.

The following diagram illustrates the currently implemented entities:

.. image:: /_static/mambupyv2_entities.png

MambuStruct
+++++++++++

:py:class:`MambuPy.api.mambustruct.MambuStruct` is a fundamental
class for Mambu Entities functionality.

v2 sues several classes, organized in an ordered fashion.

The real father of all MambuPy v2 classes is
:py:class:`MambuPy.api.classes.MambuMapObj`, which implements
dictionary and object-like behaviour to access the fundamental data
structure of MambuPy v2 entities:
:py:class:`MambuPy.api.mambustruct.MambuStruct._attrs`

Then, MambuStruct inherits from this, implementing the conversion,
serialization, extraction and update behavior over the _attrs
dictionary. This is similar to what we've described at
:ref:`mambu_rest_single_entities`, but with further functionality.

.. image:: /_static/mambupyv2_entities_ancestors.png
           :align: center

At last, comes the real
action. :py:class:`MambuPy.api.entities.MambuEntity` inherits from
MambuStruct, implementing real Mambu operations for a given
entity.

Mambu Entities raison d'être is to implement those entities with which
you may interact using Mambu web: clients, groups, loan accounts,
branches, users, etc.

However, MambuEntity is not the only one inheriting from
MambuStruct...

ValueObjects
++++++++++++

When you make a GET request to some Mambu endpoint, let's say to
retrieve a Centre, you get something like this::

  {
    "_Example_Custom_Fields": {
      "exampleCheckboxField": "TRUE",
      "exampleFreeTextField": "A free text field up to 255 characters in length",
      "exampleNumberField": "46290",
      "exampleSelectField": "Option 1"
    },
    "_centres_custom_field_set": {
      "centre_cf_1": "string",
      "cntr_cf_2": "TRUE",
      "cntr_cf_usr_lnk": "string"
    },
    "_cntr_cf_grp": [
      {
        "cntr_cf_Grp_1": "string",
        "cntr_cf_grp_2": "option 1",
        "cntr_cf_slct_2": "dep 1 a"
      },
      {
        "cntr_cf_Grp_1": "other string",
        "cntr_cf_grp_2": "option 2",
        "cntr_cf_slct_2": "dep 2 b"
      }
    ],
    "addresses": [
      {
        "city": "string",
        "country": "string",
        "encodedKey": "string",
        "indexInList": 0,
        "latitude": 0,
        "line1": "string",
        "line2": "string",
        "longitude": 0,
        "parentKey": "string",
        "postcode": "string",
        "region": "string"
      }
    ],
    "assignedBranchKey": "string",
    "creationDate": "2016-09-06T13:37:50+03:00",
    "encodedKey": "string",
    "id": "string",
    "lastModifiedDate": "2016-09-06T13:37:50+03:00",
    "meetingDay": "string",
    "name": "string",
    "notes": "string",
    "state": "ACTIVE"
  }

As you may notice, the Centre object has attribute of many different
types (translated to python's native data types with a call of
:py:meth:`MambuPy.api.mambustruct.MambuStruct._convertDict2Attrs`).

But what about such *types* conformed by structures of native data
types? Let's talk about addresses::

    "addresses": [
      {
        "city": "string",
        "country": "string",
        "encodedKey": "string",
        "indexInList": 0,
        "latitude": 0,
        "line1": "string",
        "line2": "string",
        "longitude": 0,
        "parentKey": "string",
        "postcode": "string",
        "region": "string"
      }
    ]

As you may note, it's kind of a list of element. And each element
includes several fields, always the same fields, which conform an
**Address**.

Also, there are no endpoints in Mambu's REST API to interact with
addresses. They're just part of some entity that may have addresses on
it (Centres in this example, but also Branches, Clients, and Groups).

Wouldn't it be nice to manage this structures using MambuPy's
facilities?

This is where MambuPy v2 Value Objets come in to play. Inheriting
every functionality MambuStruct can offer, specially what its father
MambuMapObj has to offer, a MambuPy ValueObject is just what its name
implies: an object that acquires certain value.
