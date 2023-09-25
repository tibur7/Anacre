#%%
class ValueMapping():
    ReferenceDate = 'Reference date',
    TypeOfInstrument = 'Type of Instrument',
    AmortisationType = 'Amortisation type',
    Currency = 'Currency',
    FiduciaryInstrument = 'Fiduciary instrument',
    InterestRateResetFrequency = 'Interest rate reset frequency',
    InterestRateType = 'Interest rate type',
    PaymentFrequency = 'Payment frequency',
    ProjectFinanceLoan = ' Project finance loan',
    Purpose = 'Purpose',
    Recourse = 'Recourse',
    ReferenceRate = 'Reference rate',
    SubordinatedDebt = 'Subordinated debt',
    RepaymentRights = 'Repayment rights',
    DefaultStatusOfInstrument = 'Default status of instrument',
    TypeOfSecurisation = 'Type of securisation',
    CounterpartyRole = 'Counterparty role',
    TypeOfProtection = 'Type of protection',
    TypeOfProtectionValue = 'Type of protection value',
    ProtectionValuationApproach = 'Protection valuation approach',
    RealEstateCollateralLocation = 'Real estate collateral location',
    ReclCountry = 'RECL Country',
    ReclRegion = 'RECL Region',
    ReclPostalCode = 'RECL Postal code',
    DefaultStatusOfCounterparty = 'Default status of counterparty'


class Mapping():
    
    def __init__(self, mapdict:dict):
        self.mapdict = mapdict

    def combined_from_key(self, key:str)->str:

        return  key + " - " +self.mapdict[key]
    

    def get_key(self,description:str)->str:
        for k, v in self.mapdict.items():
            if v == description:
                return k
            
#%%

M = ValueMapping


dic = {
    "1": "Creditor",
    "2": "Debtor",
    "3": "Originator",
    "7": "Servicer"
}

counterparty_role = Mapping(dic)




# %%
counterparty_role.get_key("Debtor")
# %%
counterparty_role.combined_from_key("2")
# %%
mapping_dic={}
mapping_dic[M.CounterpartyRole]=dic

dic = {
    "NR": "Not required",
    "1000": "Deposits other than reverse repurchase agreements",
    "1001": "Revolving credit other than overdrafts and credit card debt",
    "1002": "Credit lines other than revolving credit",
    "1003": "Reverse repurchase agreements",
    "1004": "Loans other than overdrafts, convenience credit, extended credit, credit card credit, revolving credit other than credit card credit, reverse repurchase agreements, trade receivables and financial leases",
    "20": "Overdrafts",
    "51": "Credit card debt",
    "71": "Trade receivables",
    "80": "Finance leases"
}

mapping_dic[M.TypeOfInstrument] = dic

mapping_dic[M.AmortisationType] = {
    "NR": "Not required",
    "1": "French",
    "2": "German",
    "3": "Fixed amortisation schedule",
    "4": "Bullet",
    "5": "Amortisation types other than French, German, Fixed amortisation schedule or bullet"
}


