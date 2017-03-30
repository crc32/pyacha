from datetime import datetime
from decimal import Decimal


class Nacha_PPD_Entry(object):
    def __init__(self, _batch = None, **keywords):
        defaults = {
            # < Number of characters in Field> : < Description of Field >
            'Record_Code': 6,              # 1 : 6 = PPD Entry
            'Transaction_Code': None,      # 2 : Transaction Code, see below
            'Amount': 0,                   # 10: Amount, integer cents
                                           #     ($1.54 == 154)
            'Target_DFI': '',              # 8 : First 8 digits of the target's
                                           #     bank transit routing number
            'Target_Check_Digit': 0,       # 1 : Last digit of the target's
                                           #     bank transit routing number
            'Target_ID': '',               # 15: Internal ID number,
                                           #     for your tracking
            'Target_Name': '',             # 22: Name of target
            'Target_Account_Number': '',   # 17: Target's DFI Account Number
            'Discretionary_Data': '',      # 2 : LEAVE BLANK
            'Addenda_Record_Indicator': 0, # 1 : This record has an
                                           #    addenda (7) record
            'Trace_Number': 1,             # 7 : Unique ID number for this line
            'Transaction_Type': 'CR',      # xx: Not a record, used to create
                                           #     Transaction_Code. DR or CR
            'Account_Type': 'CHK'          # xx: Not a record, used to create
                                           #     Transaction_Code. CHK or SAV
            }
        defaults.update(keywords)
        self.Record_Code              = defaults['Record_Code']
        self.Transaction_Code         = defaults['Transaction_Code']
        self.Amount                   = defaults['Amount']
        self.Target_DFI               = defaults['Target_DFI']
        self.Target_Check_Digit       = defaults['Target_Check_Digit']
        self.Target_Account_Number    = defaults['Target_Account_Number']
        self.Target_ID                = defaults['Target_ID']
        self.Target_Name              = defaults['Target_Name']
        self.Discretionary_Data       = defaults['Discretionary_Data']
        self.Addenda_Record_Indicator = defaults['Addenda_Record_Indicator']
        self.Trace_Number             = defaults['Trace_Number']
        self.Account_Type             = defaults['Account_Type']
        self.Transaction_Type         = defaults['Transaction_Type']
        self.Batch                    = _batch
        if self.Transaction_Code is None:
            self.createTransactionCode()


    def __repr__(self):
        ppd_entry_template = ("{reccode}" +
                              "{transcode}" +
                              "{rdfi: <9.9}" +
                              "{racct: <17.17}" +
                              "{amt:0>10.10}" +
                              "{recipientid: <15.15}" +
                              "{recipientname: <22.22}" +
                              "{discdata: <2.2}" +
                              "{addenda: <1.1}" +
                              "{odfi:0<8.8}" +
                              "{trace:0>7.7}")
        output = ''
        if self.Batch is None:
            output = ppd_entry_template.format(
                reccode       = str(self.Record_Code),
                transcode     = str(self.Transaction_Code),
                rdfi          = (str(self.Target_DFI) +
                                 str(self.Target_Check_Digit)),
                racct         = str(self.Target_Account_Number),
                amt           = str(self.Amount),
                recipientid   = str(self.Target_ID),
                recipientname = str(self.Target_Name),
                discdata      = str(self.Discretionary_Data),
                addenda       = str(self.Addenda_Record_Indicator),
                odfi          = str('99999999'),
                trace         = str(10000 + self.Trace_Number)
                )
        else:
            output = ppd_entry_template.format(
                reccode       = str(self.Record_Code),
                transcode     = str(self.Transaction_Code),
                rdfi          = (str(self.Target_DFI) +
                                 str(self.Target_Check_Digit)),
                racct         = str(self.Target_Account_Number),
                amt           = str(self.Amount),
                recipientid   = str(self.Target_ID),
                recipientname = str(self.Target_Name),
                discdata      = str(self.Discretionary_Data),
                addenda       = str(self.Addenda_Record_Indicator),
                odfi          = str(self.Batch.Company_DFI),
                trace         = str(self.Batch.Batch_Number + self.Trace_Number)
                )
        return output


    def createTransactionCode(self):
        code_lookup = {'CHKCR': 22,
                       'CHKDR': 27,
                       'SAVCR': 32,
                       'SAVDR': 37}
        self.Transaction_Code = code_lookup[self.Account_Type +
                                            self.Transaction_Type]


    def entryType(self):
        # LIVE-DOLLAR CODESTRANSACTION TYPE
        #   22 CREDIT TO CHECKING ACCOUNT
        #   27 DEBIT TO CHECKING ACCOUNT
        #   32 CREDIT TO SAVINGS ACCOUNT
        #   37 DEBIT TO SAVINGS ACCOUNT
        # ZERO-DOLLAR CODES TRANSACTION TYPE
        #   23 CREDIT PRENOTE TO CHECKING
        #   28 DEBIT PRENOTE TO CHECKING
        #   33 CREDIT PRENOTE TO SAVINGS
        #   38 DEBIT PRENOTE TO SAVINGS
        if self.Transaction_Code in [22, 32]:
            return 1
        elif self.Transaction_Code in [27, 37]:
            return 2
        else:
            return False


