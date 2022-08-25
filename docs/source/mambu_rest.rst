.. _mambu_rest:

MambuPy for REST
================

REST module of MambuPy implements communication with Mambu using
Mambu's REST API.

V1 of MambuPy implements v1 of `Mambu's REST API
<https://api.mambu.com/v1>`_. There's work in progress to implement v2
of MambuPy, which will use `Mambu's REST API v2
<https://api.mambu.com/>`_.

Basically, MambuPy REST is a set of classes in Python that uses
`requests <https://docs.python-requests.org>`_ module to communicate
with Mambu's REST API.

As all modules in MambuPy, REST module must be configured with a user
with correct permissions with API access rights.

If you're looking for MambuPy v2 REST developing status, documentation
and design principles, please go here: :doc:`mambu_rest_v2`

How MambuPy REST module works
-----------------------------

Every MambuPy REST object inherits from a common class,
:py:class:`MambuPy.rest.mambustruct.MambuStruct`.

.. image:: /_static/mambupyv1_classdiagram.png

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

.. image:: /_static/mambupyv1_single_and_iterable_entities.png

.. _mambu_rest_single_entities:
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
  datetimes may know. Please refer to the corresponding :ref:`section
  below <datetime-object-gotchas>`.
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
this dictionary inside itselves (in a property named
:py:obj:`MambuPy.rest.mambustruct.MambuStruct.attrs`). In fact, every
MambuPy object has dictionary-like behaviour, since this data is what
in essence conforms the entity in Mambu.

Several other methods, besides the dictionary-like ones, support this
objects.

Every module at :py:mod:`MambuPy.rest` has a single-entity class used
to instantiate single entities from Mambu.

When you wish to instantiate certain Mambu entity, you give the
entity's Mambu ID to its constructor. If the ID exists in Mambu, the
object will be instantiated.

.. image:: /_static/mambupyv1_mambustruct_attrs.png

.. _iterable-entities:

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

.. image:: /_static/mambupyv1_iterables.png

urlfuncs
++++++++

MambuPy uses certain functions to build the URL to contact and request
Mambu's REST API.

:py:mod:`MambuPy.mambuutil` holds a lot of functions that in
themselves call :py:func:`MambuPy.mambuutil.getmambuurl`. The purpose
of this function is to build a :py:obj:`str` with the URL to access
some Mambu's API endpoint.

Each urlfunc function is named ``getSOMETHINGurl``. Its signature is usually:

.. code-block:: python

  def getSOMETHINGurl(idSOMETHING, *args, **kwargs)

``idSOMETHING`` refers to the ID of the ``SOMETHING`` entity at Mambu
(there are some exceptions to this rule).

``idSOMETHING`` is generally (but not always) optional. When you do
not supply an entity's id to certain Mambu's REST API endpoint results
in a request whose response is a list (which as you may recall is
converted into the :ref:`iterable-entities`)

``kwargs`` usually has the query parameters for the URL. This
parameters implement functionality as generic as offsets and limits
for certain endpoint, but also filters that the endpoint gives to
filter out entities from Mambu using the request URL.

The real trick with urlfuncs is that, every MambuPy's REST class uses
one as default. For instance,
:py:class:`MambuPy.rest.mambuclient.MambuClient` uses
:py:func:`MambuPy.mambuutil.getclienturl`, so you don't usually
have to worry about them.

HOWEVER, power users of MambuPy's REST module can tweak their default
use to take advantage of certain endpoints. Let's talk it through an
example:

:py:class:`MambuPy.rest.mambuloan.MambuLoan` uses
:py:func:`MambuPy.mambuutil.getloansurl` as default. This default
behaviour builds the following URL to request certain loan account
at Mambu::

  GET /loans/LOAN_ID

Which will result in a single or iterable
:py:class:`MambuPy.rest.mambuloan.MambuLoan`. If you don't provide a
specific ``LOAN_ID``, you will get several
:py:class:`MambuPy.rest.mambuloan.MambuLoans`, depending on the
additional filters you give to the ``kwargs`` parameter.

However, you can change the default urlfunc that :py:class:`MambuLoan`
accepts, changing it for example with
:py:func:`MambuPy.mambuutil.getgrouploansurl`, building the following
URL::

  GET /groups/GROUP_ID/loans

which will respond with the list of loan accounts
(:py:class:`MambuPy.rest.mambuloan.MambuLoans`) belonging to a certain
group.

