""" MambuPy's REST package.

Objects using `Mambu REST API
<https://developer.mambu.com/customer/en/portal/articles/1162276-rest-apis-overview/>`_

.. autosummary::
   :toctree: _autosummary

    MambuPy.rest.mambustruct
    MambuPy.rest.mambuclient
    MambuPy.rest.mambugroup
    MambuPy.rest.mambuloan
    MambuPy.rest.mamburepayment
    MambuPy.rest.mambutransaction
    MambuPy.rest.mambuproduct
    MambuPy.rest.mambubranch
    MambuPy.rest.mambucentre
    MambuPy.rest.mambuactivity
    MambuPy.rest.mambutask
    MambuPy.rest.mambusaving
    MambuPy.rest.mambusavingtransaction
    MambuPy.rest.mambutransactionchannel
    MambuPy.rest.mambuuser
    MambuPy.rest.mamburoles


The REST API way is the currently most developed code on *MambuPy*.

Lives under the :any:`MambuPy.rest` package

It has a lot of objects which model some Mambu entity.

Every object inherits from the parent :any:`mambustruct.MambuStruct`
class. Start at the documentation there for more info on how it works.

.. todo:: Implement objects to make POST requests. The suggestion may be to use
          MambuStruct, to default the __init__ to make a POST request (via the data
          argument) and the attrs attribute to store the elements of the response that
          Mambu gives when a successful POST is achieved.
.. todo:: Implement a lot of other Mambu entities available through GET requests on
          Mambu.
.. todo:: Implement a lot of lacking GET filters on the currently available Mambu
          objects, inside the urlfuncs on the mambuutil module.
.. todo:: A lot of TODO comments are inserted inside the pydocs of the code
          itself. Please read them for suggestions on work need to be done.
"""

from .. import mambuconfig, mambuutil