mapping_dic[M.Currency] = key_value_pairs = {
    "NR": "Not required",
    "AED": "UAE Dirham",
    "AFN": "Afghani",
    "ALL": "Lek",
    "AMD": "Armenian Dram",
    "ANG": "Netherlands Antillean Guilder",
    "AOA": "Kwanza",
    "ARS": "Argentine Peso",
    "AUD": "Australian Dollar",
    "AWG": "Aruban Florin",
    "AZN": "Azerbaijanian Manat",
    "BAM": "Convertible Mark",
    "BBD": "Barbados Dollar",
    "BDT": "Taka",
    "BGN": "Bulgarian lev",
    "BHD": "Bahraini Dinar",
    "BIF": "Burundi Franc",
    "BMD": "Bermudian Dollar",
    "BND": "Brunei Dollar",
    "BOB": "Boliviano",
    "BOV": "Mvdol",
    "BRL": "Brazilian Real",
    "BSD": "Bahamian Dollar",
    "BTN": "Ngultrum",
    "BWP": "Pula",
    "BYN": "Belarussian Ruble",
    "BZD": "Belize Dollar",
    "CAD": "Canadian Dollar",
    "CDF": "Congolese Franc",
    "CHE": "WIR Euro",
    "CHF": "Swiss franc",
    "CHW": "WIR Franc",
    "CLF": "Unidades de fomento",
    "CLP": "Chilean Peso",
    "CNY": "Yuan Renminbi",
    "COP": "Colombian Peso",
    "COU": "Unidad de Valor Real",
    "CRC": "Costa Rican Colon",
    "CUC": "Peso Convertible",
    "CUP": "Cuban Peso",
    "CVE": "Cape Verde Escudo",
    "CZK": "Czech koruna",
    "DJF": "Djibouti Franc",
    "DKK": "Danish krone",
    "DOP": "Dominican Peso",
    "DZD": "Algerian Dinar",
    "EGP": "Egyptian Pound",
    "ERN": "Nakfa",
    "ETB": "Ethiopian Birr",
    "EUR": "Euro",
    "FJD": "Fiji Dollar",
    "FKP": "Falkland Islands Pound",
    "GBP": "UK pound sterling",
    "GEL": "Lari",
    "GHS": "Ghana Cedi",
    "GIP": "Gibraltar Pound",
    "GMD": "Dalasi",
    "GNF": "Guinea Franc",
    "GTQ": "Quetzal",
    "GYD": "Guyana Dollar",
    "HKD": "Hong Kong Dollar",
    "HNL": "Lempira",
    "HRK": "Croatian kuna",
    "HTG": "Gourde",
    "HUF": "Hungarian forint",
    "IDR": "Rupiah",
    "ILS": "New Israeli Sheqel",
    "INR": "Indian Rupee",
    "IQD": "Iraqi Dinar",
    "IRR": "Iranian Rial",
    "ISK": "Iceland Krona",
    "JMD": "Jamaican Dollar",
    "JOD": "Jordanian Dinar",
    "JPY": "Japanese yen",
    "KES": "Kenyan Shilling",
    "KGS": "Som",
    "KHR": "Riel",
    "KMF": "Comoro Franc",
    "KPW": "North Korean Won",
    "KRW": "Won",
    "KWD": "Kuwaiti Dinar",
    "KYD": "Cayman Islands Dollar",
    "KZT": "Tenge",
    "LAK": "Kip",
    "LBP": "Lebanese Pound",
    "LKR": "Sri Lanka Rupee",
    "LRD": "Liberian Dollar",
    "LSL": "Loti",
    "LYD": "Libyan Dinar",
    "MAD": "Moroccan Dirham",
    "MDL": "Moldovan Leu",
    "MGA": "Malagasy Ariary",
    "MKD": "Denar",
    "MMK": "Kyat",
    "MNT": "Tugrik",
    "MOP": "Pataca",
    "MRO": "Ouguiya",
    "MRU": "Ouguiya",
    "MUR": "Mauritius Rupee",
    "MVR": "Rufiyaa",
    "MWK": "Kwacha",
    "MXN": "Mexican Peso",
    "MXV": "Mexican Unidad de Inversion (UDI)",
    "MYR": "Malaysian Ringgit",
    "MZN": "Mozambique Metical",
    "NAD": "Namibia Dollar",
    "NGN": "Naira",
    "NIO": "Cordoba Oro",
    "NOK": "Norwegian Krone",
    "NPR": "Nepalese Rupee",
    "NZD": "New Zealand Dollar",
    "OMR": "Rial Omani",
    "PAB": "Balboa",
    "PEN": "Nuevo Sol",
    "PGK": "Kina",
    "PHP": "Philippine Peso",
    "PKR": "Pakistan Rupee",
    "PLN": "Polish zloty",
    "PYG": "Guarani",
    "QAR": "Qatari Rial",
    "RON": "Romanian leu",
    "RSD": "Serbian Dinar",
    "RUB": "Russian Ruble",
    "RWF": "Rwanda Franc",
    "SAR": "Saudi Riyal",
    "SBD": "Solomon Islands Dollar",
    "SCR": "Seychelles Rupee",
    "SDG": "Sudanese Pound",
    "SEK": "Swedish krona",
    "SGD": "Singapore Dollar",
    "SHP": "Saint Helena Pound",
    "SLL": "Leone",
    "SOS": "Somali Shilling",
    "SRD": "Surinam Dollar",
    "SSP": "South Sudanese Pound",
    "STD": "Dobra",
    "STN": "Dobra",
    "SVC": "El Salvador Colon",
    "SYP": "Syrian Pound",
    "SZL": "Lilangeni",
    "THB": "Baht",
    "TJS": "Somoni",
    "TMT": "Turkmenistan New Manat",
    "TND": "Tunisian Dinar"}

mapping_dic[M.FiduciaryInstrument] = {
    "NR": "Not required",
    "1": "Fiduciary instrument",
    "2": "Non-fiduciary instrument"
}

    

