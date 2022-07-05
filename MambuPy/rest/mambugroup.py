# coding: utf-8
"""Mambu Groups objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuGroup holds a group.

MambuGroups holds a list of groups.

Uses mambugeturl.getgroupurl as default urlfunc
"""


from ..mambugeturl import getgroupcustominformationurl, getgroupurl
from .mambustruct import MambuStruct, MambuStructIterator

# Other options include getgrouploansurl and getgroupcustominformationurl
mod_urlfunc = getgroupurl


class MambuGroup(MambuStruct):
    """A Group from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    group you wish to retrieve.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(
            self, urlfunc, entid, custom_field_name="customInformation", *args, **kwargs
        )

    def preprocess(self):
        """Preprocessing.

                Flattens the object. Important data comes on the 'theGroup'
                dictionary inside of the response. Instead, every element of the
                'theGroup' dictionary is taken out to the main attrs dictionary.

                Notes on the group get some html tags removed.

        .. todo:: use mambuutil.strip_tags() method

                A 'name' field is added, equivalent to the 'groupName' field.
                This is useful on loan accounts. They get a 'holder' field added
                somewhere, which may be an individual client, or a group. So to
                get the holder name, you just access the 'holder'['name']. No
                matter if you have a client loan or a group loan, you get the
                name of the holder.
        """
        super(MambuGroup, self).preprocess()

        try:
            for k, v in self["theGroup"].items():
                self[k] = v
            del self.attrs["theGroup"]
        except Exception:
            pass

        try:
            self["notes"] = self["notes"].replace("<div>", "").replace("</div>", "")
        except Exception:
            self["notes"] = ""

        try:
            self["name"] = self["groupName"]
        except KeyError:
            pass

        self["address"] = {}
        try:
            for name, item in self["addresses"][0].items():
                try:
                    self["addresses"][0][name] = item.strip()
                    self["address"][name] = item.strip()
                except AttributeError:
                    pass
        except (KeyError, IndexError):
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

        requests = 0
        if "fullDetails" in kwargs:
            fullDetails = kwargs["fullDetails"]
            kwargs.pop("fullDetails")
        else:
            fullDetails = True

        clients = []

        for m in self["groupMembers"]:
            try:
                self.mambuclientclass = kwargs.pop("mambuclientclass")
            except KeyError:
                try:
                    self.mambuclientclass
                except AttributeError:
                    from .mambuclient import MambuClient

                    self.mambuclientclass = MambuClient

            client = self.mambuclientclass(
                entid=m["clientKey"], fullDetails=fullDetails, *args, **kwargs
            )
            requests += 1
            clients.append(client)

        self["clients"] = clients

        return requests

    def setBranch(self, *args, **kwargs):
        """Adds the branch to which this groups belongs"""
        try:
            self.mambubranchclass
        except AttributeError:
            from .mambubranch import MambuBranch

            self.mambubranchclass = MambuBranch

        branch = self.mambubranchclass(entid=self["assignedBranchKey"], *args, **kwargs)
        self["branch"] = branch

        return 1

    def setCentre(self, *args, **kwargs):
        """Adds the centre to which this groups belongs"""
        try:
            self.mambucentreclass
        except AttributeError:
            from .mambucentre import MambuCentre

            self.mambucentreclass = MambuCentre

        centre = self.mambucentreclass(entid=self["assignedCentreKey"], *args, **kwargs)
        self["centre"] = centre

        return 1

    def setActivities(self, *args, **kwargs):
        """Adds the activities for this group to a 'activities' field.

        Activities are MambuActivity objects.

        Activities get sorted by activity timestamp.

        Returns the number of requests done to Mambu.
        """

        def activity_date(activity):
            """Util function used for sorting activities according to timestamp"""
            try:
                return activity["activity"]["timestamp"]
            except KeyError:
                return None

        try:
            self.mambuactivitiesclass
        except AttributeError:
            from .mambuactivity import MambuActivities

            self.mambuactivitiesclass = MambuActivities

        activities = self.mambuactivitiesclass(
            groupId=self["encodedKey"], *args, **kwargs
        )
        activities.attrs = sorted(activities.attrs, key=activity_date)
        self["activities"] = activities

        return 1

    def create(self, data, *args, **kwargs):
        """Creates a group in Mambu

        Parameters
        -data       dictionary with data to send
        """
        super(MambuGroup, self).create(data)
        if self.get("customInformation"):
            self["group"][self.custom_field_name] = self["customInformation"]
        if self.get("addresses"):
            self["group"]["addresses"] = self["addresses"]
        if self.get("groupMembers"):
            self["group"]["groupMembers"] = self["groupMembers"]
        self.init(attrs=self["group"])
        return 1

    def update(self, data, *args, **kwargs):
        """Updates a group in Mambu

        Uses PATCH and POST methods, for update "groupMembers", "groupRoles"
        and "group fields" PATCH method is used, for "customInformation" also
        Patch is used but url needs to be changed, in order to update
        "addresses" POST method is needed.

        https://support.mambu.com/docs/groups-api#post-group
        https://support.mambu.com/docs/groups-api#patch-group-information
        https://support.mambu.com/docs/groups-api#patch-group-custom-field-values

        Parameters
        -data       dictionary with data to update
        """
        cont_requests = 0
        data2update = {}
        # SET groupMembers
        if data.get("groupMembers"):
            data2update["groupMembers"] = data.get("groupMembers")
        # SET groupRoles
        if data.get("groupRoles"):
            data2update["groupRoles"] = data.get("groupRoles")

        # if there is data to update or data group to update, updates
        if data2update or data.get("group"):
            # SET group fields
            data2update["group"] = data.get("group", {})
            # UPDATE group fields
            cont_requests += self.update_patch(data2update, *args, **kwargs)

        # UPDATE customFields
        if data.get("customInformation"):
            data2update = {"group": {}}
            data2update["customInformation"] = data.get("customInformation")
            self._MambuStruct__urlfunc = getgroupcustominformationurl
            cont_requests += self.update_patch(data2update, *args, **kwargs)
            self._MambuStruct__urlfunc = getgroupurl

        # UPDATE addresses
        if data.get("addresses"):
            data2update = self._notUpdateData()
            data2update["addresses"] = data.get("addresses")
            cont_requests += self.update_post(data2update, *args, **kwargs)

        cont_requests += super(MambuGroup, self).update(data, *args, **kwargs)

        return cont_requests

    def update_patch(self, data, *args, **kwargs):
        """Updates a group Mambu using method PATCH

        Args:
            data (dictionary): dictionary with data to update

        https://support.mambu.com/docs/groups-api#patch-group-information
        """
        return super(MambuGroup, self).update_patch(data, *args, **kwargs)

    def update_post(self, data, *args, **kwargs):
        """Updates a group in Mambu using method POST

        Args:
            data (dictionary): dictionary with data to update

        https://support.mambu.com/docs/groups-api#post-group
        """
        return super(MambuGroup, self).update_post(data, *args, **kwargs)

    def _notUpdateData(self):
        """Data that would not be updated/overwritten in case of POST

        Dictionary with group data copied
        """
        notUpdateFields = [
            "id",
            "groupName",
            "mobilePhone1",
            "homePhone",
            "emailAddress",
            "preferredLanguage",
            "notes",
            "assignedUserKey",
            "assignedCentreKey",
            "assignedBranchKey",
        ]
        data = {"group": {}}
        data["group"] = {f: self.get(f) for f in notUpdateFields if self.get(f)}

        return data

    def addMembers(self, newMembers=[], *args, **kwargs):
        """Adds a list of members to the group

        Args:
            newMembers (list): list with encoded keys of the members to add to group
        """
        data2update = {}
        data2update["group"] = {}
        # get actual members
        groupMembers = [
            {"clientKey": i["clientKey"]} for i in self.get("groupMembers", [])
        ]
        data2update["groupMembers"] = groupMembers
        # add new members if not already exists in group
        newMembers = [
            {"clientKey": i}
            for i in newMembers
            if i not in [c["clientKey"] for c in groupMembers]
        ]
        data2update["groupMembers"].extend(newMembers)

        cont_requests = super(MambuGroup, self).update_patch(data2update)
        self.connect()
        cont_requests += 1
        return cont_requests


class MambuGroups(MambuStruct):
    """A list of Groups from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the groups according to any
    other filter you send to the urlfunc.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several groups, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

                You iterate over each element of the responded List from Mambu,
                and create a Mambu Group object for each one, initializing them
                one at a time, and changing the attrs attribute (which just
                holds a list of plain dictionaries) with a MambuGroup just
                created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
                  corresponding id to entid to each MambuGroup, telling
                  MambuStruct not to connect() by default. It's desirable to
                  connect at any other further moment to refresh some element in
                  the list.
        """
        for n, c in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mambugroupclass
            except AttributeError:
                self.mambugroupclass = MambuGroup

            group = self.mambugroupclass(urlfunc=None, entid=None, *args, **kwargs)
            group.init(c, *args, **kwargs)
            group._MambuStruct__urlfunc = getgroupurl
            self.attrs[n] = group
