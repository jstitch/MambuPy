# coding: utf-8
"""Mambu Branches objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuBranch holds a branch.

MambuBranches holds a list of branches.

Uses mambugeturl.getbranchesurl as default urlfunc
"""


from ..mambugeturl import getbranchesurl
from .mambustruct import MambuStruct, MambuStructIterator

mod_urlfunc = getbranchesurl


class MambuBranch(MambuStruct):
    """A Branch from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    branch you wish to retrieve.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(
            self, urlfunc, entid, custom_field_name="customFieldValues", *args, **kwargs
        )

    def setUsers(self, *args, **kwargs):
        """Adds the active users for this branch to a 'users' field.

                Returns the number of requests done to Mambu.

        .. todo:: since pagination logic was added, is not always true that
                  just 1 request was done. It may be more! But since request
                  counter singleton holds true information about how many requests
                  were done to Mambu, in fact this return value may be obsolete
        """
        try:
            self.mambuuserclass
        except AttributeError:
            from .mambuuser import MambuUsers

            self.mambuusersclass = MambuUsers

        usrs = [
            us
            for us in self.mambuusersclass(branchId=self["id"], *args, **kwargs)
            if us["userState"] == "ACTIVE"
        ]
        self["users"] = usrs

        return 1


class MambuBranches(MambuStruct):
    """A list of Branches from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the branches according to any
    other filter you send to the urlfunc.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several branches, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

                You iterate over each element of the responded List from Mambu,
                and create a Mambu Branch object for each one, initializing them
                one at a time, and changing the attrs attribute (which just
                holds a list of plain dictionaries) with a MambuBranch just
                created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
                  corresponding id to entid to each MambuBranch, telling
                  MambuStruct not to connect() by default. It's desirable to
                  connect at any other further moment to refresh some element in
                  the list.
        """
        for n, b in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mambubranchclass
            except AttributeError:
                self.mambubranchclass = MambuBranch

            branch = self.mambubranchclass(urlfunc=None, entid=None, *args, **kwargs)
            branch.init(b, *args, **kwargs)
            branch._MambuStruct__urlfunc = getbranchesurl
            self.attrs[n] = branch
