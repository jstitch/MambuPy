# coding: utf-8
"""Mambu Clients objects.

MambuClient holds a client.

MambuClients holds a list of clients.

Uses mambuutil.getclienturl as default urlfunc

Example response from Mambu for clients (please omit comment lines beginning with #):
{
 "idDocuments": [
  {
   "encodedKey": "8a101aa637fd34cc0137ffda2df40067",
   "documentId": "VIMJ730305MMCLDR09",
   "documentType": "CURP",
   "clientKey": "8a101aa637fd34cc0137ffda2df10066",
   "issuingAuthority": "SEGOB",
   "indexInList": 0
  }
 ],

 "client": {
# Datos del cliente
 "id": "PIT087",
 "firstName": "MARIA DEL CARMEN",
 "middleName": "",
 "lastName": "VILLAFRANCA MADRIGAL",
 "state": "ACTIVE",
 "gender": "FEMALE",
 "birthDate": "1973-03-05T00:00:00+0000",
# Datos de acceso
 "homePhone": "58274975",
 "mobilePhone1": "5538785979",
# Otros
 "loanCycle": 0,
 "groupLoanCycle": 1,
 "clientLinesOfCredit": []
# Fechas
 "approvedDate": "2012-06-18T13:48:37+0000",
 "creationDate": "2012-06-18T13:48:37+0000",
 "lastModifiedDate": "2012-07-09T16:54:48+0000",
 "activationDate": "2012-06-18T14:08:32+0000",
# Relaciones
 "encodedKey": "8a101aa637fd34cc0137ffda2df10066",
 "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
 },

 "addresses": [
  {
   "line2": "LA COLMENA",
   "indexInList": 0,
   "parentKey": "8a101aa637fd34cc0137ffda2df10066",
   "encodedKey": "8a101aa637fd34cc0137ffda2df50068",
   "city": "NICOLAS ROMERO",
   "country": "MEXICO",
   "region": "MEXICO",
   "line1": "AV COLMENA S/N",
   "postcode": "54467"
  }
 ],

 "customInformation": [
  {
   "value": "testing1",
   "indexInList": 0,
   "parentKey": "8a101aa637fd34cc0137ffda2df10066",
   "encodedKey": "8af4b276385d069301386caa2f7209ed",
   "customField": {
    "amounts": {
     "testing2": "3",
     "testing1": "1"
    },
    "type": "CLIENT_INFO",
    "encodedKey": "8af4b276385d069301386ca9c0f609ec",
    "isDefault": false,
    "isRequired": false,
    "name": "Test",
    "dataType": "SELECTION",
    "indexInList": 1,
    "values": [
     "testing2",
     "testing1"
    ],
    "description": "pruebas"
   },
   "customFieldKey": "8af4b276385d069301386ca9c0f609ec",
   "amount": "1"
  }
 ],

 "groupKeys": [
  "8a5e35f730dd26e4013132ec04b12a66"
 ]
}

TODO: update this with later responses from Mambu, and perhaps certain
behaviours are obsolete here
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getclienturl, strip_consecutive_repeated_char as scrc


mod_urlfunc = getclienturl

class MambuClient(MambuStruct):
    """A Client from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    client you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customInformation', *args, **kwargs)


    def preprocess(self):
        """Preprocessing.

        Flattens the object. Important data comes on the 'client'
        dictionary inside of the response. Instead, every element of the
        'client' dictionary is taken out to the main attrs dictionary.

        Removes repeated chars from firstName, middleName and lastName
        fields. Adds a firstLastName and secondLastName fields for
        clients using more than one last name.

        Adds a 'name' field joining all names in to one string. IMHO
        Mambu does an awful job with names. Besides, this is useful on
        loan accounts. They get a 'holder' field added somewhere, which
        may be an individual client, or a group. So to get the holder
        name, you just access the 'holder'['name']. No matter if you
        have a client loan or a group loan, you get the name of the
        holder.

        Creates and 'address' field that holds the very first address on
        the addresses field, to ease the use of the
        perhaps-current-or-most-important address of the client.

        Creates a field for each documentId type with the value of the
        documentId, to ease the use of docuemnt IDs. That way if you
        have a document Id named 'CURP', then you access it directly via
        the 'CURP' field, instead of going all the way through the
        idDocuments field.
        """
        super(MambuClient,self).preprocess()

        try:
            for k,v in self['client'].items():
                self[k] = v
            del(self.attrs['client'])
        except Exception as e:
            pass

        try:
            self['firstName'] = scrc(self['firstName'], " ").strip()
        except Exception as e:
            self['firstName'] = ""
        try:
            self['middleName'] = scrc(self['middleName'], " ").strip()
        except Exception as ex:
            self['middleName'] = ""
        self['givenName']      = scrc(self["firstName"] + ((" " + self["middleName"]) if self["middleName"] != "" else ""), " ").strip()
        self['lastName']       = scrc(self['lastName'], " ").strip()
        self['firstLastName']  = " ".join(self['lastName'].split(" ")[:-1]) if len(self['lastName'].split(" ")) > 1 else self['lastName']
        self['secondLastName'] = " ".join(self['lastName'].split(" ")[-1:]) if len(self['lastName'].split(" ")) > 1 else ""

        self['name'] = scrc("%s %s" % (self['givenName'], self['lastName']), " ").strip()

        self['address'] = {}
        try:
            for name,item in self['addresses'][0].items():
                try:
                    self['addresses'][0][name] = item.strip()
                    self['address'][name] = item.strip()
                except AttributeError:
                    pass
        except (KeyError, IndexError):
            pass

        try:
            for idDoc in self['idDocuments']:
                self[idDoc['documentType']] = idDoc['documentId']
        except KeyError:
            pass


    def postprocess(self):
        """Postprocessing.

        Just in case some elements on the addresses was converted to
        anything but string, it gets converted back to only string
        (unicode). Things on addresses are not useful but by what they
        say, not what they are.
        TODO: do the same thing to the 'address' field created on
        preprocessing.
        """
        try:
            for name, item in self['addresses'][0].items():
                try:
                    if name == "indexInList": continue
                    self['addresses'][0][name] = unicode(self['addresses'][0][name])
                    self['address'][name] = unicode(self['address'][name])
                except AttributeError:
                    pass
        except (KeyError, IndexError):
            pass

        super(MambuClient,self).postprocess()

    def setGroups(self, *args, **kwargs):
        """Adds the groups to which this client belongs.

        The 'groupKeys' field of the client holds a list of the
        encodedKeys of the groups to which this client belongs.

        Returns the number of requests done to Mambu.
        """
        from mambugroup import MambuGroup

        requests = 0
        groups = []
        try:
            for gk in self['groupKeys']:
                g = MambuGroup(entid=gk, *args, **kwargs)
                requests += 1
                groups.append(g)
        except KeyError:
            pass

        self['groups'] = groups

        return requests

    def setBranch(self, *args, **kwargs):
        """Adds the branch to which the client belongs.
        """
        from mambubranch import MambuBranch

        branch = MambuBranch(entid=self['assignedBranchKey'], *args, **kwargs)
        self['assignedBranchName'] = branch['name']
        self['assignedBranch'] = branch

        return 1


class MambuClients(MambuStruct):
    """A list of Clients from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the clients according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several clients, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Client object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuClient just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuClient, telling
        MambuStruct not to connect() by default. It's desirable to
        connect at any other further moment to refresh some element in
        the list.
        """
        for n,c in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            client = MambuClient(urlfunc=None, entid=None, *args, **kwargs)
            client.init(c, *args, **kwargs)
            self.attrs[n] = client
