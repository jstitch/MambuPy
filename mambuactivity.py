# coding: utf-8
"""Mambu Activity objects.

MambuActivity holds a mambu activity. Don't instantiate this class
directly. Look at MambuActivity pydoc for further info.

MambuActivities holds a list of activities.

Uses mambuutil.getactivitiesurl as default urlfunc

Example response from Mambu for activities (please omit comment lines beginning with #):
[
   {
      "activity":{
         "encodedKey":"8a54e5b444441eba014445e18c640021",
         "transactionID":1656,
         "timestamp":"2014-02-18T16:43:33+0000",
         "type":"TASK_DELETED",
         "branchKey":"8a33ae49441c4fe101441c713b36000e",
         "userKey":"8a33ae49441c4fe101441c5fe42f0005",
         "assignedUserKey":"8a33ae49441c4fe101441c5fe42f0005",
         "notes":"Disburse your first loan",
         "fieldChanges":[

         ]
      },
      "branchName":"Matola City",
      "userName":"Max Power"
   },
   {
      "activity":{
         "encodedKey":"8a54e5b444441eba0144477140920028",
         "transactionID":1657,
         "timestamp":"2014-02-19T00:00:08+0000",
         "type":"LOAN_ACCOUNT_SET_TO_IN_ARREARS",
         "clientKey":"8a33ae49441c4fe101441c7149e00102",
         "loanProductKey":"8a33ae494420ac160144210c0be50152",
         "loanAccountKey":"8a42711a4430587d0144307a352d0001",
         "notes":"",
         "fieldChanges":[

         ]
      },
      "clientName":"Kwemto Akobundu",
      "loanProductName":"dynamic dbei horizontal",
      "loanAccountName":"dynamic dbei horizontal"
   },
   {
      "activity":{
         "encodedKey":"8a54e5b44449337f014449337f130000",
         "transactionID":1661,
         "timestamp":"2014-02-19T08:11:54+0000",
         "type":"USER_LOGGED_IN",
         "branchKey":"8a33ae49441c4fe101441c713b36000e",
         "userKey":"8a33ae49441c4fe101441c5fe42f0005",
         "assignedUserKey":"8a33ae49441c4fe101441c5fe42f0005",
         "notes":"",
         "fieldChanges":[

         ]
      },
      "branchName":"Matola City",
      "userName":"Max Power"
   }
]

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