class Nacha_Batch(object):
    def __init__(self, _file = None, **keywords):
        defaults = {
            # < Number of characters in Field> : < Description of Field >
            'Batch_Open_Code': 5,          # 1 : 5 = Open Batch Record
            'Batch_Close_Code': 8,         # 1 : 8 = Close Batch Record
            'Service_Class_Code': 200,     # 3 : Service Class Code, see below
            'Company_DFI': '',             # 8 : First 8 digits of the Company's
                                           #     bank transit routing number
            'CompanyDFI_Check_Digit': 0,   # 1 : Last digit of the target's
                                           #     bank transit routing number
            'Effective_Date': '',          # 6 : Date the company intends the
                                           #     batch to be settled
            'Descriptive_Date': '',        # 6 : Descriptive Date for
                                           #     Reveicer's reference
            'Company_Entry_Desc': '',      # 10: Description of the transaction
                                           #     for the Reveicer
            'Company_Name': '',            # 16: Name of company
            'Co_Discretionary_Data': '',   # 20: Reference info
            'Company_ID': '',              # 10: Often the company's EIN with a
                                           #     padding character ('1' or ' ')
            'Originator_Status_Code': 1,   # 1 : This field must be the number 1
            'SEC_Code': 'PPD',             # 3 : See Below
            'Settlement_Date': '',         # 3 : BLANK
            'Batch_Number': 1,             # 7 : Unique Batch ID number
                                           #     for this batch
            'Message_Auth_Code': '',       # 19: BLANK
            'Reserved': '',                # 6 : BLANK
            'Batch_Number': 1              # 7 : Incremental batch number
                                           #     for file
            }
        defaults.update(keywords)
        self.Batch_Open_Code          = defaults['Batch_Open_Code']
        self.Batch_Close_Code         = defaults['Batch_Close_Code']
        self.Company_DFI              = defaults['Company_DFI']
        self.CompanyDFI_Check_Digit   = defaults['CompanyDFI_Check_Digit']
        self.Effective_Date           = defaults['Effective_Date']
        self.Descriptive_Date         = defaults['Descriptive_Date']
        self.Company_Entry_Desc       = defaults['Company_Entry_Desc']
        self.Company_Name             = defaults['Company_Name']
        self.Co_Discretionary_Data    = defaults['Co_Discretionary_Data']
        self.Company_ID               = defaults['Company_ID']
        self.Originator_Status_Code   = defaults['Originator_Status_Code']
        self.Settlement_Date          = defaults['Settlement_Date']
        self.Batch_Number             = defaults['Batch_Number']
        self.Message_Auth_Code        = defaults['Message_Auth_Code']
        self.Reserved                 = defaults['Reserved']
        self.Service_Class_Code       = defaults['Service_Class_Code']
        self.SEC_Code                 = defaults['SEC_Code']
        self.Entries                  = []
        self.Batch_Number             = defaults['Batch_Number']
        self.File                     = _file


    def getDebits(self):
        running_debits = 0
        for entry in self.Entries:
            if entry.entryType() == 2:
                running_debits = running_debits + entry.Amount
        return running_debits


    def getCredits(self):
        running_credits = 0
        for entry in self.Entries:
            if entry.entryType() == 1:
                running_credits = running_credits + entry.Amount
        return running_credits


    def getHeader(self):
        batch_hdr_template = ("{reccode}{svccode:0>3.3}{coname: <16.16}" +
                              "{discdata: <20.20}{coid: <10.10}" +
                              "{secclass: <3.3}{entrydesc: <10.10}" +
                              "{entrydate: <6.6}{effdate: <6.6}" +
                              "{settledate: <3.3}{oristatus:.1}" +
                              "{odfi: <8.8}{batch:0>7.7}")
        header = batch_hdr_template.format(
            reccode    = str(self.Batch_Open_Code),
            svccode    = str(self.Service_Class_Code),
            coname     = str(self.Company_Name),
            discdata   = str(self.Co_Discretionary_Data),
            coid       = str(self.Company_ID),
            secclass   = str(self.SEC_Code),
            entrydesc  = str(self.Company_Entry_Desc),
            entrydate  = str(self.Descriptive_Date.strftime('%y%m%d%H%M')),
            effdate    = str(self.Effective_Date.strftime('%y%m%d%H%M')),
            settledate = str(self.Settlement_Date),
            oristatus  = str(self.Originator_Status_Code),
            odfi       = str(self.Company_DFI),
            batch      = str(self.Batch_Number))
        return header


    def getFooter(self, _hash, _debits, _credits):
        batch_ftr_template = ("{reccode}{svccode:0>3.3}{entrycount:0>6.6}" +
                              "{entryhash:0>10.10}{debits:0>12.12}" +
                              "{credits:0>12.12}{co_id:1>10.10}" +
                              "{authcode: >19.19}{reserved: >6.6}" +
                              "{odfi: <8.8}{batch:0>7.7}")
        footer = batch_ftr_template.format(
            reccode    = str(self.Batch_Close_Code),
            svccode    = str(self.Service_Class_Code),
            entrycount = str(len(self.Entries)),
            entryhash  = str(_hash),
            debits     = str(_debits),
            credits    = str(_credits),
            co_id      = str(self.Company_ID),
            authcode   = '',
            reserved   = '',
            odfi       = str(self.Company_DFI),
            batch      = str(self.Batch_Number))
        return footer


    def getHash(self):
        temp_hash = 0
        for entry in self.Entries:
            temp_hash = temp_hash + int(entry.Target_DFI)
        return temp_hash


    def addEntry(self, kind='PPD', **keywords):
        defaults = {'Trace_Number':int((len(self.Entries)+1))}
        defaults.update(keywords)
        if kind == 'PPD':
            self.Entries.append(Nacha_PPD_Entry(_batch=self,**defaults))


    def countEntries(self):
        return len(self.Entries)


    def __getitem__(self, item):
        return self.Entries[item]


    def __repr__(self):
        return '\n'.join(self.getList())


    def getList(self):
        header = self.getHeader()
        footer = self.getFooter()
        temp_entries = []
        i = 0
        for entry in self.Entries:
            i = i + 1
            temp_entries.append(repr(entry))
        output = []
        output.append(header)
        output.extend(temp_entries)
        output.append(footer)
        return output


