# coding: utf-8
"""Mambu Activity objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuActivity
   MambuActivities

MambuActivity holds a mambu activity. Don't instantiate this class
directly. Look at MambuActivity pydoc for further info.

MambuActivities holds a list of activities.

Uses mambuutil.getactivitiesurl as default urlfunc
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getactivitiesurl


mod_urlfunc = getactivitiesurl

class MambuActivity(MambuStruct):
    """A loan Activity from Mambu.

    Don't instantiate this class directly. It's mostly used by
    MambuActivities to configure each of its elements as
    MambuActivity objects. There's no suitable urlfunc to use to
    retrieve just a specific transaction from a loan account. In fact,
    you can look at the code of MambuActivities.convertDict2Attrs(),
    it uses urlfunc and entid = None , so no connection to Mambu will be
    made, never, for any particular MambuActivity object.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __repr__(self):
        """Instead of the default id given by the parent class, shows
        the transactionid of the transaction.
        """
        try:
            return self.__class__.__name__ + " - activityid: %s" % self['activity']
        except KeyError:
            return self.__class__.__name__ + " - activityid: %s" % self['activity']


class MambuActivities(MambuStruct):
    """A list of loan Activities from Mambu.

    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Activity object for each one, initializing
        them one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuActivity just
        created.

        """
        for n,a in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            activity = MambuActivity(urlfunc=None, entid=None, *args, **kwargs)
            activity.init(a, *args, **kwargs)
            self.attrs[n] = activity

