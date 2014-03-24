# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getloansurl, MambuError

from util import strip_consecutive_repeated_char as strip_cons, strip_tags

# {
# Datos de la cuenta
#  "id": "38802",
#  "loanName": "Validation Credito Solidario",

# Propiedades de la cuenta
#  "accountState": "ACTIVE",
#  "repaymentPeriodUnit": "DAYS",
#  "repaymentPeriodCount": 1,
#  "repaymentInstallments": 5,
#  "interestRate": "4.2",
#  "interestChargeFrequency": "EVERY_FOUR_WEEKS",
#  "interestCalculationMethod": "FLAT_FIXED",
#  "interestRateSource": "FIXED_INTEREST_RATE",
#  "interestAdjustment": "0",
#  "accruedInterest": "0",
#  "loanAmount": "1000",

# Saldos
#  "principalDue": "200",
#  "interestDue": "1.5",
#  "feesDue": "0",
#  "penaltyDue": "0",
#  "principalPaid": "0",
#  "interestPaid": "0",
#  "feesPaid": "0",
#  "penaltyPaid": "0",
#  "principalBalance": "1000",
#  "interestBalance": "7.5",

# Mas propiedades
#  "gracePeriod": 0,
#  "gracePeriodType": "NONE",
#  "notes": "testing notes<br>",
#  "principalRepaymentInterval": 1,

# Fechas
#  "approvedDate": "2012-06-13T18:05:04+0000",
#  "expectedDisbursementDate": "2012-06-12T00:00:00+0000",
#  "disbursementDate": "2012-06-12T00:00:00+0000",
#  "lastInterestAppliedDate": "2012-06-12T00:00:00+0000"
#  "lastAccountAppraisalDate": "2012-06-13T18:05:35+0000",
#  "creationDate": "2012-06-13T18:04:49+0000",
#  "lastModifiedDate": "2012-06-13T18:05:35+0000",
#  "lastSetToArrearsDate": "2012-01-01T00:00:00+0000",
#  "closedDate": "2012-01-01T00:00:00+0000",

# Relaciones
#  "productTypeKey": "8afae1dc2f3f6afa012f45bae91500d7",
#  "accountHolderType": "GROUP",
#  "accountHolderKey": "8af20ea03755684801375d6b5f7f145b",
#  "assignedUserKey": "8a5c1e9f34bdd2b90134c49b6b950948",
#  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
#  "encodedKey": "8af25b7337e52f8b0137e704ef71057b",
# }

mod_urlfunc = getloansurl

# Objeto con una Cuenta desde Mambu
class MambuLoan(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)
    
    # Deuda
    def getDebt(self):
        debt = float(self['principalBalance']) + float(self['interestBalance'])
        debt += float(self['feesBalance']) + float(self['penaltyBalance'])

        return debt

    # Preprocesamiento
    def preprocess(self):
        if self.has_key('customFieldValues'):
            for custom in self['customFieldValues']:
                custom['name'] = custom['customField']['name']
                self[custom['name']] = custom['value']
        try:
            try:
                notes = strip_cons(self['notes'], "\n")
            except KeyError:
                notes = ""
            self['notes_'] = notes

            # for e in notes.replace("\n","<br>").replace("<div>","").replace('<div style="text-align: left;">',"").replace('<p class="MsoNormal">',"").replace("</p>","").replace("<o:p>","").replace("</o:p>","").split("</div>"):
            #     s += "<br>".join([st for st in e.split("<br>") if st != ""]) + "<br>"
            # for e in self['notes'].split("<br>"):
            #     s += "<br>".join([st for st in e.replace("<div>").split("</div>") if st != ""]) + "<br>"
            # self['notes'] = strip_cons(s.strip("<br>").replace("&nbsp;"," "), " ")

            self['notes'] = strip_tags(self['notes'])
        except Exception as ex:
            pass

    # Anexa calendario de pagos de la cuenta
    # Retorna numero de requests hechos
    def setRepayments(self):
        from mamburepayment import MambuRepayments
        from util import duedate

        reps = MambuRepayments(entid=self['id'])
        reps.attrs = sorted(reps.attrs, key=duedate)
        self['repayments'] = reps

        return 1

    # Anexa transacciones de la cuenta
    # Retorna numero de requests hechos
    def setTransactions(self):
        from mambutransaction import MambuTransactions
        from util import transactionid
        
        trans = MambuTransactions(entid=self['id'])
        trans.attrs = sorted(trans.attrs, key=transactionid)
        self['transactions'] = trans

        return 1

    # Anexa sucursal de la cuenta
    # Retorna numero de requests hechos
    def setBranch(self):
        from mambubranch import MambuBranch

        branch = MambuBranch(entid=self['assignedBranchKey'])
        self['assignedBranchName'] = branch['name']
        self['assignedBranch'] = branch
        
        return 1

    # Anexa usuario de la cuenta
    # Retorna numero de requests hechos
    def setUser(self):
        from mambuuser import MambuUser

        try:
            user = MambuUser(entid=self['assignedUserKey'])
        except KeyError as kerr:
            raise MambuError("La cuenta %s no tiene asignado un usuario" % self['id'])

        self['user'] = user

        return 1

    # Anexa holder de la cuenta (integrante para individual, grupo e integrantes para grupal)
    # Retorna numero de requests hechos
    def setHolder(self, getClients=False, getRoles=False):

        params = {'fullDetails': True}
        requests = 0

        if self['accountHolderType'] == "GROUP":
            from mambugroup import MambuGroup

            self['holderType'] = "Grupo"
            holder = MambuGroup(entid=self['accountHolderKey'], **params)
            requests += 1

            if getRoles:
                from mambuclient import MambuClient
                
                roles = []
                # If holder is group, attach role client data to the group
                for c in holder['groupRoles']:
                    roles.append({'role'   : c['roleName'],
                                  'client' : MambuClient(entid=c['clientKey'])
                                 })
                    requests += 1
                holder['roles'] = roles

            if getClients:
                requests += holder.setClients()
                
                loanclients = {}

                loannombres = self.getClientDetails(holder=holder) # Esto seguro se puede sustituir por with y context managers...

                for client in holder['clients']:
                    if client['name'] in [ l['name'] for l in loannombres ]:
                        for cte in [ l for l in loannombres if l['name'] == client['name'] ]:
                            loanclients[cte['name']] = {'client'     : client,
                                                        'loan'       : self,
                                                        'amount'     : cte['amount'],
                                                        'montoPago'  : cte['amount'] / float(self['repaymentInstallments']),
                                                        'porcentaje' : cte['amount'] / float(self['loanAmount']),
                                                       }

                self['clients'] = loanclients


        else: # "CLIENT"
            from mambuclient import MambuClient
            
            self['holderType'] = "Cliente"
            holder = MambuClient(entid=self['accountHolderKey'],
                                 **params)
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

        self['holder'] = holder

        return requests

    # Detalles de los clientes (nombre-monto)
    # Por default asigna a cada cliente la cantidad total del credito
    def getClientDetails(self, *args, **kwargs):
        loannombres = []

        holder = kwargs['holder']
        for client in holder['clients']:
            loannombres.append({'name': client['name'], 'amount': self['loanAmount']})

        return loannombres

# Objeto con una lista de Cuentas Mambu
class MambuLoans(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', itemclass=MambuLoan, *args, **kwargs):
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)
    
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        for n,l in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            loan = self.itemclass(urlfunc=None, entid=None, *args, **kwargs)
            loan.init(l, *args, **kwargs)
            self.attrs[n] = loan
