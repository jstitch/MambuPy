# coding: utf-8
"""Mambu Branches objects.

MambuBranch holds a branch.

MambuBranches holds a list of branches.

Uses mambuutil.getbranchesurl as default urlfunc

Example response from Mambu for branches:
[
 {
  "id": "1",
  "name": "Nicolas Romero",
  "phoneNumber": "12345678",
  "emailAddress": "correo@example.com",
  "branchHolidays": [],
  "encodedKey": "8a70db342e6d595a012e6e7158670f9d",
  "address": {
    "line1": "Niños Heroes #15",
    "line2": "Miguel Hidalgo",
    "city": "Nicolas Romero",
    "region": "Mexico",
    "postcode": "54400",
    "country": "Mexico",
    "indexInList": -1
    "encodedKey": "8a6a80593fc305e1013fc47ad052686b",
    "parentKey": "8a70db342e6d595a012e6e7158670f9d",
  },
  "customFieldValues": []
  "creationDate": "2011-02-28T22:44:05+0000",
  "lastModifiedDate": "2013-07-09T17:36:27+0000",
 },
]

TODO: update this with later responses from Mambu, and perhaps certain
behaviours are obsolete here
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getbranchesurl


mod_urlfunc = getbranchesurl

class MambuBranch(MambuStruct):
    """A Branch from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    branch you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customFieldValues', *args, **kwargs)


    def setUsers(self, *args, **kwargs):
        """Adds the active users for this branch to a 'users' field.

        Returns the number of requests done to Mambu.
        TODO: since pagination logic was added, is not always true that
        just 1 request was done. It may be more! But since request
        counter singleton holds true information about how many requests
        were done to Mambu, in fact this return value may be obsolete
        """
        from mambuuser import MambuUsers
        usrs = [ us for us in MambuUsers(branchId=self['id'], *args, **kwargs) if us['userState'] == "ACTIVE" ]
        self['users'] = usrs

        return 1


class MambuBranches(MambuStruct):
    """A list of Branches from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the branches according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several branches, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Branch object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuBranch just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuBranch, telling
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
            branch = MambuBranch(urlfunc=None, entid=None, *args, **kwargs)
            branch.init(b, *args, **kwargs)
            self.attrs[n] = branch
