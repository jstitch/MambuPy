.. _mambu_rest:

MambuPy for REST
================

REST module of MambuPy implements communication with Mambu using
Mambu's REST API.

V1 of MambuPy implements v1 of `Mambu's API REST
<https://api.mambu.com/v1>`_. There's work in progress to implement v2
of MambuPy, which will use `Mambu's API REST v2
<https://api.mambu.com/>`_.

Basically, MambuPy REST is a set of classes in Python that uses
`requests <https://docs.python-requests.org>`_ module to communicate
with Mambu's API REST.

As all modules in MambuPy, REST module must be configured with a user
with correct permissions with API access rights.

If you're looking for MambuPy v2 REST developing status, documentation
and design principles, please go here: :doc:`mambu_rest_v2`

How MambuPy REST module works
-----------------------------

Every MambuPy REST object inherits from a common class,
:py:class:`MambuPy.rest.mambustruct.MambuStruct`.

Also, there are two types of MambuPy REST objects: single entities,
and iterable entities.

Single entities simply inherit from MambuStruct.

Iterable entities also inherit from MambuStruct but also implement the
`Iterator
<https://docs.python.org/3.8/library/stdtypes.html#iterator-types>`_
protocol.

Since everything is related to Mambu's REST API, it all boils down to
JSON objects. If translated to python, JSON objects are either:
dictionaries or lists (either of which may recursively include more
dictionaries, lists, and of course plain data)

Single entities from Mambu
++++++++++++++++++++++++++

When you get a single entity from Mambu (say *Client*, *Group*, *Loan
Account*, etc.), you usually request a **GET** operation and Mambu
responds with a corresponding JSON object, such as::

  {
    "encodedKey": "abcdef1234567890",
    "id": "ABC432",
    "creationDate": "2022-05-03T21:00:00-05:00",
    "accountState": "ACTIVE",
    "disbursementDetails": {
      "encodedKey": "987654321fedcba",
      "disbursementDate": "2022-05-04T12:00:05-05:00"
    },
    "_list_of_values_in_set_cf": [
      {
        "some_value": "12345.67",
        "another": "TESTING1"
      },
      {
        "some_value": "0.0",
        "another": "TESTING2"
      }
    ]
  }

As you can observe, you can, if you wish, translate this as a Python
dictionary, having some keys with string values, and having others
with lists and dictionaries, which in turn may have more nested data
structures:

.. code-block:: python

  d = {"encodedKey": "abcdef1234567890",
       "id": "ABC432",
       "creationDate": "2022-05-03T21:00:00-05:00",
       "accountState": "ACTIVE",
       "disbursementDetails": {
           "encodedKey": "987654321fedcba",
           "disbursementDate": "2022-05-04T12:00:05-05:00"
       },
       "_list_of_values_in_set_cf": [
           {"some_value": "12345.67",
            "another": "TESTING1"
           },
           {"some_value": "0.0",
            "another": "TESTING2"}]}

The principal design decision we made on MambuPy is to directly
exploit this feature and translate the JSON objects to Python objects.

The other important decision is that MambuPy translates the data from
the JSON object directly to python's native data. For example, when
the data can be translated in to a floating point number, the
resulting dictionary gets a floating point number as its value. The
following are the the data types detected by MambuPy, directly
translated as python's native types:

* :py:obj:`int`, for instance :py:data:`"123"` is translated as
  :py:data:`123`
* :py:obj:`float`, :py:data:`"123.45"` is translated as
  :py:data:`123.45`
* :py:obj:`datetime.datetime`, it's not a native type, but we consider
  it to be of really high value to convert it. There are some gotchas
  to consider when using datetime objects, as any developer using
  datetimes may know. Please refer to the corresponding section below.
* :py:obj:`str` are the default case, every other case not being able
  to be converted to some of the previous types is left as is.

All else been given, the result of this conversion would result on the
following dictionary:

.. code-block:: python

  d = {"encodedKey": "abcdef1234567890",
       "id": "ABC432",
       "creationDate": datetime(2022, 5, 3, 21, 0),
       "accountState": "ACTIVE",
       "disbursementDetails": {
           "encodedKey": "987654321fedcba",
           "disbursementDate": datetime(2022, 5, 4, 12, 0, 5)
       },
       "_list_of_values_in_set_cf": [
           {"some_value": 12345.67,
            "another": "TESTING1"
           },
           {"some_value": 0.0,
            "another": "TESTING2"}]}

In essence, that would be the way MambuPy objects work, they store
this dictionary inside itselves. In fact, every MambuPy object has
dictionary-like behaviour, since this data is what in essence conforms
the entity in Mambu.

Several other methods, besides the dictionary-like ones, support this
objects.

Every module at :py:mod:`MambuPy.rest` has a single-entity class used
to instantiate single entities from Mambu.

When you wish to instantiate certain Mambu entity, you give the
entity's Mambu ID to its constructor. If the ID exists in Mambu, the
object will be instantiated.

Iterable entities from Mambu
++++++++++++++++++++++++++++

Iterable entities implement the `Iterator
<https://docs.python.org/3.8/library/stdtypes.html#iterator-types>`_
protocol.

:py:class:`MambuPy.rest.mambustruct.MambuStructIterator` class enables
iteration. It implements the :py:meth:`iterator.__next__` method.

Several modules at :py:mod:`MambuPy.rest` have iterable entities
classes used to instantiate iterable entities from Mambu. Its name is
usually the single-entity class, pluralized. This class implements the
:py:meth:`iterator.__iter__` method, which in turn returns a
:py:class:`MambuPy.rest.mambustruct.MambuStructIterator` object.

When you wish to instantiate several Mambu entities, you give several
filters to its constructor. When requested, MambuPy converts the
resulting list in a list of single-entity classes.

urlfuncs
++++++++

The connect() method
++++++++++++++++++++

Examples
--------

API Docs
--------

Steps to instantiate a certain MambuEntity (a
:py:obj:`MambuPy.rest.mambuclient.MambuClient` for example):

1. Get the Mambu's entity ID, and the level of detail you wish to
   retrieve.

2. Import the correct module from MambuPy:

.. code-block:: python

  from MambuPy.rest import mambuclient

3. Instantiate the object you are retrieving:

.. code-block:: python

  client = mambuclient.MambuClient(entid="MY_CLIENT_ID")

Go to :py:obj:`MambuPy.rest` for the complete API reference.
