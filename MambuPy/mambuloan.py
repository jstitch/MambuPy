# coding: utf-8
"""Mambu Loans objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuLoan
   MambuLoans

MambuLoan holds a loan account.

MambuLoans holds a list of loan accounts.

Uses mambuutil.getloans as default urlfunc.
You can override this and use mambuutil.getgrouploansurl for the loans
of a specific group instead (you should send the Group ID instead of the
Loan ID as the entid argument in the constructor in that case).
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getloansurl, MambuError, strip_tags


mod_urlfunc = getloansurl

# Objeto con una Cuenta desde Mambu
class MambuLoan(MambuStruct):
    """A Loan account from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    loan account you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, customFieldName='customFieldValues', *args, **kwargs)


    def getDebt(self):
        """Sums up all the balances of the account and returns them.
        """
        debt = float(self['principalBalance']) + float(self['interestBalance'])
        debt += float(self['feesBalance']) + float(self['penaltyBalance'])

        return debt


    def preprocess(self):
        """Preprocessing.

        Each active custom field is given a 'name' key that holds the field
        name, and for each keyed name, the value of the custom field is
        assigned.

        Notes on the group get some html tags removed.
        """
        super(MambuLoan,self).preprocess()

        try:
            self['notes'] = strip_tags(self['notes'])
        except KeyError:
            pass


    def setRepayments(self, *args, **kwargs):
        """Adds the repayments for this loan to a 'repayments' field.

        Repayments are MambuRepayment objects.

        Repayments get sorted by due date.

        Returns the number of requests done to Mambu.

.. todo:: since pagination logic was added, is not always true that
          just 1 request was done. It may be more! But since request
          counter singleton holds true information about how many requests
          were done to Mambu, in fact this return value may be obsolete
        """
        def duedate(repayment):
            """Util function used for sorting repayments according to due Date"""
            try:
                return repayment['dueDate']
            except KeyError as kerr:
                return datetime.now()
        from mamburepayment import MambuRepayments

        reps = MambuRepayments(entid=self['id'], *args, **kwargs)
        reps.attrs = sorted(reps.attrs, key=duedate)
        self['repayments'] = reps

        return 1


    def setTransactions(self, *args, **kwargs):
        """Adds the transactions for this loan to a 'transactions' field.

        Transactions are MambuTransaction objects.

        Transactions get sorted by transaction id.

        Returns the number of requests done to Mambu.

.. todo:: since pagination logic was added, is not always true that
          just 1 request was done. It may be more! But since request
          counter singleton holds true information about how many requests
          were done to Mambu, in fact this return value may be obsolete
        """
        def transactionid(transaction):
            """Util function used for sorting transactions according to id"""
            try:
                return transaction['transactionId']
            except KeyError as kerr:
                return None
        from mambutransaction import MambuTransactions

        trans = MambuTransactions(entid=self['id'], *args, **kwargs)
        trans.attrs = sorted(trans.attrs, key=transactionid)
        self['transactions'] = trans

        return 1


    def setBranch(self, *args, **kwargs):
        """Adds the branch for this loan to a 'assignedBranch' field.

        Also adds an 'assignedBranchName' field with the name of the branch.

        Branch is a MambuBranch object.

        Returns the number of requests done to Mambu.
        """
        from mambubranch import MambuBranch

        branch = MambuBranch(entid=self['assignedBranchKey'], *args, **kwargs)
        self['assignedBranchName'] = branch['name']
        self['assignedBranch'] = branch

        return 1


    def setCentre(self, *args, **kwargs):
        """Adds the centre for this loan to a 'assignedCentre' field.

        Also adds an 'assignedCentreName' field with the name of the centre.

        Centre is a MambuCentre object.

        Returns the number of requests done to Mambu.
        """
        from mambucentre import MambuCentre

        centre = MambuCentre(entid=self['assignedCentreKey'], *args, **kwargs)
        self['assignedCentreName'] = centre['name']
        self['assignedCentre'] = centre

        return 1


    def setUser(self, *args, **kwargs):
        """Adds the user for this loan to a 'user' field.

        User is a MambuUser object.

        Returns the number of requests done to Mambu.
        """
        from mambuuser import MambuUser

        try:
            user = MambuUser(entid=self['assignedUserKey'], *args, **kwargs)
        except KeyError as kerr:
            err = MambuError("La cuenta %s no tiene asignado un usuario" % self['id'])
            err.noUser = True
            raise err

        self['user'] = user

        return 1


    def setProduct(self, cache=False, *args, **kwargs):
        """Adds the product for this loan to a 'product' field.

        Product is a MambuProduct object.

        cache argument allows to use AllMambuProducts singleton to
        retrieve the products. See mambuproduct.AllMambuProducts code
        and pydoc for further information.

        Returns the number of requests done to Mambu.
        """
        if cache:
            from mambuproduct import AllMambuProducts
            prods = AllMambuProducts(*args, **kwargs)
            for prod in prods:
                if prod['encodedKey'] == self['productTypeKey']:
                    self['product'] = prod
            try:
                # asked for cache, but cache was originally empty
                prods.noinit
            except AttributeError:
                return 1
            return 0

        from mambuproduct import MambuProduct

        product = MambuProduct(entid=self['productTypeKey'], *args, **kwargs)
        self['product'] = product

        return 1


    def setHolder(self, getClients=False, getRoles=False, *args, **kwargs):
        """Adds the "holder" of the loan to a 'holder' field.

        Holder may be a MambuClient or a MambuGroup object, depending on
        the type of loan created at Mambu.

        getRoles argument tells this method to retrive the clients who
        have specific roles in the group, in case of a group holder.

        getClients argument tells this method to retrieve the client
        members of the group, in case of a group holder. See the
        definition of the 'clients' field added with this argument
        below.

        fullDetails argument works for Client Holder and for the client
        members of the group. But the Group is always retrieved with
        full details.

        When using getRoles argument also adds a 'roles' field to the
        holder, a dictionary with keys:

        * 'role' , the rolename

        * 'client', a MambuClient having that role on the group

.. todo:: since the roles field is added to the holder, and it only
          applies to Groups, perhaps the getRoles functionality should be
          on MambuGroup code

        When using getClients argument, also adds a 'clients' field to
        the loan. By the way it works, when holder is a Group, it calls
        the setClients method, which adds a 'clients' field to the
        MambuGroup.

        The 'clients' field on the loan is a dictionary with the full
        name of each client receiving from this loan account as a key
        (see the 'name' field on MambuClient and MambuGroup). Each key
        holds another dictionary with the following keys:

        * 'client' holds a MambuClient. So even if a group is the holder
          of the account, you can access each individual client object
          here.

        * 'loan' holds a reference to this loan account (self)

        * 'amount' defaults to the total loan amount ('loanAmount'
          field) (see the pydoc for getClientDetails method)

        * 'montoPago' defaults to the total loan amount divided by the
          number of repayment installments of the loan account (the
          'repaymentInstallments' field), that is, how much to pay for
          each repayment installment (see the pydoc for getClientDetails
          method)

.. todo:: change the name to an english name

        * 'porcentaje' defaults to a 100%, the total loan amount divided
          by itself, that is, hoy much in percentage of the debt belongs
          to this client (see the pydoc for getClientDetails method)

.. todo:: change the name to an english name

        This three fields are supposed to reflect individual numbers for
        each client, but Mambu does an awful job indicating this on
        group loan accounts. So you should indicate how much you
        assigned to each client in other ways. Using the notes of the
        loan account perhaps (with a predefined format you parse on the
        preprocessing of MambuLoan)? with custom fields? Your call that
        you may define making your own loan account class inheriting
        from MambuLoan class. See the pydoc for getClientDetails method
        below, it specifies the way to determine the amount for each
        client depending on your use of Mambu, and additionally any
        other fields you wish to add to the 'clients' field on the loan
        account.

        Returns the number of requests done to Mambu.

.. todo:: what to do on Hybrid loan accounts?
        """
        requests = 0
        if kwargs.has_key('fullDetails'):
            fullDetails = kwargs['fullDetails']
            kwargs.pop('fullDetails')
        else:
            fullDetails = True

        if self['accountHolderType'] == "GROUP":
            from mambugroup import MambuGroup

            self['holderType'] = "Grupo"
            holder = MambuGroup(entid=self['accountHolderKey'], fullDetails=True, *args, **kwargs)
            self['holder'] = holder
            requests += 1

            if getRoles:
                from mambuclient import MambuClient

                roles = []
                # If holder is group, attach role client data to the group
                for c in holder['groupRoles']:
                    roles.append({'role'   : c['roleName'],
                                  'client' : MambuClient(entid=c['clientKey'], *args, **kwargs)
                                 })
                    requests += 1
                holder['roles'] = roles

            if getClients:
                requests += holder.setClients(fullDetails=fullDetails, *args, **kwargs)

                loanclients = {}

                loanclientsdata = self.getClientDetails(holder=holder, *args, **kwargs)

                for data in loanclientsdata:
                    loanclients[data['id']] = {'client'     : data['client'],
                                               'name'       : data['name'],
                                               'loan'       : self,
                                               'amount'     : data['amount'],
                                               'montoPago'  : data['amount'] / float(self['repaymentInstallments']),
                                               'porcentaje' : data['amount'] / float(self['loanAmount']),
                                              }
                    # Any extra key,val pair on loannames is plainly assigned to the loanclients[cte] dict
                    for k,v in [ (key,val) for (key,val) in data.items() if key not in['amount', 'name'] ]:
                        loanclients[data['id']][k] = v

                self['clients'] = loanclients


        else: # "CLIENT"
            from mambuclient import MambuClient

            self['holderType'] = "Cliente"
            holder = MambuClient(entid=self['accountHolderKey'],
                                 fullDetails=fullDetails, *args, **kwargs)
            self['holder'] = holder
            requests += 1

            if getClients:
                monto = float(self['loanAmount'])
                self['clients'] = {holder['name']: {'client'     : holder,
                                                          'loan'       : self,
                                                          'amount'     : monto,
                                                          'montoPago'  : monto / float(self['repaymentInstallments']),
                                                          'porcentaje' : 1.0,
                                                         }
                                        }

        return requests


    def getClientDetails(self, *args, **kwargs):
        """Gets the loan details for every client holder of the account.

        As default, assigns the whole loan amount to each client. This
        works fine for Client holders of the loan account. When Group
        holders, this is perhaps not ideal, but I cannot tell.

        If you inherit MambuLoan you should override this method to
        determine another way to assign particular amounts to each
        client.

        You can also use the overriden version of this method to add
        several other fields with information you wish to associate to
        each client holder of the loan account.

        BEWARE: for group loan accounts, this code assumes the holder
        (the group) currentrly has all the client members. But for
        accounts where the holder has changed along time, you may
        stumble upon accounts which assumes certain group members which
        weren't the members that belonged to the group when it was
        disbursed.
        """
        loannames = []

        holder = kwargs['holder']
        for client in holder['clients']:
            loannames.append({'id'     : client['id'],
                              'name'   : client['name'],
                              'client' : client,
                              'amount' : self['loanAmount']
                             })

        return loannames


    def setActivities(self, *args, **kwargs):
        """Adds the activities for this loan to a 'activities' field.

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

        activities = MambuActivities(loanAccountId=self['encodedKey'], *args, **kwargs)
        activities.attrs = sorted(activities.attrs, key=activityDate)
        self['activities'] = activities

        return 1


class MambuLoans(MambuStruct):
    """A list of Loan accounts from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the loan accounts according to
    any other filter you send to the urlfunc.

    There's another possible urlfunc you may use, getgrouploansurl. If
    you use that, you should send the ID of the group from which you
    wish to retrieve its loan accounts.

    itemclass argument allows you to pass some other class as the
    elements for the list. Why is this useful? at least for now,
    MambuLoan is the most specialized class on MambuPy. So you may
    wish to override several behaviours by creating your own
    MambuLoan son class. Pass that to the itemclass argument here
    and voila, you get a list of YourMambuLoan class using
    MambuLoans instead of plain old MambuLoan elements.

    If you wish to specialize other Mambu objects on MambuPy you may
    do that. Mind that if you desire that the iterable version of it
    to have elements of your specialized class, you need to change
    the logic of the constructor and the convertDict2Attrs method in
    the iterable class to use some sort of itemclass there too.
    Don't forget to submit the change on a pull request when done
    ;-)
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', itemclass=MambuLoan, *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several groups, not just one.
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Loan (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        MambuLoan (or your own itemclass) just created.

.. todo:: pass a valid (perhaps default) urlfunc, and its
          corresponding id to entid to each itemclass, telling MambuStruct
          not to connect() by default. It's desirable to connect at any
          other further moment to refresh some element in the list.
        """
        for n,l in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            loan = self.itemclass(urlfunc=None, entid=None, *args, **kwargs)
            loan.init(l, *args, **kwargs)
            self.attrs[n] = loan
