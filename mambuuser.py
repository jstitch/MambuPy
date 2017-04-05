# coding: utf-8
"""Mambu Users objects.

MambuUser holds a user.

MambuUsers holds a list of users.

Uses mambuutil.getuserurl as default urlfunc

Example response from Mambu for users:
{
  "id": 51,
  "username": "i.martinez",
  "email": "i.martinez@podemos.mx",
  "userState": "ACTIVE",

  "firstName": "Ilya ",
  "lastName": "Martinez",
  "title": "Coordinador de Emprendedoras",
  "homePhone": "58288424",
  "mobilePhone1": "(044)5559951342",
  "notes": ""

  "language": "SPANISH",
  "twoFactorAuthentication": false,
  "isAdministrator": false,
  "isCreditOfficer": true,
  "accessRights": [
    "MAMBU",
    "MOBILE"
  ],

  "lastLoggedInDate": "2012-12-19T20:31:07+0000",

  "creationDate": "2011-08-25T19:23:54+0000",
  "lastModifiedDate": "2012-12-19T20:31:07+0000",

  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
  "encodedKey": "8ad807b031f6305b01320266094b4948",

}

TODO: update this with later responses from Mambu, and perhaps certain
behaviours are obsolete here
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getuserurl


mod_urlfunc = getuserurl

class MambuUser(MambuStruct):
    """A User from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    user you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customFields', *args, **kwargs)


    def preprocess(self):
        """Preprocessing.

        Removes repeated chars from firstName and lastName fields.

        Adds a 'name' field joining all names in to one string.
        """
        super(MambuUser,self).preprocess()

        try:
            self['firstName'] = self['firstName'].strip()
        except Exception as e:
            self['firstName'] = ""
        try:
            self['lastName'] = self['lastName'].strip()
        except Exception as ex:
            self['lastName'] = ""

        self['name'] = self['firstName'] + " " + self['lastName']


    def setGroups(self, *args, **kwargs):
        """Adds the groups assigned to this user to a 'groups' field.

        Returns the number of requests done to Mambu.
        """
        from mambugroup import MambuGroups

        groups = MambuGroups(creditOfficerUsername=self['username'], *args, **kwargs)
        self['groups'] = groups

        return 1


class MambuUsers(MambuStruct):
    """A list of Users from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the users according to any other
    filter you send to the urlfunc.

    itemclass argument allows you to pass some other class as the
    elements for the list. Why is this useful? You may wish to override
    several behaviours by creating your own MambuUser son class. Pass
    that to the itemclass argument here and voila, you get a list of
    YourMambuUser class using MambuUsers instead of plain old MambuUser
    elements.

    If you wish to specialize other Mambu objects on MambuPy you may
    do that. Mind that if you desire that the iterable version of it
    to have elements of your specialized class, you need to change
    the logic of the constructor and the convertDict2Attrs method in
    the iterable class to use some sort of itemclass there too.
    Don't forget to submit the change on a pull request when done
    ;-)
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', itemclass=MambuUser, *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several branches, not just one
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu User (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        MambuUser (or your own itemclass) just created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each itemclass, telling MambuStruct
        not to connect() by default. It's desirable to connect at any
        other further moment to refresh some element in the list.
        """
        for n,u in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            user = self.itemclass(urlfunc=None, entid=None, *args, **kwargs)
            user.init(u, *args, **kwargs)
            self.attrs[n] = user
