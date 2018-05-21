# coding: utf-8
"""Mambu Roles objects.

MambuRole holds a user role.

MambuRoles holds a list of user roles.

Uses mambuutil.getrolesurl as default urlfunc

Example response from Mambu for roles:
[
   {
      "encodedKey":"8a099a615027d23a015036acc64e2e1a",
      "name":"Tech Support",
      "isAdministrator":true,
      "isTeller":false,
      "isCreditOfficer":false,
      "permissions":{
         "encodedKey":"8a099a615027d23a015036acc64e2e1b",
         "permissions":[
            "VIEW_LINE_OF_CREDIT_DETAILS"
         ],
         "canManageAllBranches":true,
         "canManageEntitiesAssignedToOtherOfficers":true
      },
      "accessRights":[
         "MAMBU"
      ],
      "creationDate":"2015-10-05T06:25:04+0000",
      "lastModifiedDate":"2015-10-05T06:27:01+0000"
   },
   {
      "encodedKey":"8a17d58a511a685601511aff82e60130",
      "name":"Back-Office 1",
      "isAdministrator":false,
      "isTeller":false,
      "isCreditOfficer":true,
      "permissions":{
         "encodedKey":"8a17d58a511a685601511aff82e70131",
         "permissions":[
            "VIEW_INTELLIGENCE"
         ],
         "canManageAllBranches":true,
         "canManageEntitiesAssignedToOtherOfficers":true
      },
      "accessRights":[

      ],
      "creationDate":"2015-11-18T14:28:52+0000",
      "lastModifiedDate":"2015-11-18T14:28:52+0000"
   },
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getrolesurl


mod_urlfunc = getrolesurl

class MambuRole(MambuStruct):
    """A Role from Mambu.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        """Instead of the default id given by the parent class, shows
        the rolename
        """
        return self.__class__.__name__ + " - rolename: '%s'" % self['name']


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
    the logic of the constructor and the convertDict2Attrs method in
    the iterable class to use some sort of itemclass there too.
    Don't forget to submit the change on a pull request when done
    ;-)
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', itemclass=MambuRole, *args, **kwargs):
        """entid argument is empty. That makes perfect
        sense: you always get serveral roles from Mambu REST API
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Role (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        MambuUser (or your own itemclass) just created.
        """
        for n,u in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            role = self.itemclass(urlfunc=None, entid=None, *args, **kwargs)
            role.init(u, *args, **kwargs)
            self.attrs[n] = role
