# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from podemos import PodemosError, getloansurl, DEBUG, ERROR_CODES
from util import strip_consecutive_repeated_char as strip_cons, strip_tags
from datetime import datetime
from products import products
import re

# {
# Datos de la cuenta
#  "id": "38802",
#  "loanName": "Validation Credito Solidario",

# Propiedades de la cuenta
#  "accountState": "ACTIVE",
#  "repaymentPeriodUnit": "DAYS",
#  "repaymentInstallments": 5,
#  "interestRate": "4.2",
#  "interestChargeFrequency": "EVERY_FOUR_WEEKS",
#  "interestCalculationMethod": "FLAT_FIXED",
#  "interestRateSource": "FIXED_INTEREST_RATE",
#  "interestAdjustment": "0",
#  "accruedInterest": "0",
#  "principalRepaymentInterval": 1,
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
#  "repaymentPeriodCount": 1,
#  "notes": "testing notes<br>",

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

urlfunc = getloansurl

# Objeto con una lista de Cuentas Mambu
class MambuLoans(MambuStruct):
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __len__(self):
        return len(self.attrs)

    def convertDict2Attrs(self):
        for n,l in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            loan = MambuLoan(urlfunc=None, entid=None, **params)
            loan.init(l)
            self.attrs[n] = loan

