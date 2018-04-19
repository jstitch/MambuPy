# coding: utf-8
"""Mambu Groups objects.

MambuGroup holds a group.

MambuGroups holds a list of groups.

Uses mambuutil.getgroupurl as default urlfunc

Example response from Mambu for groups:
{
 "groupMembers": [
  {
   "encodedKey": "8af4b2763852bc0201385421e2af0229",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "indexInList": 0,
   "creationDate": "2012-07-04T22:35:03+0000",
   "clientKey": "8a101aa637fd34cc013816274ec902d9"
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b1022a",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "indexInList": 1,
   "creationDate": "2012-07-04T22:35:03+0000",
   "clientKey": "8a43a79f3664edaa013733547d156af5"
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b1022b",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "indexInList": 2,
   "creationDate": "2012-07-04T22:35:03+0000",
   "clientKey": "8a101aa637fd34cc0137ffdc3692006b"
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b1022c",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "indexInList": 3,
   "creationDate": "2012-07-04T22:35:03+0000",
   "clientKey": "8a5c291d33563d0501335ad699960783"
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b1022d",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "indexInList": 4,
   "creationDate": "2012-07-04T22:35:03+0000",
   "clientKey": "8ad807b0316f84eb013191735a041b2b"
  }
 ],
 "theGroup": {
  "notes": "Las notas del grupo<br><br>son<br><br>estas<br>....<br>",
  "id": "VQ611",
  "groupLinesOfCredit": [],
  "encodedKey": "8af4b2763852bc0201385421e2a70226",
  "loanCycle": 0,
  "creationDate": "2012-07-04T22:35:03+0000",
  "lastModifiedDate": "2012-07-04T22:35:03+0000",
  "groupName": "TestGroup",
  "assignedUserKey": "8a5c1e9f34bdd2b90134c49b6b950948",
  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d"
 },
 "addresses": [
  {
   "line2": "Entre SnLuisPotosi y LopezMateos",
   "indexInList": 0,
   "parentKey": "8af4b2763852bc0201385421e2a70226",
   "encodedKey": "8af4b2763852bc0201385421e2a90227",
   "city": "Atizapan",
   "country": "Mexico",
   "region": "Mexico",
   "line1": "Pedro Velasquez",
   "postcode": "12345"
  }
 ],
 "groupRoles": [
  {
   "encodedKey": "8af4b2763852bc0201385421e2b2022e",
   "roleName": "President",
   "groupRoleNameKey": "8a70db342e6d595a012e6d8391eb04be",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "clientKey": "8a101aa637fd34cc013816274ec902d9",
   "indexInList": 0
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b5022f",
   "roleName": "Secretary",
   "groupRoleNameKey": "8a70db342e6d595a012e6d83925d04bf",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "clientKey": "8a43a79f3664edaa013733547d156af5",
   "indexInList": 1
  },
  {
   "encodedKey": "8af4b2763852bc0201385421e2b50230",
   "roleName": "Treasurer",
   "groupRoleNameKey": "8a70db342e6d595a012e6d83926504c0",
   "groupKey": "8af4b2763852bc0201385421e2a70226",
   "clientKey": "8a101aa637fd34cc0137ffdc3692006b",
   "indexInList": 2
  }
 ],
 "customInformation": [
  {
   "value": "ValorCustom",
   "indexInList": 0,
   "parentKey": "8af4b2763852bc0201385421e2a70226",
   "encodedKey": "8af4b2763852bc0201385421e2aa0228",
   "customField": {
    "type": "GROUP_INFO",
    "encodedKey": "8afae1dc2ecf2844012ee4a468f62773",
    "isDefault": false,
    "isRequired": false,
    "name": "Referencia",
    "dataType": "STRING",
    "indexInList": -1
   },
   "customFieldKey": "8afae1dc2ecf2844012ee4a468f62773"
  }
 ]
}

TODO: update this with later responses from Mambu, and perhaps certain
behaviours are obsolete here
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getgroupurl

# Other options include getgrouploansurl and getgroupcustominformationurl
mod_urlfunc = getgroupurl

class MambuGroup(MambuStruct):
    """A Group from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    group you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customInformation', *args, **kwargs)


    def preprocess(self):
        """Preprocessing.

        Flattens the object. Important data comes on the 'theGroup'
        dictionary inside of the response. Instead, every element of the
        'theGroup' dictionary is taken out to the main attrs dictionary.

        Notes on the group get some html tags removed.
        TODO: use mambuutil.strip_tags() method

        A 'name' field is added, equivalent to the 'groupName' field.
        This is useful on loan accounts. They get a 'holder' field added
        somewhere, which may be an individual client, or a group. So to
        get the holder name, you just access the 'holder'['name']. No
        matter if you have a client loan or a group loan, you get the
        name of the holder.
        """
        super(MambuGroup,self).preprocess()

        try:
            for k,v in self['theGroup'].items():
                self[k] = v
            del(self.attrs['theGroup'])
        except Exception as e:
            pass

        try:
            self['notes'] = self['notes'].replace("<div>", "").replace("</div>", "")
        except Exception as e:
            self['notes'] = ""

        try:
            self['name'] = self['groupName']
        except KeyError:
            pass


    def setClients(self, *args, **kwargs):
        """Adds the clients for this group to a 'clients' field.

        The 'groupMembers' field of the group holds the encodedKeys of
        the member clients of the group. Since Mambu REST API accepts
        both ids or encodedKeys to retrieve entities, we use that here.

        You may wish to get the full details of each client by passing a
        fullDetails=True argument here.

        Returns the number of requests done to Mambu.
        """
        from mambuclient import MambuClient

        requests = 0
        if kwargs.has_key('fullDetails'):
            fullDetails = kwargs['fullDetails']
            kwargs.pop('fullDetails')
        else:
            fullDetails = True

        clients = []
        for m in self['groupMembers']:
            client = MambuClient(entid=m['clientKey'],
                                 fullDetails=fullDetails, *args, **kwargs)
            requests += 1
            clients.append(client)

        self['clients'] = clients

        return requests

    def setBranch(self, *args, **kwargs):
        """Adds the branch to which this groups belongs
        """
        from mambubranch import MambuBranch

        branch = MambuBranch(entid=self['assignedBranchKey'], *args, **kwargs)
        self['branch'] = branch

        return 1

    def setCentre(self, *args, **kwargs):
        """Adds the centre to which this groups belongs
        """
        from mambucentre import  MambuCentre

        centre = MambuCentre(entid=self['assignedCentreKey'], *args, **kwargs)
        self['centre'] = centre

        return 1

    def setActivities(self, *args, **kwargs):
        """Adds the activities for this group to a 'activities' field.

        Activities are MambuActivity objects.

        Activities get sorted by activity timestamp.

        Returns the number of requests done to Mambu.
        """
        def activityDate(activity):
            """Util function used for sorting activities according to timestamp"""
            try:
                return activity['activity']['timestamp']
            except KeyError as kerr:
                return None
        from mambuactivity import MambuActivities

        activities = MambuActivities(groupId=self['encodedKey'], *args, **kwargs)
        activities.attrs = sorted(activities.attrs, key=activityDate)
        self['activities'] = activities

        return 1



class MambuGroups(MambuStruct):
    """A list of Groups from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the groups according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several groups, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Group object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuGroup just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuGroup, telling
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
            group = MambuGroup(urlfunc=None, entid=None, *args, **kwargs)
            group.init(c, *args, **kwargs)
            self.attrs[n] = group
