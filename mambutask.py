# coding: utf-8
"""Mambu Task objects.

MambuTask holds a task. Look at MambuTask pydoc for further info.

Uses mambuutil.gettasksurl as default urlfunc

Example response from Mambu for tasks (please omit comment lines beginning with #):
[
   {
      "encodedKey":"8a33ae49441c4fe101441c71580403a5",
      "id":1,
      "creationDate":"2014-02-10T15:36:34+0000",
      "lastModifiedDate":"2014-02-10T15:36:34+0000",
      "dueDate":"2014-02-11T15:36:34+0000",
      "title":"Create a new client",
      "description":"Create a new client named John Smith with home phone (35)325-069 and address 123 Home Street",
      "createdByUserKey":"8a33ae49441c4fe101441c5fe42f0005",
      "status":"OPEN",
      "daysUntilDue":-7,
      "createdByFullName":"Max Power",
      "assignedUserKey":"8a33ae49441c4fe101441c5fe42f0005"
   }
]
"""
from mambustruct import MambuStruct
from mambuutil import gettasksurl


mod_urlfunc = gettasksurl

class MambuTask(MambuStruct):
    """A Task from Mambu.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __repr__(self):
        """Instead of the default id given by the parent class, shows
        the id, title, dueDate, status of the task.
        """
        try:
            return self.__class__.__name__ + " - taskid: '%s', '%s', %s, %s" % (self['task']['id'], self['task']['title'], self['task']['dueDate'], self['task']['status'])
        except KeyError:
            return self.__class__.__name__ + " - taskid: '%s'" % self['task']['id']
