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
from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import gettasksurl


mod_urlfunc = gettasksurl

class MambuTask(MambuStruct):
    """A Task from Mambu.

    Don't instantiate this class directly. It's mostly used by
    MambuTasks to configure each of its elements as MambuTask
    objects. There's no suitable urlfunc to use to retrieve just a
    specific transaction from a loan account. In fact, you can look at
    the code of MambuTasks.convertDict2Attrs(), it uses urlfunc
    and entid = None , so no connection to Mambu will be made, never,
    for any particular MambuTask object.
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
            return self.__class__.__name__ + " - taskid: '%s', %s, %s" % (self['task']['id'], self['task']['dueDate'], self['task']['status'])
        except KeyError:
            try:
                return self.__class__.__name__ + " - taskid: '%s'" % self['task']['id']
            except KeyError:
                try:
                    return self.__class__.__name__ + " - taskid: '%s', %s, %s" % (self['id'], self['dueDate'], self['status'])
                except KeyError:
                    return self.__class__.__name__ + " - taskid: '%s'" % self['id']


class MambuTasks(MambuStruct):
    """A list of Tasks from Mambu.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Task object for each one, initializing
        them one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuTask just
        created.

        """
        for n,a in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            task = MambuTask(urlfunc=None, entid=None, *args, **kwargs)
            task.init(a, *args, **kwargs)
            self.attrs[n] = task
