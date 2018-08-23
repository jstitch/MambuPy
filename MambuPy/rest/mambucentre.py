# coding: utf-8
"""Mambu Centres objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuCentre
   MambuCentres

MambuCentre holds a centre.

MambuCentres holds a list of centres.

Uses mambuutil.getcentresurl as default urlfunc
"""


from .mambustruct import MambuStruct, MambuStructIterator
from ..mambuutil import getcentresurl


mod_urlfunc = getcentresurl

class MambuCentre(MambuStruct):
    """A Centre from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    centre you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customFieldValues', *args, **kwargs)


class MambuCentres(MambuStruct):
    """A list of Centres from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the centres according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several centres, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Centre object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuCentre just
        created.

.. todo:: pass a valid (perhaps default) urlfunc, and its
          corresponding id to entid to each MambuCentre, telling
          MambuStruct not to connect() by default. It's desirable to
          connect at any other further moment to refresh some element in
          the list.
        """
        for n,b in enumerate(self.attrs):
           # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            centre = MambuCentre(urlfunc=None, entid=None, *args, **kwargs)
            centre.init(b, *args, **kwargs)
            self.attrs[n] = centre
