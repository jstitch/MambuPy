# coding: utf-8
"""Mambu Centres objects.

MambuCentre holds a centre.

MambuCentres holds a list of centres.

Uses mambuutil.getcentresurl as default urlfunc

Example response from Mambu for centres:
{
   "encodedKey":"8a33ae49441c4fe101441c713b3a0010",
   "id":"MP1",
   "creationDate":"2014-02-10T15:36:26+0000",
   "lastModifiedDate":"2014-02-17T12:45:59+0000",
   "name":"Market Place",
   "notes":"All clients and officers gather in the market to discuss loans and savings situation.",
   "meetingDay":"MONDAY",
   "assignedBranchKey":"8a33ae49441c4fe101441c713b36000e",
   "address":{
      "encodedKey":"8a33ae49441c4fe101441c713c310012",
      "parentKey":"8a33ae49441c4fe101441c713b3a0010",
      "line1":"Hegyalja út 95.",
      "line2":"Stress address 2124",
      "city":"Debrecen",
      "region":"",
      "postcode":"4032",
      "country":"",
      "indexInList":-1
   },
   "customFieldValues":[
      {
         "encodedKey":"8a42711a4425d77d014425e4505d0082",
         "parentKey":"8a33ae49441c4fe101441c713b3a0010",
         "customFieldKey":"8a33ae494420ac160144254049a00bf5",
         "customField":{
            "encodedKey":"8a33ae494420ac160144254049a00bf5",
            "id":"centre_test_Centres",
            "name":"centre test",
            "type":"CENTRE_INFO",
            "dataType":"STRING",
            "valueLength":"SHORT",
            "isDefault":false,
            "isRequired":false,
            "description":"",
            "customFieldSet":{
               "encodedKey":"8a33ae494420ac1601442540165e0bf4",
               "name":"Centre",
               "notes":"",
               "createdDate":"2014-02-12T08:39:20+0000",
               "indexInList":0,
               "type":"CENTRE_INFO"
            },
            "indexInList":0,
            "state":"NORMAL"
         },
         "value":"sa",
         "indexInList":-1
      }
   ]
}
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getcentresurl


mod_urlfunc = getcentresurl

class MambuCentre(MambuStruct):
    """A Centre from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    centre you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customFieldValues', *args, **kwargs)


class MambuCentres(MambuStruct):
    """A list of Centres from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the centres according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several centres, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Centre object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuCentre just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuCentre, telling
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
            centre = MambuCentre(urlfunc=None, entid=None, *args, **kwargs)
            centre.init(b, *args, **kwargs)
            self.attrs[n] = centre
