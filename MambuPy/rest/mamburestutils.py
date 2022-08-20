from future.utils import implements_iterator

from ..mambuutil import MambuError


class RequestsCounter(object):
    """Singleton that counts requests.

    If you want to control the number of requests you do to Mambu, you
    may find this counter useful. Since it is a Singleton, every Mambu
    object shares it and increases the amount of requests counted here,
    so you may read it on every Mambu object you have per Python
    session you hold.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(RequestsCounter, cls).__new__(cls, *args, **kwargs)
            cls.requests = []
            cls.cnt = 0
        return cls.__instance

    def add(cls, temp):
        cls.requests.append(temp)
        cls.cnt += 1

    def reset(cls):
        cls.cnt = 0
        cls.requests = []


@implements_iterator
class MambuStructIterator:
    """Enables iteration for some Mambu objects that may want to have iterators.

    Loans, Transactions, Repayments, Clients, Groups, Users, Branches
    are some of the Mambu entitites that may be iterable. Here at
    MambuPy, all of them have an iterator class for requesting several
    entitites to Mambu, instead of just one of them. Please refer to
    each MambuObject pydoc for more info.
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.offset = 0

    def __next__(self):
        if self.offset >= len(self.wrapped):
            raise StopIteration
        else:
            item = self.wrapped[self.offset]
            self.offset += 1
            return item

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self


def set_custom_field(mambuentity, customfield="", *args, **kwargs):
    """Modifies the customField field for the given object with
    something related to the value of the given field.

    If the dataType == "USER_LINK" then instead of using the value
    of the CF, it will be a MambuUser object.

    Same if dataType == "CLIENT_LINK", but with a MambuClient.

    Default case: just uses the same value the CF already had.

    Returns the number of requests done to Mambu.
    """
    from . import mambuclient, mambuuser

    try:
        customFieldValue = mambuentity[customfield]
        # find the dataType customfield by name or id
        datatype = [
            l["customField"]["dataType"]
            for l in mambuentity[mambuentity.custom_field_name]
            if (l["name"] == customfield or l["id"] == customfield)
        ][0]
    except IndexError:
        # if no customfield found with the given name, assume it is a grouped
        # custom field, name must have an index suffix that must be removed
        try:
            # find the dataType customfield by name or id
            datatype = [
                l["customField"]["dataType"]
                for l in mambuentity[mambuentity.custom_field_name]
                if (
                    l["name"] == customfield.split("_")[0] or
                    l["id"] == customfield.split("_")[0]
                )
            ][0]
        except IndexError:
            err = MambuError(
                "Object %s has no custom field '%s'" % (mambuentity["id"], customfield)
            )
            raise err
    except AttributeError:
        err = MambuError("Object does not have a custom field to set")
        raise err

    if datatype == "USER_LINK":
        mambuentity[customfield] = mambuuser.MambuUser(
            entid=customFieldValue, *args, **kwargs
        )
    elif datatype == "CLIENT_LINK":
        mambuentity[customfield] = mambuclient.MambuClient(
            entid=customFieldValue, *args, **kwargs
        )
    else:
        mambuentity[customfield] = customFieldValue
        return 0
    return 1
