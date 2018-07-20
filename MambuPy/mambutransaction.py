# coding: utf-8
"""Mambu loan Transaction objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuTransaction
   MambuTransactions

MambuTransaction holds a loan transaction. Don't instantiate this class
directly. Look at MambuTransaction pydoc for further info.

MambuTransactions holds a list of loan transactions.

Uses mambuutil.gettransactionssurl as default urlfunc
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import gettransactionsurl


mod_urlfunc = gettransactionsurl

class MambuTransaction(MambuStruct):
    """A loan Transaction from Mambu.

    Don't instantiate this class directly. It's mostly used by
    MambuTransactions to configure each of its elements as
    MambuTransaction objects. There's no suitable urlfunc to use to
    retrieve just a specific transaction from a loan account. In fact,
    you can look at the code of MambuTransactions.convertDict2Attrs(),
    it uses urlfunc and entid = None , so no connection to Mambu will be
    made, never, for any particular MambuTransaction object.
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
            return self.__class__.__name__ + " - transactionid: %s" % self['transactionid']
        except KeyError:
            return self.__class__.__name__ + " - transactionid: %s" % self['transactionId']


class MambuTransactions(MambuStruct):
    """A list of loan Transactions from Mambu.

    You SHOULD give an entid at instantiation time: the id for the loan
    account which transactions you wish to retrieve.

    Makes no sense to send an empty entid, which throws a
    MambuError.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Transaction object for each one, initializing
        them one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuTransaction just
        created.

        You send a None urlfunc and entid to each MambuTransaction,
        because there's no method to retrieve individual transactions
        from Mambu.

.. todo:: use the transactionid as a possible entid here.
        """
        for n,t in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            trans = MambuTransaction(urlfunc=None, entid=None, *args, **kwargs)
            trans.init(t, *args, **kwargs)
            self.attrs[n] = trans
