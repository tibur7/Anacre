import pandas as pd

class RecordRules():
    def __init__(self, df_dict: dict):
        self.df_dict = df_dict

    def CR001(self):
        #[Counterparty-instrument.Counterparty identifier] EXISTS IN {[Counterparty reference.Counterparty identifier]}
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        reference_identifiers = set(df_counterparty_reference["Counterparty identifier"])
        
        invalid_rows = df_counterparty_instrument[~df_counterparty_instrument["Counterparty identifier"].isin(reference_identifiers)]
        
        return "CR001", "Counterparty-reference", invalid_rows
    
    def CR002(self):
        #[Joint liabilities.Counterparty identifier] EXISTS IN {[Counterparty reference.Counterparty identifier]}
        df_joint_liabilities = self.df_dict["Joint liabilities"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        reference_identifiers = set(df_counterparty_reference["Counterparty identifier"])
        
        invalid_rows = df_joint_liabilities[~df_joint_liabilities["Counterparty identifier"].isin(reference_identifiers)]
        
        return "CR002", "Counterparty-reference", invalid_rows
    
    def CR003(self):
        #[Counterparty risk.Counterparty identifier] EXISTS IN {[Counterparty reference.Counterparty identifier]}
        df_counterparty_risk = self.df_dict["Counterparty risk"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        reference_identifiers = set(df_counterparty_reference["Counterparty identifier"])
        
        invalid_rows = df_counterparty_risk[~df_counterparty_risk["Counterparty identifier"].isin(reference_identifiers)]
        
        return "CR003", "Counterparty risk", invalid_rows    
    
    def CR004(self):
        #[Counterparty default.Counterparty identifier] EXISTS IN {[Counterparty reference.Counterparty identifier]}
        df_counterparty_default = self.df_dict["Counterparty default"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        reference_identifiers = set(df_counterparty_reference["Counterparty identifier"])
        
        invalid_rows = df_counterparty_default[~df_counterparty_default["Counterparty identifier"].isin(reference_identifiers)]
        
        return "CR004", "Counterparty default", invalid_rows
    
    def CR005(self):
        #[Protection received.Protection provider identifier] EXISTS IN {[Counterparty reference.Counterparty identifier]}
        df_protection_received = self.df_dict["Protection received"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        reference_identifiers = set(df_counterparty_reference["Counterparty identifier"])
        
        invalid_rows = df_protection_received[~df_protection_received["Protection provider identifier"].isin(reference_identifiers)]
        
        return "CR005", "Protection received", invalid_rows
    

    def CPC001(self):
        #[Counterparty-instrument.Counterparty role] = 'Creditor' => [Counterparty reference.Role 3 Creditor] = 'True'
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        # Merge the DataFrames on "Counterparty identifier"
        merged_df = pd.merge(
            df_counterparty_instrument,
            df_counterparty_reference,
            on="Counterparty identifier",
            how="left"
        )
        
        # Filter rows where "Counterparty role" is 'Creditor' and "Role 3 Creditor" is not 'True'
        invalid_rows = merged_df[
            (merged_df["Counterparty role"] == 'Creditor') &
            (merged_df["Role 3 Creditor"] != 'True')
        ]
        
        return "CPC001", "Counterparty-instrument", invalid_rows

    def CPC002(self):
        # IF [Counterparty-instrument.Counterparty role] = 'Debtor' THEN
        # [Counterparty reference.Role 4 Debtor - All instruments originated prior to 1 September 2018] = 'True'
        # OR [Counterparty reference.Role 4 Debtor - At least one instrument originated at or after 1 September 2018] = 'TRUE'
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        # Merge the DataFrames on "Counterparty identifier"
        merged_df = pd.merge(
            df_counterparty_instrument,
            df_counterparty_reference,
            on="Counterparty identifier",
            how="left"
        )
        
        # Filter rows where "Counterparty role" is 'Debtor' and the specified conditions are not met
        invalid_rows = merged_df[
            (merged_df["Counterparty role"] == 'Debtor') &
            ~(
                (merged_df["Role 4 Debtor - All instruments originated prior to 1 September 2018"] == 'True') |
                (merged_df["Role 4 Debtor - At least one instrument originated at or after 1 September 2018"] == 'TRUE')
            )
        ]
        
        return "CPC002", "Counterparty-instrument", invalid_rows

    def CPC003(self):
        #[Counterparty-instrument.Counterparty role] = 'Originator' => [Counterparty reference.Role 10 Originator] = 'True'
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        # Merge the DataFrames on "Counterparty identifier"
        merged_df = pd.merge(
            df_counterparty_instrument,
            df_counterparty_reference,
            on="Counterparty identifier",
            how="left"
        )
        
        # Filter rows where "Counterparty role" is 'Originator' and "Role 10 Originator" is not 'True'
        invalid_rows = merged_df[
            (merged_df["Counterparty role"] == 'Originator') &
            (merged_df["Role 10 Originator"] != 'True')
        ]
        
        return "CPC003", "Counterparty-instrument", invalid_rows

    def CPC004(self):
            #[Counterparty-instrument.Counterparty role] = 'Servicer' => [Counterparty reference.Role 11 Servicer] = 'True'
            df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
            df_counterparty_reference = self.df_dict["Counterparty-reference"]
            
            # Merge the DataFrames on "Counterparty identifier"
            merged_df = pd.merge(
                df_counterparty_instrument,
                df_counterparty_reference,
                on="Counterparty identifier",
                how="left"
            )
            
            # Filter rows where "Counterparty role" is 'Servicer' and "Role 11 Servicer" is not 'True'
            invalid_rows = merged_df[
                (merged_df["Counterparty role"] == 'Servicer') &
                (merged_df["Role 11 Servicer"] != 'True')
            ]
            
            return "CPC004", "Counterparty-instrument", invalid_rows

    def CPC005(self):
        #[Protection received.Protection provider identifier] NOT IN {'Not applicable', 'Not required'} => [Counterparty referece.Role 6 Protection provider] = 'True'
        df_protection_received = self.df_dict["Protection received"]
        df_counterparty_reference = self.df_dict["Counterparty-reference"]
        
        # Merge the DataFrames on "Counterparty identifier"
        merged_df = pd.merge(
            df_protection_received,
            df_counterparty_reference,
            left_on="Protection provider identifier",
            right_on="Counterparty identifier",
            how="left"
        )
        
        # Filter rows where "Protection provider identifier" is not in the specified values
        # and "Role 6 Protection provider" is not 'True'
        invalid_rows = merged_df[
            (~merged_df["Protection provider identifier"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Role 6 Protection provider"] != 'True')
        ]

        return "CPC005", "Protection received and Counterparty-reference", invalid_rows

    def CN0010(self):
        # 'Checks that if the value reported for attribute [Settlement date] is not equal to 'Non-applicable' {'NA'},
        # then the value reported for [Settlement date] should be greater than or equal to the value reported
        # for the attribute [Inception date].
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Settlement date" is not in the specified values and "Settlement date" is less than "Inception date"
        invalid_rows = df_instrument[
            (~df_instrument["Settlement date"].isin(['Not applicable', 'Not required'])) &
            (df_instrument["Settlement date"] < df_instrument["Inception date"])
        ]
        
        return "CN0010", "Instrument", invalid_rows
    

    def CN0030(self):
        # 'IF [Instrument.End date of interest-only period] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Instrument.End date of interest-only period] >= [Instrument.Inception date]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "End date of interest-only period" is not in the specified values
        # and "End date of interest-only period" is less than "Inception date"
        invalid_rows = df_instrument[
            (~df_instrument["End date of interest-only period"].isin(['Not applicable', 'Not required'])) &
            (df_instrument["End date of interest-only period"] < df_instrument["Inception date"])
        ]
        
        return "CN0030", "Instrument", invalid_rows
    
    def CN0040(self):
        # 'IF [Instrument.Legal final maturity date] NOT IN {‘Not applicable’, 'Not required'} AND
        # [Instrument.Settlement date] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Instrument.Legal final maturity date] >= [Instrument.Settlement date]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where both "Legal final maturity date" and "Settlement date" are not in the specified values
        # and "Legal final maturity date" is less than "Settlement date"
        invalid_rows = df_instrument[
            (~df_instrument["Legal final maturity date"].isin(['Not applicable', 'Not required'])) &
            (~df_instrument["Settlement date"].isin(['Not applicable', 'Not required'])) &
            (df_instrument["Legal final maturity date"] < df_instrument["Settlement date"])
        ]
        
        return "CN0040", "Instrument", invalid_rows
    
    def CN0050(self):
        # 'IF [Instrument.Legal final maturity date] NOT IN {‘Not applicable’, 'Not required'} AND
        # [Instrument.End date of interest-only period] NOT IN {‘Not applicable’, 'Not required'} THEN 
        # [Instrument.Legal final maturity date] >= [Instrument.End date of interest-only period]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where both "Legal final maturity date" and "End date of interest-only period" are not in the specified values
        # and "Legal final maturity date" is less than "End date of interest-only period"
        invalid_rows = df_instrument[
            (~df_instrument["Legal final maturity date"].isin(['Not applicable', 'Not required'])) &
            (~df_instrument["End date of interest-only period"].isin(['Not applicable', 'Not required'])) &
            (df_instrument["Legal final maturity date"] < df_instrument["End date of interest-only period"])
        ]
        
        return "CN0050", "Instrument", invalid_rows
    
   
    def CN0080(self):
        # 'IF [Financial.Next interest rate reset date] NOT IN {‘Not applicable’, 'Not required'} AND
        # [Instrument.Legal final maturity date] NOT IN {‘Not applicable’, 'Not required'} AND 
        # [Instrument.Legal final maturity date] > [Instrument.Reference date] THEN
        # [Instrument.Legal final maturity date] >= [Financial.Next interest rate reset date]'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Merge the "Instrument" and "Financial" DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            df_instrument,
            df_financial,
            on="Instrument identifier",
            how="left"
        )
        
        # Filter rows where the specified conditions are not met
        invalid_rows = merged_df[
            (~merged_df["Financial.Next interest rate reset date"].isin(['Not applicable', 'Not required'])) &
            (~merged_df["Instrument.Legal final maturity date"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Instrument.Legal final maturity date"] > merged_df["Instrument.Reference date"]) &
            (merged_df["Instrument.Legal final maturity date"] < merged_df["Financial.Next interest rate reset date"])
        ]
        
        return "CN0080", "Instrument and Financial", invalid_rows
    
    def CN0140(self):
        # '[Instrument.Reference date] >= [Instrument.Inception date]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Reference date" is less than "Inception date"
        invalid_rows = df_instrument[df_instrument["Reference date"] < df_instrument["Inception date"]]
        
        return "CN0140", "Instrument", invalid_rows

    def CN0141(self):
        # 'IF [Instrument.Settlement date] <> ‘Non-applicable’ THEN [Instrument.Reference date] >= [Instrument.Settlement date]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Settlement date" is not 'Non-applicable' and "Reference date" is less than "Settlement date"
        invalid_rows = df_instrument[
            (df_instrument["Settlement date"] != 'Non-applicable') &
            (df_instrument["Reference date"] < df_instrument["Settlement date"])
        ]
        
        return "CN0141", "Instrument", invalid_rows

    def CN0142(self):
        # '[Protection received. Date of protection value] >= [Protection received.Date of original protection value]'
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Filter rows where "Date of protection value" is less than "Date of original protection value"
        invalid_rows = df_protection_received[df_protection_received["Date of protection value"] < df_protection_received["Date of original protection value"]]
        
        return "CN0142", "Protection received", invalid_rows            

    
    def CN0150(self):
        # 'IF [Financial.Next interest rate reset date] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Next interest rate reset date] >= [Instrument.Inception date]'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Merge the "Instrument" and "Financial" DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            df_instrument,
            df_financial,
            on="Instrument identifier",
            how="left"
        )
        
        # Filter rows where "Next interest rate reset date" is not in the specified values
        # and "Next interest rate reset date" is less than "Inception date"
        invalid_rows = merged_df[
            (~merged_df["Financial.Next interest rate reset date"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Financial.Next interest rate reset date"] < merged_df["Instrument.Inception date"])
        ]
        
        return "CN0150", "Instrument and Financial", invalid_rows
    
    def CN0160(self):
        # 'IF [Financial.Date of the default status of the instrument] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Date of the default status of the instrument] >= [Instrument.Inception date]'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Merge the "Instrument" and "Financial" DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            df_instrument,
            df_financial,
            on="Instrument identifier",
            how="left"
        )
        
        # Filter rows where "Date of the default status of the instrument" is not in the specified values
        # and "Date of the default status of the instrument" is less than "Inception date"
        invalid_rows = merged_df[
            (~merged_df["Financial.Date of the default status of the instrument"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Financial.Date of the default status of the instrument"] < merged_df["Instrument.Inception date"])
        ]
        
        return "CN0160", "Instrument and Financial", invalid_rows

    def CN0170(self):
        # 'IF [Financial.Date of past due for the instrument] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Date of past due for the instrument] >= [Instrument.Inception date]'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Merge the "Instrument" and "Financial" DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            df_instrument,
            df_financial,
            on="Instrument identifier",
            how="left"
        )
        
        # Filter rows where "Date of past due for the instrument" is not in the specified values
        # and "Date of past due for the instrument" is less than "Inception date"
        invalid_rows = merged_df[
            (~merged_df["Financial.Date of past due for the instrument"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Financial.Date of past due for the instrument"] < merged_df["Instrument.Inception date"])
        ]
        
        return "CN0170", "Instrument and Financial", invalid_rows

    def CN0200(self):
        # 'IF [Financial.Next interest rate reset date] NOT IN {‘Not applicable’, 'Not required'} AND
        # [Instrument.Settlement date] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Next interest reset date] >= [Instrument.Settlement date]'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Merge the "Instrument" and "Financial" DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            df_instrument,
            df_financial,
            on="Instrument identifier",
            how="left"
        )
        
        # Filter rows where "Next interest rate reset date" is not in the specified values
        # and "Settlement date" is not in the specified values
        # and "Next interest rate reset date" is less than "Settlement date"
        invalid_rows = merged_df[
            (~merged_df["Financial.Next interest rate reset date"].isin(['Not applicable', 'Not required'])) &
            (~merged_df["Instrument.Settlement date"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Financial.Next interest rate reset date"] < merged_df["Instrument.Settlement date"])
        ]
        
        return "CN0200", "Instrument and Financial", invalid_rows

    def CN0210(self):
        # 'IF [Financial.Next interest rate reset date] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Next interest rate reset date] >= [Financial.Reference date]'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Next interest rate reset date" is not in the specified values
        # and "Next interest rate reset date" is less than "Reference date"
        invalid_rows = df_financial[
            (~df_financial["Financial.Next interest rate reset date"].isin(['Not applicable', 'Not required'])) &
            (df_financial["Financial.Next interest rate reset date"] < df_financial["Financial.Reference date"])
        ]
        
        return "CN0210", "Financial", invalid_rows

    def CN0220(self):
        # 'IF [Instrument.End date of interest-only period] NOT IN {‘Not applicable’, 'Not required'} AND
        # [Instrument.Settlement date] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Instrument.End date of interest-only period] >= [Instrument.Settlement date]'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "End date of interest-only period" is not in the specified values
        # and "Settlement date" is not in the specified values
        # and "End date of interest-only period" is less than "Settlement date"
        invalid_rows = df_instrument[
            (~df_instrument["Instrument.End date of interest-only period"].isin(['Not applicable', 'Not required'])) &
            (~df_instrument["Instrument.Settlement date"].isin(['Not applicable', 'Not required'])) &
            (df_instrument["Instrument.End date of interest-only period"] < df_instrument["Instrument.Settlement date"])
        ]
        
        return "CN0220", "Instrument", invalid_rows

    def CN0230(self):
        # 'IF [Financial.Type of securitisation]='Synthetic securitisation' THEN EXISTS protection item such that
        # [Protection received.Type of protection] IN {'Credit derivatives', 'Financial guarantees other than credit derivatives',
        # 'Currency and deposits', 'Securities'}'
        
        df_financial = self.df_dict["Financial"]
        df_protection_received = self.df_dict["Protection received"]
        
        # Filter rows where "Type of securitisation" is 'Synthetic securitisation'
        synthetic_securitisation = df_financial[df_financial["Financial.Type of securitisation"] == 'Synthetic securitisation']
        
        # Filter protection received items where "Type of protection" is in the specified values
        valid_protection_items = df_protection_received[
            df_protection_received["Protection received.Type of protection"].isin([
                'Credit derivatives',
                'Financial guarantees other than credit derivatives',
                'Currency and deposits',
                'Securities'
            ])
        ]
        
        # Merge the synthetic securitisation and valid protection items DataFrames on the common key "Instrument identifier"
        merged_df = pd.merge(
            synthetic_securitisation,
            valid_protection_items,
            on="Instrument identifier",
            how="inner"
        )
        
        # If there are any rows in the merged DataFrame, the condition is met
        if not merged_df.empty:
            return "CN0230", "Financial and Protection received", merged_df
        else:
            return "CN0230", "Financial and Protection received", pd.DataFrame(columns=df_financial.columns)  # Empty DataFrame
        
    def CN0240(self):
        # 'IF [Financial.Date of the default status of the instrument] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Reference date] >= [Financial.Date of the default status of the instrument]'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Date of the default status of the instrument" is not in the specified values
        # and "Reference date" is less than "Date of the default status of the instrument"
        invalid_rows = df_financial[
            (~df_financial["Financial.Date of the default status of the instrument"].isin(['Not applicable', 'Not required'])) &
            (df_financial["Financial.Reference date"] < df_financial["Financial.Date of the default status of the instrument"])
        ]
        
        return "CN0240", "Financial", invalid_rows    

    def CN0250(self):
        # 'IF [Financial.Date of past due for the instrument] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Reference date] >= [Financial.Date of past due for the instrument]'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Date of past due for the instrument" is not in the specified values
        # and "Reference date" is less than "Date of past due for the instrument"
        invalid_rows = df_financial[
            (~df_financial["Financial.Date of past due for the instrument"].isin(['Not applicable', 'Not required'])) &
            (df_financial["Financial.Reference date"] < df_financial["Financial.Date of past due for the instrument"])
        ]
        
        return "CN0250", "Financial", invalid_rows

    def CN0270A(self):
        # 'IF [Financial.Date of past due for the instrument] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Financial.Arrears for the instrument] > 0'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Date of past due for the instrument" is not in the specified values
        # and "Arrears for the instrument" is not greater than 0
        invalid_rows = df_financial[
            (~df_financial["Financial.Date of past due for the instrument"].isin(['Not applicable', 'Not required'])) &
            (df_financial["Financial.Arrears for the instrument"] <= 0)
        ]
        
        return "CN0270A", "Financial", invalid_rows
    
    def CN0270B(self):
        # 'IF [Financial.Arrears for the instrument] > 0 THEN
        # [Financial.Date of past due for the instrument] NOT IN {‘Not applicable’, 'Not required'}'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Arrears for the instrument" is greater than 0
        # and "Date of past due for the instrument" is in the specified values
        invalid_rows = df_financial[
            (df_financial["Financial.Arrears for the instrument"] > 0) &
            (df_financial["Financial.Date of past due for the instrument"].isin(['Not applicable', 'Not required']))
        ]
        
        return "CN0270B", "Financial", invalid_rows
# Example usage
# Assuming you have your dataframes ready
# df_counterparty_instrument = ...
# df_counterparty_reference = ...

# Store the dataframes in a dictionary
df_dict = {
    "Counterparty-instrument": df_counterparty_instrument,
    "Counterparty-reference": df_counterparty_reference
}

# Create an instance of RecordRules
record_rules = RecordRules(df_dict)

# Perform the validation check CR001
rule_code, reference_name, invalid_rows = record_rules.CR001()

# Display the results
print("Rule Code:", rule_code)
print("Reference Name:", reference_name)
print("Invalid rows:")
print(invalid_rows)