# Objeto con una Cuenta desde Mambu
class MambuLoan(MambuStruct):
    # Deuda
    def getDebt(self):
        debt = float(self.attrs['principalBalance']) + float(self.attrs['interestBalance'])
        debt += float(self.attrs['feesBalance']) + float(self.attrs['penaltyBalance'])

        return debt

    # Preprocesamiento
    def preprocess(self):
        if self.attrs.has_key('customFieldValues'):
            for custom in self.attrs['customFieldValues']:
                custom['name'] = custom['customField']['name']
                self.attrs[custom['name']] = custom['value']

        prods = dict((v['key'],k) for k,v in products.iteritems())
        try:
            self.attrs['productTypeName'] = prods[self.attrs['productTypeKey']]
            self.attrs['productMora'] = products[self.attrs['productTypeName']]['mora']
        except Exception as ex:
            self.attrs['productTypeName'] = ""
            self.attrs['productMora'] = "0"

        try:
            s = ""
            try:
                notes = strip_cons(self.attrs['notes'], "\n")
            except KeyError:
                notes = ""
            self.attrs['notes_'] = notes

            # for e in notes.replace("\n","<br>").replace("<div>","").replace('<div style="text-align: left;">',"").replace('<p class="MsoNormal">',"").replace("</p>","").replace("<o:p>","").replace("</o:p>","").split("</div>"):
            #     s += "<br>".join([st for st in e.split("<br>") if st != ""]) + "<br>"
            # for e in self.attrs['notes'].split("<br>"):
            #     s += "<br>".join([st for st in e.replace("<div>").split("</div>") if st != ""]) + "<br>"
            # self.attrs['notes'] = strip_cons(s.strip("<br>").replace("&nbsp;"," "), " ")

            self.attrs['notes'] = strip_tags(self.attrs['notes'])

            # Hay notas en mambu que a veces no tienen un <br> dividiendo
            # cada renglon, y hay que insertarlo
            notas = ""
            pcalif = re.compile(r"^[0-9]+")
            pnombre = re.compile(u"[a-zA-ZñÑ\xc3\x91\s.]+$") # \xc3\x91 = Ñ
            for part in self.attrs["notes"].split("|"):
                mcalif = pcalif.search(part)
                mnombre = pnombre.search(part)
                try:
                    calif = mcalif.group(0)
                    nombre = mnombre.group(0)
                    notas = notas + calif + "<br>" + nombre + "|"
                except AttributeError:
                    notas = notas + part + "|"
            notas = notas.strip("|").strip().strip("<br>").strip()
            
            self.attrs['notes'] = notas

            totnotas = 0
            for note in self['notes'].split("<br>"):
                if note in ["", "<br>", "<div>", "</div>", "\n", " "]:
                    continue
                totnotas += 1
            self.attrs['totnotes'] = totnotas

        except Exception as ex:
            pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            self.attrs['repaymentInstallments'] = int(self.attrs['repaymentInstallments'])
            self.attrs['interestRate'] = float(self.attrs['interestRate'])

            self.attrs['loanAmount'] = float(self.attrs['loanAmount'])

            self.attrs['principalDue'] = float(self.attrs['principalDue'])
            self.attrs['interestDue'] = float(self.attrs['interestDue'])
            self.attrs['feesDue'] = float(self.attrs['feesDue'])
            self.attrs['penaltyDue'] = float(self.attrs['penaltyDue'])

            self.attrs['principalPaid'] = float(self.attrs['principalPaid'])
            self.attrs['interestPaid'] = float(self.attrs['interestPaid'])
            self.attrs['feesPaid'] = float(self.attrs['feesPaid'])
            self.attrs['penaltyPaid'] = float(self.attrs['penaltyPaid'])

            self.attrs['creationDate'] = datetime.strptime(self.attrs['creationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            self.attrs['lastModifiedDate'] = datetime.strptime(self.attrs['lastModifiedDate'], "%Y-%m-%dT%H:%M:%S+0000")

            try:
                self.attrs['approvedDate'] = datetime.strptime(self.attrs['approvedDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['expectedDisbursementDate'] = datetime.strptime(self.attrs['expectedDisbursementDate'],
                                                                           "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['disbursementDate'] = datetime.strptime(self.attrs['disbursementDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['lastSetToArrearsDate'] = datetime.strptime(self.attrs['lastSetToArrearsDate'],
                                                                       "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['closedDate'] = datetime.strptime(self.attrs['closedDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))

    # Anexa calendario de pagos de la cuenta
    def setRepayments(self):
        from mamburepayment import MambuRepayments
        from podemos import getrepaymentsurl
        from util import duedate

        reps = MambuRepayments(entid=self['id'], urlfunc=getrepaymentsurl)
        self.attrs['repayments'] = sorted(reps, key=duedate)

    # Anexa transacciones de la cuenta
    def setTransactions(self):
        from mambutransaction import MambuTransactions
        from podemos import gettransactionsurl
        from util import transactionid
        
        trans = MambuTransactions(entid=self['id'], urlfunc=gettransactionsurl)
        self.attrs['transactions'] = sorted(trans, key=transactionid)

    def setBranch(self):
        from mambubranch import MambuBranches
        from podemos import getbranchesurl

        branches = MambuBranches(urlfunc=getbranchesurl)
        for branch in branches:
            if branch['encodedKey'] == self['assignedBranchKey']:
                self.attrs['assignedBranchName'] = branch['name']

    # Anexa holder de la cuenta (integrante para individual, grupo e integrantes para grupal)
    def setHolder(self, getClients=False, getRoles=False):
        from mambuclient import MambuClient
        from podemos import getclienturl

        params = {'fullDetails': True}

        if self['accountHolderType'] == "GROUP":
            from mambugroup import MambuGroup
            from podemos import getgroupurl

            holder = MambuGroup(entid=self['accountHolderKey'], urlfunc=getgroupurl, **params)

            if getRoles:
                roles = []
                # If holder is group, attach role client data to the group
                for c in holder['groupRoles']:
                    roles.append({'role'   : c['roleName'],
                                  'client' : MambuClient(entid=c['clientKey'],
                                                         urlfunc=getclienturl)})
                holder.attrs['roles'] = roles

            if getClients:
                clients = []
                loanclients = {}

                loannombres = []
                for nota in self['notes'].split("<br>"):
                    fields = nota.split("|")
                    loannombres.append(fields[0])

                for m in holder['groupMembers']:
                    client = MambuClient(entid=m['clientKey'],
                                         urlfunc=getclienturl,
                                         **params)

                    nombre = ""
                    if client.attrs["firstName"].strip() != "":
                        nombre += client.attrs["firstName"].strip()
                    if client.attrs["middleName"].strip() != "":
                        nombre += " " + client.attrs["middleName"].strip()
                    if client.attrs["lastName"].strip() != "":
                        nombre += " " + client.attrs["lastName"].strip()
                    nombre = nombre.strip()

                    clients.append(client)

                    if nombre in loannombres:
                        loanclients[nombre] = client

                holder.attrs['clients'] = clients
                self.attrs['clients'] = loanclients
                    

        else: # "CLIENT"
            holder = MambuClient(entid=self['accountHolderKey'],
                                 urlfunc=getclienturl,
                                 **params)

        self.attrs['holder'] = holder