class Nacha_File(object):
    def __init__(self, **keywords):
        defaults = {
            # < Number of characters in Field> : < Description of Field >
            'File_Open_Code': '1',             # 1 : 1 = Open File Record
            'File_Close_Code': '9',            # 1 : 9 = Close File Record
            'Record_Priority': '01',           # 2 : Priority Code (often 01)
            'Immediate_Destination_ID': '',    # 10: Initial Target Bank DFI
            'Immediate_Origin_ID': '',         # 10: Company ID (often EIN)
            'File_ID': '0',                    # 1 : File ID modifier (0-9 A-Z)
            'File_Date': datetime.now(),       # 10: Creation Date '%y%m%d%H%M'
            'Record_Size': '094',              # 3 : Characters in record (094)
            'Blocking_Factor': '10',           # 2 : Block Size (10)
            'Format_Code': '1',                # 1 : Format Code (1)
            'Immediate_Destination_Name': '',  # 12: Name of receiving bank
            'Immediate_Origin_Name': '',       # 12: Company Name
            'Reference_Code': '00000000'       # 8 : File Reference Code
            }
        defaults.update(keywords)
        self.File_Open_Code             = defaults['File_Open_Code']
        self.File_Close_Code            = defaults['File_Close_Code']
        self.Record_Priority            = defaults['Record_Priority']
        self.Immediate_Destination_ID   = defaults['Immediate_Destination_ID']
        self.Immediate_Origin_ID        = defaults['Immediate_Origin_ID']
        self.File_ID                    = defaults['File_ID']
        self.File_Date                  = defaults['File_Date']
        self.Record_Size                = defaults['Record_Size']
        self.Blocking_Factor            = defaults['Blocking_Factor']
        self.Format_Code                = defaults['Format_Code']
        self.Immediate_Destination_Name = defaults['Immediate_Destination_Name']
        self.Immediate_Origin_Name      = defaults['Immediate_Origin_Name']
        self.Reference_Code             = defaults['Reference_Code']
        self.Batches                    = []
        self.Reserved                   = ''


    def countStats(self):
        entries = 0
        for batch in self.Batches:
            entries = batch.countEntries() + entries
        lines = 2 + entries + (len(self.Batches) * 2)
        blocks = int(Decimal(lines)/10)+1
        return (entries, lines, blocks)


    def fillerNines(self):
        (entries, lines, blocks) = self.countStats()
        block_template = '{0:9>94.94}'.format('')
        output = []
        if not (lines % 10) == 10:
            for i in range(0,(10 - (lines % 10))):
                output.append('{0:9>94.94}'.format(''))
        return output


    def getHeader(self):
        file_hdr_template = ("{reccode}{recpri}{immdest:>10}{immorigin:<10.10}" +
                           "{fdate}{id}{recsize}{blockfact}{fmtcode}" +
                           "{dstname:<23.23}{oriname:<23.23}{refcode:8}")
        output = file_hdr_template.format(
            reccode   = str(self.File_Open_Code),
            recpri    = str(self.Record_Priority),
            immdest   = str(self.Immediate_Destination_ID),
            immorigin = str(self.Immediate_Origin_ID),
            fdate     = str(self.File_Date.strftime('%y%m%d%H%M')),
            id        = str(self.File_ID),
            recsize   = str(self.Record_Size),
            blockfact = str(self.Blocking_Factor),
            fmtcode   = str(self.Format_Code),
            dstname   = str(self.Immediate_Destination_Name),
            oriname   = str(self.Immediate_Origin_Name),
            refcode   = str(self.Reference_Code))
        return output


    def getHash(self):
        temp_hash = 0
        for batch in self.Batches:
            temp_hash = temp_hash + int(batch.getHash())
        return temp_hash


    def getCredits(self):
        running_credits = 0
        for batch in self.Batches:
            running_credits = running_credits + int(batch.getCredits())
        return running_credits


    def getDebits(self):
        running_debits = 0
        for batch in self.Batches:
            running_debits = running_debits + int(batch.getDebits())
        return running_debits


    def getFooter(self):
        file_ftr_template = ("{reccode}{batchcount:0>6.6}{blockcount:0>6.6}" +
                                 "{entrycount:0>8.8}{hash:0>10.10}" +
                                 "{debits:0>12.12}{credits:0>12.12}" +
                                 "{res: >39.39}")
        (entries, lines, blocks) = self.countStats()
        output = file_ftr_template.format(
            reccode    = str(self.File_Close_Code),
            batchcount = str(len(self.Batches)),
            blockcount = str(blocks),
            entrycount = str(entries),
            hash       = str(self.getHash())[-10:],  # Left side truncation
            debits     = str(self.getDebits()),
            credits    = str(self.getCredits()),
            res        = str(self.Reserved))
        return output


    def addBatch(self, **keywords):
        defaults = {'Batch_Number':int(((len(self.Batches)+1)*10000))}
        defaults.update(keywords)
        self.Batches.append(Nacha_Batch(_file=self,**defaults))


    def __getitem__(self, item):
        return self.Batches[item]


    def __repr__(self):
        return '\n'.join(self.getList())

    def getList(self):
        output = []
        output.append(self.getHeader())
        for batch in self.Batches:
            output.append(batch.getHeader())
            for entry in batch:
                output.append(repr(entry))
            output.append(batch.getFooter(_hash=batch.getHash(),
                                          _debits=batch.getDebits(),
                                          _credits=batch.getCredits()))
        output.append(self.getFooter())
        output.extend(self.fillerNines())
        return output


if __name__ == '__main__':
    i = 1
