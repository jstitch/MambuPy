# coding: utf-8
"""Mambu Roles objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuRole holds a user role.

MambuRoles holds a list of user roles.

Uses mambugeturl.getrolesurl as default urlfunc
"""


from ..mambugeturl import getrolesurl
from .mambustruct import MambuStruct, MambuStructIterator

mod_urlfunc = getrolesurl


class MambuRole(MambuStruct):
    """A Role from Mambu."""

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        """Instead of the default id given by the parent class, shows
        the rolename
        """
        return self.__class__.__name__ + " - rolename: '%s'" % self["name"]


class MambuRoles(MambuStruct):
    """A list of Roles from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the roles according to any other
    filter you send to the urlfunc.

    itemclass argument allows you to pass some other class as the
    elements for the list. Why is this useful? You may wish to override
    several behaviours by creating your own MambuRole son class. Pass
    that to the itemclass argument here and voila, you get a list of
    YourMambuRole class using MambuRoles instead of plain old MambuRole
    elements.

    If you wish to specialize other Mambu objects on MambuPy you may
    do that. Mind that if you desire that the iterable version of it
    to have elements of your specialized class, you need to change
    the logic of the constructor and the convert_dict_to_attrs method in
    the iterable class to use some sort of itemclass there too.
    Don't forget to submit the change on a pull request when done
    ;-)
    """

    def __init__(
        self, urlfunc=mod_urlfunc, entid="", itemclass=MambuRole, *args, **kwargs
    ):
        """entid argument is empty. That makes perfect
        sense: you always get serveral roles from Mambu REST API
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Role (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        MambuUser (or your own itemclass) just created.
        """
        for n, u in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mamburoleclass
            except AttributeError:
                self.mamburoleclass = MambuRole

            role = self.mamburoleclass(urlfunc=None, entid=None, *args, **kwargs)
            role.init(u, *args, **kwargs)
            role._MambuStruct__urlfunc = getrolesurl
            self.attrs[n] = role
