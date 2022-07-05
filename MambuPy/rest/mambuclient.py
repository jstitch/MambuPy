# coding: utf-8
"""Mambu Clients objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuClient holds a client.

MambuClients holds a list of clients.

Uses mambugeturl.getclienturl as default urlfunc
"""


from builtins import str as unicode

from ..mambugeturl import getclientcustominformationurl, getclienturl
from ..mambuutil import strip_consecutive_repeated_char as scrc
from .mambustruct import MambuStruct, MambuStructIterator

mod_urlfunc = getclienturl


class MambuClient(MambuStruct):
    """A Client from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    client you wish to retrieve.
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
        super(MambuClient, self).preprocess()

        try:
            for k, v in self["client"].items():
                self[k] = v
            del self.attrs["client"]
        except Exception:
            pass

        try:
            self["firstName"] = scrc(self["firstName"], " ").strip()
        except Exception:
            self["firstName"] = ""
        try:
            self["middleName"] = scrc(self["middleName"], " ").strip()
        except Exception:
            self["middleName"] = ""
        self["givenName"] = scrc(
            self["firstName"]
            + ((" " + self["middleName"]) if self["middleName"] != "" else ""),
            " ",
        ).strip()
        self["lastName"] = scrc(self["lastName"], " ").strip()
        self["firstLastName"] = (
            " ".join(self["lastName"].split(" ")[:-1])
            if len(self["lastName"].split(" ")) > 1
            else self["lastName"]
        )
        self["secondLastName"] = (
            " ".join(self["lastName"].split(" ")[-1:])
            if len(self["lastName"].split(" ")) > 1
            else ""
        )

        self["name"] = scrc("%s %s" % (self["givenName"], self["lastName"]), " ").strip()

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

        try:
            for idDoc in self["idDocuments"]:
                self[idDoc["documentType"]] = idDoc["documentId"]
        except KeyError:
            pass

    def postprocess(self):
        """Postprocessing.

                Just in case some elements on the addresses was converted to
                anything but string, it gets converted back to only string
                (unicode). Things on addresses are not useful but by what they
                say, not what they are.

        .. todo:: do the same thing to the 'address' field created on
                  preprocessing.
        """
        try:
            for name, item in self["addresses"][0].items():
                try:
                    if name == "indexInList":
                        continue
                    self["addresses"][0][name] = unicode(self["addresses"][0][name])
                    self["address"][name] = unicode(self["address"][name])
                except AttributeError:
                    pass
        except (KeyError, IndexError):
            pass

        super(MambuClient, self).postprocess()

    def setGroups(self, *args, **kwargs):
        """Adds the groups to which this client belongs.

        The 'groupKeys' field of the client holds a list of the
        encodedKeys of the groups to which this client belongs.

        Returns the number of requests done to Mambu.
        """

        requests = 0
        groups = []
        try:
            for gk in self["groupKeys"]:
                try:
                    self.mambugroupclass
                except AttributeError:
                    from .mambugroup import MambuGroup

                    self.mambugroupclass = MambuGroup

                g = self.mambugroupclass(entid=gk, *args, **kwargs)
                requests += 1
                groups.append(g)
        except KeyError:
            pass

        self["groups"] = groups

        return requests

    def setBranch(self, *args, **kwargs):
        """Adds the branch to which the client belongs."""

        try:
            self.mambubranchclass
        except AttributeError:
            from .mambubranch import MambuBranch

            self.mambubranchclass = MambuBranch

        branch = self.mambubranchclass(entid=self["assignedBranchKey"], *args, **kwargs)
        self["assignedBranchName"] = branch["name"]
        self["assignedBranch"] = branch

        return 1

    def create(self, data, *args, **kwargs):
        """Create a client in Mambu

        Parameters
        -data       dictionary with data to send

        """
        return super(MambuClient, self).create(data)

    def update(self, data, *args, **kwargs):
        """Updates a client in Mambu

        Uses PATCH and POST methods, for update "customInformation" and
        "client fields" PATCH method is used, for "customInformation" also
        Patch is used but url needs to be changed, in order to update
        "addresses" or "idDocuments" POST method is needed.

        https://support.mambu.com/docs/clients-api#post-clients
        https://support.mambu.com/docs/clients-api#patch-client
        https://support.mambu.com/docs/clients-api#patch-client-custom-field-values

        Parameters
        -data       dictionary with data to update
        """
        cont_requests = 0
        data2update = {}
        # UPDATE client fields
        if data.get("client"):
            data2update["client"] = data.get("client", {})
            cont_requests += self.update_patch(data2update, *args, **kwargs)

        # UPDATE customFields
        if data.get("customInformation"):
            data2update = {"client": {}}
            data2update["customInformation"] = data.get("customInformation")
            self._MambuStruct__urlfunc = getclientcustominformationurl
            cont_requests += self.update_patch(data2update, *args, **kwargs)
            self._MambuStruct__urlfunc = getclienturl

        # UPDATE addresses or idDocuments
        if data.get("addresses") or data.get("idDocuments"):
            data2update = {}
            # UPDATE addresses
            if data.get("addresses"):
                data2update["addresses"] = data.get("addresses")
            # UPDATE idDocuments
            if data.get("idDocuments"):
                data2update["idDocuments"] = data.get("idDocuments")
            cont_requests += self.update_post(data2update, *args, **kwargs)

        cont_requests += super(MambuClient, self).update(data, *args, **kwargs)

        return cont_requests

    def update_patch(self, data, *args, **kwargs):
        """Updates a client Mambu using method PATCH

        Args:
            data (dictionary): dictionary with data to update

        https://support.mambu.com/docs/clients-api#patch-client
        """
        return super(MambuClient, self).update_patch(data, *args, **kwargs)

    def update_post(self, data, *args, **kwargs):
        """Updates a client in Mambu using method POST

        Args:
            data (dictionary): dictionary with data to update

        https://support.mambu.com/docs/clients-api#post-clients
        """
        return super(MambuClient, self).update_post(data, *args, **kwargs)


class MambuClients(MambuStruct):
    """A list of Clients from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the clients according to any
    other filter you send to the urlfunc.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several clients, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

                You iterate over each element of the responded List from Mambu,
                and create a Mambu Client object for each one, initializing them
                one at a time, and changing the attrs attribute (which just
                holds a list of plain dictionaries) with a MambuClient just
                created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
                  corresponding id to entid to each MambuClient, telling
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
                self.mambuclientclass
            except AttributeError:
                self.mambuclientclass = MambuClient

            client = self.mambuclientclass(urlfunc=None, entid=None, *args, **kwargs)
            client.init(c, *args, **kwargs)
            client._MambuStruct__urlfunc = getclienturl
            self.attrs[n] = client
