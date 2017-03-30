# pyacha
Python NACHA file builder.

## Version 0.1 - 20170330

I was unimpressed with the state of the NACHA processors available for Python,
so I quickly coded this up to allow me to build files which were compatable
with my bank. I tried to make it generic, so that if I had to swich banks,
it would be easy to adapt.

Right now, all it can do is create PPD entries, without Addenda. However,
the Batch and File objects should be nearly ready to accept other entry types.

## Use

To build a compliant file, you need to provide a minimum of information.

        from datetime import datetime, timedelta
        from decimal import Decimal
        
        file_def = {
            'Immediate_Destination_ID': 'XXX',   # Bank ABA Routing Number
            'Immediate_Origin_ID': 'XXX',        # Company ID (often the EIN)
            'File_Date': datetime.now(),         # File Creation Date
            'Immediate_Destination_Name': 'XXX', # Name of Bank
            'Immediate_Origin_Name': 'XXX'       # Name of Company
        }

        batch_def = {
            'Company_Name'           : file_def['Immediate_Origin_Name'].upper(),  # Uppercase of the Company name
            'Company_ID'             : file_def['Immediate_Origin_ID'],            # Company ID
            'Company_Entry_Desc'     : 'PAYROLL',                                  # Entry Description
            'Company_DFI'            : file_def['Immediate_Destination_ID'][:8],   # Bank ID (without the check digit)
            'CompanyDFI_Check_Digit' : file_def['Immediate_Destination_ID'][8:9],  # Bank ID Check Digit
            'Effective_Date'         : datetime.now() + timedelta(1),              # ACH Effective Date
            'Descriptive_Date'       : datetime.now()                              # File Creation Date
        }

        nacha_file = Nacha_File(**file_def)
        nacha_file.addBatch(**batch_def)
        
        # obviously you can have your raw records any way you like. Below assumes a list of dicts
        for record in records:

            nacha_file[0].addEntry(**{
                'Account_Type'         : record['Type'],                 # CHK or SAV for Checking or Savings
                'Target_DFI'           : record['TargetRouting'][:8],    # Target's routing number (DFI)
                'Target_Check_Digit'   : record['TargetRouting'][8:9],   # Target's routing number (DFI Check)
                'Target_Account_Number': record['TargetAccount'],        # Target's Account Number
                'Transaction_Type'     : record['TxnType'],              # Transaction Type ('CR' or 'DR') for Credit or Debit
                                                                         # Credit is GIVING money, Debit is TAKING money
                'Target_Name'          : record['TargetName'],           # Target's name on the account
                'Target_ID'            : record['TargetID'],             # An Internal ID for the Target (employee ID, etc.)
                
                                                                         # Initial assumption is that amounts are stored as
                                                                         # Decimals or Floats.
                                                                         # Must be converted to integer cents before
                                                                         # addition to file
                'Amount'               : int(((Decimal(record['Payment'])**2)**Decimal(0.5))*100)
                
            })

You can then access your NACHA file with, for instance:

    with open(_filename, 'w+') as output_file: output_file.write(repr(nacha_file))

Hopefully this will prove helpful to others!
