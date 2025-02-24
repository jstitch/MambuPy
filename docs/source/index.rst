=======
MambuPy
=======

MambuPy is a Python library designed to interact with the Mambu API, a
leading cloud financial services platform. This library facilitates
integration with Mambu, allowing developers to automate operations,
manage clients, groups, loans, and transactions efficiently through an
intuitive Pythonic interface.

.. note::
   MambuPy is distributed under the GNU GPL v3 license, it is free
   software and your collaboration is welcome:
   https://gitlab.com/jstitch/MambuPy

.. important::

   The basic conceptual idea behind MambuPy is to be a library that
   provides an abstraction layer over Mambu's REST API, simplifying
   common tasks such as managing clients, groups, loans, among others.

   It is designed to be easy to use while maintaining the flexibility
   needed for complex financial operations, abstracting low-level
   details such as request handling, authentication, pagination, data
   serialization/deserialization, timezones, retries on failures,
   idempotency for retrying write operations, etc. The idea here is:
   you want to interact with a Mambu Client or Group, not with the
   technical details behind the implementation of that interaction.

   And even other not-so-low-level details, like the fact that Mambu
   handles encodedKeys to identify entities - why do you need to know
   that the `assignedBranchKey` field corresponds to the encodedKey of
   the Branch that a Group is assigned to when all you really need is
   to know and interact with that Branch?  Or the "detail" that
   accessing custom fields must be done through the aspects with which
   Mambu implements them: using field sets and groups json objets. Do
   you really want to reach your "Nationality" field via
   `client._client_details["Nationality"]`? If Nationality is a client
   property, why not simply reach it via `client.Nationality`?

Important References
--------------------

Here are some official resources and relevant documentation:

* `Official MambuPy Repository on GitLab <https://gitlab.com/jstitch/MambuPy>`_
* `MambuPy Releases on PyPi <https://pypi.org/project/MambuPy/>`_
* `Official Mambu REST API v2 Documentation <https://api.mambu.com>`_
* `Official Mambu Developer Documentation <https://support.mambu.com/docs/developer-overview>`_
* `Mambu Community <https://community.mambu.com>`_ - Official forum for developers and users

.. note::
   Some code conventions break certain 100% Pythonic code best
   practices. For example, ``camelCase`` is used instead of
   ``snake_case`` in entity properties. This is a design decision of
   the library dictated by how Mambu's REST API, and Mambu itself,
   deliver their information. Mambu is built in Java and its endpoints
   handle nomenclature with camelCase. The decision to use camelCase
   in some parts of MambuPy goes hand in hand with maintaining certain
   compatibility but above all ensuring clean code reading in Python
   compared to the JSON that Mambu's API delivers. It's easier to
   understand that ``loanAmount`` of a credit account is the
   ``loanAmount`` from the response that obtains said account, rather
   than inferring that Mambu delivers a ``loanAmount`` but we decided
   to call it ``loan_amount``.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 1

   intro
   cookbook
   mambu_rest_v2
   mambu_rest
   mambu_orm
   mambupy
   release_notes
   LICENSE


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