So, using the same class, :py:class:`MambuLoan`, you get for free two
different endpoints, ``/loans/LOAN_ID`` and
``/groups/GROUP_ID/loans``, depending only on the urlfunc you pass to
``MambuLoan's`` constructor. Remember that not providing any urlfunc
will use ``getloansurl`` as default.

.. image:: /_static/mambupyv1_mambustruct_attrs.png

The connect() method
++++++++++++++++++++

Now that we know what we need: a dictionary-like object with
properties acquired from the response in JSON from Mambu, request done
using certain urlfunc,
:py:meth:`MambuPy.rest.mambustruct.MambuStruct.connect` glues all this
together following this recipe:

  1. determine the type of request to do (basically the HTTP verb, which
     depends on certain data present on the object)
  2. using the given urlfunc (which may be the default one for the
     object), make the corresponding request to Mambu
  3. the resulting JSON is then preprocessed: if Mambu gave an error
     (say for an invalid Mambu ID), a
     :py:exc:`MambuPy.mambuutil.MambuError` is thrown
  4. if no error was thrown by Mambu,
     :py:meth:`MambuPy.rest.mambustruct.MambuStruct.init` is called,
     which basically executes some custom preprocessing, converts the
     JSON to a :py:obj:`dict` and them some custom postprocessing may be
     executed

The :py:meth:`MambuPy.rest.mambustruct.MambuStruct.connect` also
catches comm errors. If for some reason Mambu is down,
:py:exc:`MambuPy.mambuutil.MambuCommError` is thrown.

The following are the methods involved in step 4:
  - :py:meth:`MambuPy.rest.mambustruct.MambuStruct.preprocess`
  - :py:meth:`MambuPy.rest.mambustruct.MambuStruct.postprocess`
  - :py:meth:`MambuPy.rest.mambustruct.MambuStruct.convertDict2Attrs`

.. image:: /_static/mambupyv1_mambustruct_methods.png

Pagination
~~~~~~~~~~

Also, when retrieving several objects (when the JSON response is a
:py:obj:`list`), Mambu has some restrictions on how many objects will
be retrieved
(:py:const:`MambuPy.mambuutil.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE`),
which basically means pagination must be used. Well, if you like it
that way, you can paginate it yourself.

We thinked it in another manner. We believe this details should be (at
least optionally) omitted. So,
:py:meth:`MambuPy.rest.mambustruct.MambuStruct.connect` also has
default logic to make the pagination for you, and join every single
item you requested in a resulting big list with all the info you
need.

The pro: forget about managing pagination logic by yourself. The cons:
you may end up with some really BIG structures, and the number of the
requests made to Mambu may be of a considerable size too. See the
documentation for the **limit** argument on
:py:meth:`MambuPy.rest.mambustruct.MambuStruct.__init__`

.. image:: /_static/mambupyv1_mambustruct_attrs.png

Configuration
+++++++++++++

As you may read at :py:mod:`MambuPy.mambuconfig`, REST configuration
consists of the following options:

* :py:obj:`MambuPy.mambuconfig.apiurl` - the URL of the Mambu tenant you use.
* :py:obj:`MambuPy.mambuconfig.apiuser` - a Mambu user with API permissions
* :py:obj:`MambuPy.mambuconfig.apipwd` - the password of the user

As :py:mod:`MambuPy.mambuconfig` documentation tells, you can set
these on ``/etc/mambupyrc``, ``$HOME/.mambupy.rc``, on an `ini-format
<https://en.wikipedia.org/wiki/INI_file>`_ style. Home directory RC
file overrides what ``/etc`` file says.

You can also set the environment variables: ``MAMBUPY_APIRUL``,
``MAMBUPY_APIUSER`` and ``MAMBUPY_APIPWD``, which override what RC
files say.

.. _datetime-object-gotchas:

datetime objects gotchas
++++++++++++++++++++++++

As you may read at
`<https://docs.python.org/3/library/datetime.html#aware-and-naive-objects>`_,
datetime objects may be aware or naive.

Aware datetime objects know about timezones and daylight saving time
information. Naive objecst on the other hand do not.

The most simple use of datetime objects is when you use them as
naive. Using the aware feature complicates things a little. On the
flip side being able to differentiate time zones on datetime objects
gives you the ability to make date and time equivalencies, specially
when treating with dates and times across the world.

Mambu gives timezone information insied every datetime field it
uses. MambuPy v1's REST module on the other hand uses naive mode. v2
for MambuPy supports aware mode too.

Examples
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

API Docs
--------

The API documentation is hold at the docstrings of every file at the
:py:mod:`MambuPy.rest` module.
