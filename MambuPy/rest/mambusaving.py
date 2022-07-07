# coding: utf-8
"""Mambu Savings objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuSaving holds a savings account.

MambuSavings holds a list of savings accounts.

Uses mambugeturl.getsavings as default urlfunc.
"""


from ..mambugeturl import getsavingssurl
from .mambustruct import MambuStruct, MambuStructIterator, MambuError

mod_urlfunc = getsavingssurl

# Objeto con una Cuenta desde Mambu
class MambuSaving(MambuStruct):
    """A Savings account from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    saving account you wish to retrieve.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(
            self, urlfunc, entid, custom_field_name="customFieldValues", *args, **kwargs
        )

    def preprocess(self):
        """Preprocessing.

        Each active custom field is given a 'name' key that holds the field
        name, and for each keyed name, the value of the custom field is
        assigned.
        """
        super(MambuSaving, self).preprocess()

    def setUser(self, *args, **kwargs):
        """Adds the user for this savings account to a 'user' field.

        User is a MambuUser object.

        Returns the number of requests done to Mambu.
        """
        from .mambuuser import MambuUser

        try:
            user = MambuUser(entid=self["assignedUserKey"], *args, **kwargs)
        except KeyError:
            err = MambuError("La cuenta %s no tiene asignado un usuario" % self["id"])
            err.noUser = True
            raise err

        self["user"] = user

        return 1


class MambuSavings(MambuStruct):
    """A list of savings accounts from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the savings accounts according to
    any other filter you send to the urlfunc.
    """

    def __init__(
        self, urlfunc=mod_urlfunc, entid="", itemclass=MambuSaving, *args, **kwargs
    ):
        """By default, entid argument is empty. That makes perfect
        sense: you want several groups, not just one.
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a MambuSaving (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        MambuSaving (or your own itemclass) just created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
          corresponding id to entid to each itemclass, telling MambuStruct
          not to connect() by default. It's desirable to connect at any
          other further moment to refresh some element in the list.
        """
        for n, l in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            saving = self.itemclass(urlfunc=None, entid=None, *args, **kwargs)
            saving.init(l, *args, **kwargs)
            saving._MambuStruct__urlfunc = getsavingssurl
            self.attrs[n] = saving
