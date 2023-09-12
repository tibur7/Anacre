import pandas as pd

class DataValidator():
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.df_dict = self.load_data()

    def load_data(self):
        # Implement your data loading logic here
        # Read the dataset into a dictionary of dataframes
        # Example:
        df_dict = {}
        df_dict["Counterparty-instrument"] = pd.read_csv("counterparty_instrument.csv")
        df_dict["Counterparty-reference"] = pd.read_csv("counterparty_reference.csv")
        # Load other tables as needed
        return df_dict

    def apply_validation_rules(self):
        validation_rules = RecordRules(self.df_dict)  # Create an instance of your validation class
        validation_results = {}

        # Apply each validation rule
        for rule_name in dir(validation_rules):
            if callable(getattr(validation_rules, rule_name)) and rule_name.startswith("CR"):  # Adjust as needed for other rule prefixes
                rule_function = getattr(validation_rules, rule_name)
                rule_id, table_name, invalid_rows = rule_function()

                # Create a column "Correct" indicating whether each row is valid (True) or not (False)
                invalid_rows["Correct"] = False
                valid_rows = self.df_dict[table_name][~self.df_dict[table_name].index.isin(invalid_rows.index)]
                valid_rows["Correct"] = True

                # Combine valid and invalid rows
                combined_df = pd.concat([valid_rows, invalid_rows])

                # Store the results in the dictionary
                validation_results[rule_id] = combined_df

        return validation_results

    def generate_report(self, validation_results):
        # Implement your report generation logic here
        # You can save the results as an Excel file, CSV, or any other format
        # Example:
        writer = pd.ExcelWriter("validation_report.xlsx")
        for rule_id, df in validation_results.items():
            df.to_excel(writer, sheet_name=rule_id, index=False)
        writer.save()

if __name__ == "__main__":
    validator = DataValidator("your_dataset_path.csv")
    validation_results = validator.apply_validation_rules()
    validator.generate_report(validation_results)

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
    
    def CN0290(self):
        # 'Let T be the reference date,
        # IF [Financial.Default status of the instrument] (T) <> [Financial.Default status of the instrument] (T - 1)
        # THEN [Financial.Date of default status of the instrument] (T) > [Financial.Date of default status of the instrument] (T - 1)'
        
        df_financial = self.df_dict["Financial"]
        
        # Sort the DataFrame by "Instrument identifier" and "Financial.Reference date" to prepare for comparison
        df_financial_sorted = df_financial.sort_values(by=["Instrument identifier", "Financial.Reference date"])
        
        # Create a new DataFrame that shifts the "Financial.Default status of the instrument" and "Financial.Date of default status of the instrument" columns by 1 row for comparison
        shifted_df = df_financial_sorted.groupby("Instrument identifier")[["Financial.Default status of the instrument", "Financial.Date of default status of the instrument"]].shift(1)
        
        # Filter rows where the current "Default status of the instrument" is different from the previous
        # and where the current "Date of default status of the instrument" is not greater than the previous
        invalid_rows = df_financial_sorted[
            (df_financial_sorted["Financial.Default status of the instrument"] != shifted_df["Financial.Default status of the instrument"]) &
            ~(df_financial_sorted["Financial.Date of default status of the instrument"] > shifted_df["Financial.Date of default status of the instrument"])
        ]
        
        return "CN0290", "Financial", invalid_rows

    
    def CN0620(self):
        # 'LET [Counterparty reference.Counterparty identifier] = X.
        # IF [Counterparty reference.Institutional sector] ='Financial vehicle corporations (FVCs) engaged in securitisation transactions' 
        # AND [Financial.Type of securitisation] = ‘Traditional securitisation’
        # WHERE [Counterparty reference.Counterparty identifier] = X 
        # AND [Counterparty-instrument.Counterparty role](X) = 'Creditor', 
        # THEN EXISTS [Counterparty-instrument.Counterparty role] = 'Originator'
        
        df_counterparty_reference = self.df_dict["Counterparty reference"]
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        
        # Define X as a Counterparty identifier (you can replace X with the specific identifier you want to check)
        X = 'Your_Counterparty_Identifier'
        
        # Check if the specified conditions are met
        condition = (
            (df_counterparty_reference["Counterparty identifier"] == X) &
            (df_counterparty_reference["Institutional sector"] == 'Financial vehicle corporations (FVCs) engaged in securitisation transactions') &
            (df_counterparty_reference["Counterparty identifier"] == X) &
            (df_counterparty_instrument["Counterparty role"] == 'Creditor') &
            (df_counterparty_reference["Counterparty identifier"] == df_counterparty_instrument["Counterparty identifier"]) &
            (df_counterparty_reference["Counterparty identifier"] == X) &
            (df_counterparty_reference["Financial.Type of securitisation"] == 'Traditional securitisation')
        )
        
        # If the conditions are met, check for the existence of 'Originator' role
        if condition.any():
            exists_originator = df_counterparty_instrument[
                (df_counterparty_instrument["Counterparty role"] == 'Originator') &
                (df_counterparty_instrument["Counterparty identifier"] == X)
            ]
            
            # If 'Originator' exists, return the result, otherwise, return an empty DataFrame
            if not exists_originator.empty:
                return "CN0620", "Counterparty-instrument", exists_originator
            else:
                return "CN0620", "Counterparty-instrument", pd.DataFrame(columns=df_counterparty_instrument.columns)
        
        # If the conditions are not met, return an empty DataFrame
        return "CN0620", "Counterparty-instrument", pd.DataFrame(columns=df_counterparty_instrument.columns)    


    def CN0621(self):
        # 'Let A := {[Counterparty-instrument.Counterparty role]} for 
        # ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],
        # [Counterparty-instrument.Instrument identifier],[Counterparty-instrument.Counterparty identifier]).
        # Then, 'Creditor' IN A IF AND ONLY IF 'Debtor' NOT IN A'
        
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        
        # Create a DataFrame 'A' that contains the unique combinations of columns
        # ([Observed agent identifier], [Contract identifier], [Instrument identifier], [Counterparty identifier]) 
        # along with the set of Counterparty roles for each combination.
        A = df_counterparty_instrument.groupby(
            ["Observed agent identifier", "Contract identifier", "Instrument identifier", "Counterparty identifier"]
        )["Counterparty role"].unique().reset_index()
        
        # Check if 'Creditor' is in 'A' and 'Debtor' is not in 'A' for each unique combination
        condition = A.apply(lambda row: ('Creditor' in row["Counterparty role"]) == ('Debtor' not in row["Counterparty role"]), axis=1)
        
        # Filter the rows that satisfy the condition
        valid_rows = A[condition]
        
        return "CN0621", "Counterparty-instrument", valid_rows


    
    def CN0622(self):
        # '[Protection received.Protection provider identifier] DOES NOT EXIST IN 
        # {[Counterparty-instrument.Counterparty identifier] GIVEN THAT 
        # ([Instrument-Protection received.Observed agent identifier],[Instrument-Protection received.Contract identifier],
        # [Instrument-Protection received.Instrument identifier]) = 
        # ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],
        # [Counterparty-instrument.Instrument identifier]) AND [Counterparty-instrument.Counterparty role] = ‘Creditor’ }'
        
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_protection_received = self.df_dict["Protection received"]
        df_instrument_protection_received = self.df_dict["Instrument-Protection received"]
        
        # Merge the "Counterparty-instrument" and "Protection received" DataFrames on the common key
        merged_df = pd.merge(
            df_counterparty_instrument[df_counterparty_instrument["Counterparty role"] == 'Creditor'],
            df_protection_received,
            left_on=["Observed agent identifier", "Contract identifier", "Instrument identifier"],
            right_on=["Observed agent identifier", "Contract identifier", "Instrument identifier"],
            how="inner"
        )
        
        # Extract the set of "Counterparty identifier" from the merged DataFrame
        existing_protection_providers = set(merged_df["Counterparty identifier_x"])
        
        # Get the set of all "Counterparty identifier" from "Counterparty-instrument"
        all_counterparty_identifiers = set(df_counterparty_instrument["Counterparty identifier"])
        
        # Calculate the set of "Counterparty identifier" that do not exist in the existing_protection_providers set
        invalid_protection_providers = all_counterparty_identifiers.difference(existing_protection_providers)
        
        # Create a DataFrame to store the invalid protection providers
        invalid_protection_providers_df = pd.DataFrame({"Counterparty identifier": list(invalid_protection_providers)})
        
        return "CN0622", "Counterparty-instrument", invalid_protection_providers_df
    
    def CN0630(self):
        # 'IF [Counterparty default.Date of the default status of the counterparty] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Counterparty default.Reference date] >= [Counterparty default.Date of the default status of the counterparty]'
        
        df_counterparty_default = self.df_dict["Counterparty default"]
        
        # Filter rows where "Date of the default status of the counterparty" is not in the specified values
        # and "Reference date" is less than "Date of the default status of the counterparty"
        invalid_rows = df_counterparty_default[
            (~df_counterparty_default["Counterparty default.Date of the default status of the counterparty"].isin(['Not applicable', 'Not required'])) &
            (df_counterparty_default["Counterparty default.Reference date"] < df_counterparty_default["Counterparty default.Date of the default status of the counterparty"])
        ]
        
        return "CN0630", "Counterparty default", invalid_rows

    def CN0640(self):
        # 'Let T be the reference date
        # IF [Counterparty default.Default status of the counterparty] (T) <>
        # [Counterparty default.Default status of the counterparty] (T - 1) THEN
        # [Counterparty default.Date of the default status of the counterparty] (T) >
        # [Counterparty default.Date of the default status of the counterparty] (T - 1)'
        
        df_counterparty_default = self.df_dict["Counterparty default"]
        
        # Sort the DataFrame by "Counterparty identifier" and "Counterparty default.Reference date" to prepare for comparison
        df_counterparty_default_sorted = df_counterparty_default.sort_values(by=["Counterparty identifier", "Counterparty default.Reference date"])
        
        # Create a new DataFrame that shifts the "Counterparty default.Default status of the counterparty" and "Counterparty default.Date of the default status of the counterparty" columns by 1 row for comparison
        shifted_df = df_counterparty_default_sorted.groupby("Counterparty identifier")[["Counterparty default.Default status of the counterparty", "Counterparty default.Date of the default status of the counterparty"]].shift(1)
        
        # Filter rows where the current "Default status of the counterparty" is different from the previous
        # and where the current "Date of the default status of the counterparty" is not greater than the previous
        invalid_rows = df_counterparty_default_sorted[
            (df_counterparty_default_sorted["Counterparty default.Default status of the counterparty"] != shifted_df["Counterparty default.Default status of the counterparty"]) &
            ~(df_counterparty_default_sorted["Counterparty default.Date of the default status of the counterparty"] > shifted_df["Counterparty default.Date of the default status of the counterparty"])
        ]
        
        return "CN0640", "Counterparty default", invalid_rows
    
    def CN0650(self):
        # 'IF [Protection received.Maturity date of the protection] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Protection received.Maturity date of the protection] >= [Instrument.Inception date]'
        
        df_protection_received = self.df_dict["Protection received"]
        df_instrument = self.df_dict["Instrument"]
        
        # Merge the "Protection received" and "Instrument" DataFrames on the common key
        merged_df = pd.merge(
            df_protection_received,
            df_instrument,
            left_on=["Observed agent identifier", "Contract identifier", "Instrument identifier"],
            right_on=["Observed agent identifier", "Contract identifier", "Instrument identifier"],
            how="inner"
        )
        
        # Filter rows where "Maturity date of the protection" is not in the specified values
        # and "Maturity date of the protection" is less than "Inception date"
        invalid_rows = merged_df[
            (~merged_df["Protection received.Maturity date of the protection"].isin(['Not applicable', 'Not required'])) &
            (merged_df["Protection received.Maturity date of the protection"] < merged_df["Instrument.Inception date"])
        ]
        
        return "CN0650", "Protection received", invalid_rows
    
    def CN0660(self):
        # 'IF [Protection received.Date of protection value] NOT IN {‘Not applicable’, 'Not required'} THEN
        # [Protection received.Reference date] >= [Protection received.Date of protection value]'
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Filter rows where "Date of protection value" is not in the specified values
        # and "Reference date" is less than "Date of protection value"
        invalid_rows = df_protection_received[
            (~df_protection_received["Protection received.Date of protection value"].isin(['Not applicable', 'Not required'])) &
            (df_protection_received["Protection received.Reference date"] < df_protection_received["Protection received.Date of protection value"])
        ]
        
        return "CN0660", "Protection received", invalid_rows

    def CN0661(self):
        # '[Protection received.Date of protection value](T) >= [Protection received.Date of protection value](T-1)'
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Sort the DataFrame by "Protection received.Date of protection value" and "Protection received.Reference date" to prepare for comparison
        df_protection_received_sorted = df_protection_received.sort_values(by=["Protection received.Reference date", "Protection received.Date of protection value"])
        
        # Create a new DataFrame that shifts the "Protection received.Date of protection value" column by 1 row for comparison
        shifted_df = df_protection_received_sorted.groupby("Protection received.Reference date")["Protection received.Date of protection value"].shift(1)
        
        # Filter rows where the current "Date of protection value" is not greater than or equal to the previous
        invalid_rows = df_protection_received_sorted[
            ~(df_protection_received_sorted["Protection received.Date of protection value"] >= shifted_df)
        ]
        return "CN0661", "Protection received", invalid_rows  

    def CN0701(self):
        # 'IF [Financial.Transferred amount] > 0 THEN [Financial.Outstanding nominal amount] >= [Financial.Transferred amount]'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Transferred amount" is greater than 0 and "Outstanding nominal amount" is less than "Transferred amount"
        invalid_rows = df_financial[
            (df_financial["Financial.Transferred amount"] > 0) &
            (df_financial["Financial.Outstanding nominal amount"] < df_financial["Financial.Transferred amount"])
        ]
        
        return "CN0701", "Financial", invalid_rows    

    def CN0704(self):
        # '[Financial.Outstanding nominal amount] >= [Financial.Arrears for the instrument]'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Outstanding nominal amount" is less than "Arrears for the instrument"
        invalid_rows = df_financial[df_financial["Financial.Outstanding nominal amount"] < df_financial["Financial.Arrears for the instrument"]]
        
        return "CN0704", "Financial", invalid_rows

    def CN0705(self):
        # 'IF [Instrument.Commitment amount at inception] <> 'Non-applicable' THEN [Instrument.Commitment amount at inception] > 0'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Commitment amount at inception" is not 'Non-applicable' and not greater than 0
        invalid_rows = df_instrument[
            (df_instrument["Instrument.Commitment amount at inception"] != 'Non-applicable') &
            (df_instrument["Instrument.Commitment amount at inception"] <= 0)
        ]
        
        return "CN0705", "Instrument", invalid_rows

    def CN0804(self):
        # 'Let T be the reference date:  
        # [Instrument.Commitment amount at inception]  (T) = [Instrument.Commitment amount at inception] (T-1)'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Sort the DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Create a new DataFrame that shifts the "Commitment amount at inception" column by 1 row for comparison
        shifted_df = df_instrument_sorted.groupby("Instrument.Identifier")["Instrument.Commitment amount at inception"].shift(1)
        
        # Filter rows where the current "Commitment amount at inception" is not equal to the previous
        invalid_rows = df_instrument_sorted[
            df_instrument_sorted["Instrument.Commitment amount at inception"] != shifted_df
        ]
        
        return "CN0804", "Instrument", invalid_rows

    def CN0805(self):
        # 'Let T be the reference date and T' the end of quarter reference date such that T'>=T:
        # For each T IN{T', T'-1, T'-2}, IF [Instrument.Project finance loan]  (T) <> [Instrument.Project finance loan]  (T-1) 
        # THEN [Accounting.Date of the forbearance and renegotiation status] (T') > (T-1)'
        
        df_instrument = self.df_dict["Instrument"]
        df_accounting = self.df_dict["Accounting"]
        
        # Sort the "Instrument" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Project finance loan" column by 1 row for comparison
        shifted_df = grouped_df["Instrument.Project finance loan"].shift(1)
        
        # Define the end of quarter reference date T'
        end_of_quarter_reference_date = grouped_df["Instrument.Reference date"].max()
        
        # Filter rows where the current "Project finance loan" is different from the previous for T, T-1, T-2
        invalid_rows = df_instrument_sorted[
            (df_instrument_sorted["Instrument.Reference date"].isin([end_of_quarter_reference_date, end_of_quarter_reference_date - pd.DateOffset(1), end_of_quarter_reference_date - pd.DateOffset(2)])) &
            (df_instrument_sorted["Instrument.Project finance loan"] != shifted_df)
        ]
        
        # Filter rows where the "Date of the forbearance and renegotiation status" (T') is not greater than (T-1)
        invalid_rows = invalid_rows[invalid_rows["Accounting.Date of the forbearance and renegotiation status"] <= invalid_rows["Instrument.Reference date"] - pd.DateOffset(1)]
        
        return "CN0805", "Instrument", invalid_rows
    

    
    def CN0806(self):
        # 'Let T be the reference date and T' the end of quarter reference date such that T'>=T:
        # For each T IN {T’, T’-1, T’-2}, IF [Instrument.Purpose] (T) <> [Instrument.Purpose] (T-1)
        # THEN [Accounting.Date of the forbearance and renegotiation status] (T') > (T-1)'
        
        df_instrument = self.df_dict["Instrument"]
        df_accounting = self.df_dict["Accounting"]
        
        # Sort the "Instrument" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Purpose" column by 1 row for comparison
        shifted_df = grouped_df["Instrument.Purpose"].shift(1)
        
        # Define the end of quarter reference date T'
        end_of_quarter_reference_date = grouped_df["Instrument.Reference date"].max()
        
        # Filter rows where the current "Purpose" is different from the previous for T, T-1, T-2
        invalid_rows = df_instrument_sorted[
            (df_instrument_sorted["Instrument.Reference date"].isin([end_of_quarter_reference_date, end_of_quarter_reference_date - pd.DateOffset(1), end_of_quarter_reference_date - pd.DateOffset(2)])) &
            (df_instrument_sorted["Instrument.Purpose"] != shifted_df)
        ]
        
        # Filter rows where the "Date of the forbearance and renegotiation status" (T') is not greater than (T-1)
        invalid_rows = invalid_rows[invalid_rows["Accounting.Date of the forbearance and renegotiation status"] <= invalid_rows["Instrument.Reference date"] - pd.DateOffset(1)]
        
        return "CN0806", "Instrument", invalid_rows
    
    def CN0807(self):
        # 'Let T be the reference date and T' the end of quarter reference date such that T'>=T:
        # For each T IN{T', T'-1, T'-2}, IF [Instrument.Recourse]  (T) <> [Instrument.Recourse] (T-1)
        # THEN [Accounting.Date of the forbearance and renegotiation status] (T') > (T-1) '
        
        df_instrument = self.df_dict["Instrument"]
        df_accounting = self.df_dict["Accounting"]
        
        # Sort the "Instrument" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Recourse" column by 1 row for comparison
        shifted_df = grouped_df["Instrument.Recourse"].shift(1)
        
        # Define the end of quarter reference date T'
        end_of_quarter_reference_date = grouped_df["Instrument.Reference date"].max()
        
        # Filter rows where the current "Recourse" is different from the previous for T, T-1, T-2
        invalid_rows = df_instrument_sorted[
            (df_instrument_sorted["Instrument.Reference date"].isin([end_of_quarter_reference_date, end_of_quarter_reference_date - pd.DateOffset(1), end_of_quarter_reference_date - pd.DateOffset(2)])) &
            (df_instrument_sorted["Instrument.Recourse"] != shifted_df)
        ]
        
        # Filter rows where the "Date of the forbearance and renegotiation status" (T') is not greater than (T-1)
        invalid_rows = invalid_rows[invalid_rows["Accounting.Date of the forbearance and renegotiation status"] <= invalid_rows["Instrument.Reference date"] - pd.DateOffset(1)]
        
        return "CN0807", "Instrument", invalid_rows
    
    
    def CN0809(self):
        # 'Let T be the reference date and T' the end of quarter reference date such that T'>=T:
        # For each T IN{T', T'-1, T'-2}, IF [Instrument.Repayment rights]  (T) <> [Instrument.Repayment rights] (T-1) 
        # THEN [Accounting.Date of the forbearance and renegotiation status] (T') > (T-1) '
        
        df_instrument = self.df_dict["Instrument"]
        df_accounting = self.df_dict["Accounting"]
        
        # Sort the "Instrument" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Repayment rights" column by 1 row for comparison
        shifted_df = grouped_df["Instrument.Repayment rights"].shift(1)
        
        # Define the end of quarter reference date T'
        end_of_quarter_reference_date = grouped_df["Instrument.Reference date"].max()
        
        # Filter rows where the current "Repayment rights" is different from the previous for T, T-1, T-2
        invalid_rows = df_instrument_sorted[
            (df_instrument_sorted["Instrument.Reference date"].isin([end_of_quarter_reference_date, end_of_quarter_reference_date - pd.DateOffset(1), end_of_quarter_reference_date - pd.DateOffset(2)])) &
            (df_instrument_sorted["Instrument.Repayment rights"] != shifted_df)
        ]
        
        # Filter rows where the "Date of the forbearance and renegotiation status" (T') is not greater than (T-1)
        invalid_rows = invalid_rows[invalid_rows["Accounting.Date of the forbearance and renegotiation status"] <= invalid_rows["Instrument.Reference date"] - pd.DateOffset(1)]
        
        return "CN0809", "Instrument", invalid_rows
    
    def CN0810(self):
        # 'Let T be the reference date:
        # [Instrument.Fair value changes due to changes in credit risk before purchase]  (T) = [Instrument.Fair value changes due to changes in credit risk before purchase] (T-1)'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Sort the "Instrument" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_sorted = df_instrument.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Fair value changes due to changes in credit risk before purchase" column by 1 row for comparison
        shifted_df = grouped_df["Instrument.Fair value changes due to changes in credit risk before purchase"].shift(1)
        
        # Filter rows where the current "Fair value changes due to changes in credit risk before purchase" is not equal to the previous
        invalid_rows = df_instrument_sorted[df_instrument_sorted["Instrument.Fair value changes due to changes in credit risk before purchase"] != shifted_df]
        
        return "CN0810", "Instrument", invalid_rows    

    
    def CN0812(self):
        # 'Let T be the reference date:
        # IF [Instrument-protection received.Instrument ID] (T) IN [Instrument-protection received.Instrument ID] (T-1) THEN
        # [Protection received.Original protection value]  (T) = [Protection received.Original protection value] (T-1)'
        
        df_instrument_protection_received = self.df_dict["Instrument-protection received"]
        df_protection_received = self.df_dict["Protection received"]
        
        # Sort the "Instrument-protection received" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_protection_received_sorted = df_instrument_protection_received.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument-protection received" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_protection_received_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Instrument ID" column by 1 row for comparison
        shifted_df = grouped_df["Instrument-protection received.Instrument ID"].shift(1)
        
        # Filter rows where the current "Instrument ID" is the same as the previous for T and T-1
        matching_ids = df_instrument_protection_received_sorted["Instrument-protection received.Instrument ID"] == shifted_df
        invalid_rows = df_protection_received[matching_ids]
        
        # Filter rows where the "Original protection value" (T) is not equal to (T-1)
        invalid_rows = invalid_rows[invalid_rows["Protection received.Original protection value"] != invalid_rows["Protection received.Original protection value"].shift(1)]
        
        return "CN0812", "Protection received", invalid_rows
    
    def CN0813(self):
        # 'Let T be the reference date:
        # IF [Instrument-protection received.Instrument ID] (T) IN [Instrument-protection received.Instrument ID] (T-1) THEN
        # [Protection received.Date of original protection value]  (T) = [Protection received.Date of original protection value] (T-1)'
        
        df_instrument_protection_received = self.df_dict["Instrument-protection received"]
        df_protection_received = self.df_dict["Protection received"]
        
        # Sort the "Instrument-protection received" DataFrame by "Instrument.Reference date" to prepare for comparison
        df_instrument_protection_received_sorted = df_instrument_protection_received.sort_values(by=["Instrument.Reference date"])
        
        # Group the "Instrument-protection received" DataFrame by "Instrument.Identifier" for efficient processing
        grouped_df = df_instrument_protection_received_sorted.groupby("Instrument.Identifier")
        
        # Create a new DataFrame that shifts the "Instrument ID" column by 1 row for comparison
        shifted_df = grouped_df["Instrument-protection received.Instrument ID"].shift(1)
        
        # Filter rows where the current "Instrument ID" is the same as the previous for T and T-1
        matching_ids = df_instrument_protection_received_sorted["Instrument-protection received.Instrument ID"] == shifted_df
        invalid_rows = df_protection_received[matching_ids]
        
        # Filter rows where the "Date of original protection value" (T) is not equal to (T-1)
        invalid_rows = invalid_rows[invalid_rows["Protection received.Date of original protection value"] != invalid_rows["Protection received.Date of original protection value"].shift(1)]
        
        return "CN0813", "Protection received", invalid_rows
    
    def CN0814(self):
        # 'IF [Instrument.Settlement date] = 'Non-applicable' THEN [Financial.Off-balance sheet amount] > 0'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Settlement date" is 'Non-applicable'
        non_applicable_settlement = df_instrument["Instrument.Settlement date"] == 'Non-applicable'
        
        # Filter rows where "Off-balance sheet amount" is not greater than 0
        invalid_rows = df_financial[(non_applicable_settlement) & (df_financial["Financial.Off-balance sheet amount"] <= 0)]
        
        return "CN0814", "Financial", invalid_rows
    
    def CN0816(self):
        # 'IF [Counterparty default.Date of the default status of the counterparty] = 'Non-applicable' AND
        # [Counterparty default.Default status of the counterparty] <> 'Non-applicable' THEN
        # [Counterparty default.Default status of the counterparty] = 'Not in default'
        
        df_counterparty_default = self.df_dict["Counterparty default"]
        
        # Filter rows where "Date of the default status of the counterparty" is 'Non-applicable'
        non_applicable_date = df_counterparty_default["Counterparty default.Date of the default status of the counterparty"] == 'Non-applicable'
        
        # Filter rows where "Default status of the counterparty" is not 'Non-applicable'
        not_non_applicable_status = df_counterparty_default["Counterparty default.Default status of the counterparty"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met and "Default status of the counterparty" is not 'Not in default'
        invalid_rows = df_counterparty_default[(non_applicable_date) & (not_non_applicable_status) & (df_counterparty_default["Counterparty default.Default status of the counterparty"] != 'Not in default')]
        
        return "CN0816", "Counterparty default", invalid_rows
    
    def CN0821(self):
        # 'IF [Instrument.Type of instrument] = 'Reverse repurchase agreements' THEN [Financial.Off-balance sheet amount] = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Type of instrument" is 'Reverse repurchase agreements'
        reverse_repurchase = df_instrument["Instrument.Type of instrument"] == 'Reverse repurchase agreements'
        
        # Filter rows where "Off-balance sheet amount" is not 'Non-applicable'
        non_applicable_off_balance = df_financial["Financial.Off-balance sheet amount"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_financial[(reverse_repurchase) & (non_applicable_off_balance)]
        
        return "CN0821", "Financial", invalid_rows  

    def CN0833(self):
        # '[Financial.Default status of the instrument] <> {'Non-applicable'} IF AND ONLY IF
        # [Financial.Date of the Default status of the instrument] <> 'Non-applicable'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Default status of the instrument" is not 'Non-applicable'
        not_non_applicable_status = df_financial["Financial.Default status of the instrument"] != 'Non-applicable'
        
        # Filter rows where "Date of the Default status of the instrument" is 'Non-applicable'
        non_applicable_date = df_financial["Financial.Date of the Default status of the instrument"] == 'Non-applicable'
        
        # Check if the condition is met for one and not the other or vice versa
        invalid_rows = df_financial[(not_non_applicable_status & non_applicable_date) | (~not_non_applicable_status & ~non_applicable_date)]
        
        return "CN0833", "Financial", invalid_rows
    
    def CN0835(self):
        # 'IF [Instrument.Amortisation type] IN {'French', 'Fixed amortisation schedule'} THEN
        # [Instrument.End date of interest-only period]  = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Amortisation type" is in {'French', 'Fixed amortisation schedule'}
        valid_amortisation_types = df_instrument["Instrument.Amortisation type"].isin(['French', 'Fixed amortisation schedule'])
        
        # Filter rows where "End date of interest-only period" is not 'Non-applicable'
        non_applicable_end_date = df_instrument["Instrument.End date of interest-only period"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[(valid_amortisation_types) & (non_applicable_end_date)]
        
        return "CN0835", "Instrument", invalid_rows
    
    def CN0836(self):
        # 'IF [Instrument.Interest rate type] = 'Fixed' THEN [Instrument.Interest rate cap] = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Interest rate type" is 'Fixed'
        fixed_interest_rate = df_instrument["Instrument.Interest rate type"] == 'Fixed'
        
        # Filter rows where "Interest rate cap" is not 'Non-applicable'
        non_applicable_cap = df_instrument["Instrument.Interest rate cap"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[(fixed_interest_rate) & (non_applicable_cap)]
        
        return "CN0836", "Instrument", invalid_rows
    
    def CN0837(self):
        # 'IF [Instrument.Interest rate type] = 'Fixed' THEN [Instrument.Interest rate floor] = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Interest rate type" is 'Fixed'
        fixed_interest_rate = df_instrument["Instrument.Interest rate type"] == 'Fixed'
        
        # Filter rows where "Interest rate floor" is not 'Non-applicable'
        non_applicable_floor = df_instrument["Instrument.Interest rate floor"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[(fixed_interest_rate) & (non_applicable_floor)]
        
        return "CN0837", "Instrument", invalid_rows
    
    def CN0838(self):
        # 'IF [Instrument.Interest rate type] = 'Fixed' THEN [Instrument.Interest rate spread / margin] = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Interest rate type" is 'Fixed'
        fixed_interest_rate = df_instrument["Instrument.Interest rate type"] == 'Fixed'
        
        # Filter rows where "Interest rate spread / margin" is not 'Non-applicable'
        non_applicable_spread = df_instrument["Instrument.Interest rate spread / margin"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[(fixed_interest_rate) & (non_applicable_spread)]
        
        return "CN0838", "Instrument", invalid_rows
    
    def CN0839(self):
        # 'IF [Instrument.Interest rate type] = 'Fixed' THEN [Instrument.Reference rate] = 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Filter rows where "Interest rate type" is 'Fixed'
        fixed_interest_rate = df_instrument["Instrument.Interest rate type"] == 'Fixed'
        
        # Filter rows where "Reference rate" is not 'Non-applicable'
        non_applicable_reference = df_instrument["Instrument.Reference rate"] != 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[(fixed_interest_rate) & (non_applicable_reference)]
        
        return "CN0839", "Instrument", invalid_rows
    
    def CN0847(self):
        # 'IF [Financial.Off-balance sheet amount] > 0 AND [Financial.Outstanding nominal amount] = 0 THEN
        # [Financial.Type of securitisation] <> 'Traditionally securitised'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Off-balance sheet amount" is greater than 0
        off_balance_positive = df_financial["Financial.Off-balance sheet amount"] > 0
        
        # Filter rows where "Outstanding nominal amount" is 0
        nominal_amount_zero = df_financial["Financial.Outstanding nominal amount"] == 0
        
        # Filter rows where "Type of securitisation" is 'Traditionally securitised'
        traditional_securitised = df_financial["Financial.Type of securitisation"] == 'Traditionally securitised'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_financial[(off_balance_positive) & (nominal_amount_zero) & (traditional_securitised)]
        
        return "CN0847", "Financial", invalid_rows
    
    def CN0901(self):
        # 'IF [Financial.Interest rate] <> 'Non-applicable' THEN [Financial.Accrued interest] <> 'Non-applicable'
        
        df_financial = self.df_dict["Financial"]
        
        # Filter rows where "Interest rate" is not 'Non-applicable'
        non_applicable_interest = df_financial["Financial.Interest rate"] != 'Non-applicable'
        
        # Filter rows where "Accrued interest" is 'Non-applicable'
        non_applicable_accrued = df_financial["Financial.Accrued interest"] == 'Non-applicable'
        
        # Filter rows where the above conditions are met
        invalid_rows = df_financial[(non_applicable_interest) & (non_applicable_accrued)]
        
        return "CN0901", "Financial", invalid_rows

    
    def CN0925(self):
        # Let T be the reference date: 
        # IF [Instrument] NOT IN ({[Instrument.Type of instrument] = 'Overdraft' AND [Financial.Off- balance sheet amount] = 'Non-applicable'} 
        # OR {[Instrument.Type of Instrument]  = ‘Deposits other than reverse repurchase agreements’ AND [Instrument.Legal final maturity date] =  'Non-applicable'})
        # THEN [Instrument.Inception date] (T) = [Instrument.Inception date] (T-1)
        
        df_instrument = self.df_dict["Instrument"]
        
        # Create conditions for filtering rows
        condition1 = (df_instrument["Instrument.Type of instrument"] == 'Overdraft') & (df_instrument["Financial.Off-balance sheet amount"] == 'Non-applicable')
        condition2 = (df_instrument["Instrument.Type of instrument"] == 'Deposits other than reverse repurchase agreements') & (df_instrument["Instrument.Legal final maturity date"] == 'Non-applicable')
        
        # Apply the conditions
        filtered_rows = df_instrument[~(condition1 | condition2)]
        
        # Shift the "Inception date" column to get T-1 values
        t_inception_date = df_instrument["Instrument.Inception date"]
        t_minus_1_inception_date = t_inception_date.shift(1)
        
        # Check if T Inception date is equal to T-1 Inception date
        invalid_rows = filtered_rows[~(t_inception_date == t_minus_1_inception_date)]
        
        return "CN0925", "Instrument", invalid_rows
    
    def CN0935(self):
        # Let T be the reference date: 
        # IF [Instrument] NOT IN ({ [Instrument.Type of instrument] = 'Overdraft' AND [Financial.Off- balance sheet amount] = 'Non-applicable'} 
        # OR {[Instrument.Type of instrument] = ‘Deposits other than reverse repurchase agreements’ AND [Instrument.Legal final maturity date] = 'Non-applicable'})  
        # THEN {[Instrument.Settlement date] (T) is not 'Non-applicable' AND [Instrument.Settlement date] (T) = [Instrument.Settlement date] (T-1)} 
        # IF AND ONLY IF [Instrument.Settlement date] (T-1) is not 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        
        # Create conditions for filtering rows
        condition1 = (df_instrument["Instrument.Type of instrument"] == 'Overdraft') & (df_instrument["Financial.Off-balance sheet amount"] == 'Non-applicable')
        condition2 = (df_instrument["Instrument.Type of instrument"] == 'Deposits other than reverse repurchase agreements') & (df_instrument["Instrument.Legal final maturity date"] == 'Non-applicable')
        
        # Apply the conditions
        filtered_rows = df_instrument[~(condition1 | condition2)]
        
        # Get the "Settlement date" at T and T-1
        t_settlement_date = df_instrument["Instrument.Settlement date"]
        t_minus_1_settlement_date = t_settlement_date.shift(1)
        
        # Get a boolean series indicating if T-1 Settlement date is not 'Non-applicable'
        t_minus_1_not_non_applicable = t_minus_1_settlement_date != 'Non-applicable'
        
        # Check if the conditions are met for T and T-1
        condition_met_t = (t_settlement_date != 'Non-applicable') & (t_settlement_date == t_minus_1_settlement_date)
        
        # Check if the IF AND ONLY IF condition is met
        invalid_rows = filtered_rows[(condition_met_t & t_minus_1_not_non_applicable) | (~condition_met_t & ~t_minus_1_not_non_applicable)]
        
        return "CN0935", "Instrument", invalid_rows
    
    def CN0945(self):
        # IF [Instrument.Settlement date] is not ‘Non-applicable’
        # AND [Instrument.Inception date] < [Instrument.Settlement date] 
        # AND  [Financial.Off-balance sheet amount] = 'Non-applicable' 
        # AND {[Instrument.Type of instrument] is not {‘Deposits other than reverse repurchase agreements’ 
        # AND [Instrument.Type of instrument] is not ‘Trade receivables’ HAVING Recourse attribute reported as ‘No recourse’
        # THEN [Instrument.Commitment amount at inception] is not 'Non-applicable'
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Create conditions for filtering rows
        condition1 = df_instrument["Instrument.Settlement date"] != 'Non-applicable'
        condition2 = df_instrument["Instrument.Inception date"] < df_instrument["Instrument.Settlement date"]
        condition3 = df_financial["Financial.Off-balance sheet amount"] == 'Non-applicable'
        condition4 = ~((df_instrument["Instrument.Type of instrument"] == 'Deposits other than reverse repurchase agreements') & (df_instrument["Instrument.Type of instrument"] == 'Trade receivables') & (df_instrument["Instrument.HAVING Recourse attribute reported"] == 'No recourse'))
        
        # Combine the conditions
        combined_condition = condition1 & condition2 & condition3 & condition4
        
        # Filter rows where the above conditions are met
        invalid_rows = df_instrument[combined_condition & (df_instrument["Instrument.Commitment amount at inception"] == 'Non-applicable')]
        
        return "CN0945", "Instrument", invalid_rows

    
    def CN0950(self):
        # Let T be the reference date: 
        # IF [Protection received.Type of protection] (T) OR [Protection received.Type of protection] (T-1) 
        # NOT IN {"Residential real estate", "Commercial real estate", "Offices and commercial premises"} 
        # THEN [Protection received.Type of protection] (T) = [Protection received.Type of protection] (T-1)
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of valid protection types
        valid_protection_types = {"Residential real estate", "Commercial real estate", "Offices and commercial premises"}
        
        # Get the protection types at T and T-1
        t_protection_types = df_protection_received["Protection received.Type of protection"]
        t_minus_1_protection_types = t_protection_types.shift(1)
        
        # Check if any of the protection types at T or T-1 are not in the valid set
        invalid_rows = df_protection_received[~(t_protection_types.isin(valid_protection_types) | t_minus_1_protection_types.isin(valid_protection_types))]
        
        return "CN0950", "Protection received", invalid_rows
    
    def CN0960(self):
        # [Protection received.Real estate collateral location] = 'Non-applicable' 
        # IF AND ONLY IF [Protection received.Type of protection] NOT IN {'Residential real estate collateral', 
        # 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of valid collateral types
        valid_collateral_types = {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        # Get the collateral location and protection types
        collateral_location = df_protection_received["Protection received.Real estate collateral location"]
        protection_types = df_protection_received["Protection received.Type of protection"]
        
        # Check if collateral location is 'Non-applicable' if protection type is not in the valid set
        invalid_rows = df_protection_received[(collateral_location != 'Non-applicable') & (~protection_types.isin(valid_collateral_types))]
        
        return "CN0960", "Protection received", invalid_rows
    
    def CN0961(self):
        # [Protection received.Real Estate Collateral Location Country] = 'Non-applicable' 
        # IF AND ONLY IF [Protection received.Type of protection] NOT IN {'Residential real estate collateral', 
        # 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of valid collateral types
        valid_collateral_types = {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        # Get the collateral location country and protection types
        collateral_location_country = df_protection_received["Protection received.Real Estate Collateral Location Country"]
        protection_types = df_protection_received["Protection received.Type of protection"]
        
        # Check if collateral location country is 'Non-applicable' if protection type is not in the valid set
        invalid_rows = df_protection_received[(collateral_location_country != 'Non-applicable') & (~protection_types.isin(valid_collateral_types))]
        
        return "CN0961", "Protection received", invalid_rows
    
    def CN0962(self):
        # [Protection received.Real Estate Collateral Location Region] = 'Non-applicable' 
        # IF AND ONLY IF [Protection received.Type of protection] 
        # NOT IN {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of valid collateral types
        valid_collateral_types = {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        # Get the collateral location region and protection types
        collateral_location_region = df_protection_received["Protection received.Real Estate Collateral Location Region"]
        protection_types = df_protection_received["Protection received.Type of protection"]
        
        # Check if collateral location region is 'Non-applicable' if protection type is not in the valid set
        invalid_rows = df_protection_received[(collateral_location_region != 'Non-applicable') & (~protection_types.isin(valid_collateral_types))]
        
        return "CN0962", "Protection received", invalid_rows
    
    def CN0963(self):
        # [Protection received.Real Estate Collateral Location Postal Code] = 'Non-applicable' 
        # IF AND ONLY IF [Protection received.Type of protection] 
        # NOT IN {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of valid collateral types
        valid_collateral_types = {'Residential real estate collateral', 'Commercial real estate collateral', 'Offices and commercial premises'}
        
        # Get the collateral location postal code and protection types
        collateral_location_postal_code = df_protection_received["Protection received.Real Estate Collateral Location Postal Code"]
        protection_types = df_protection_received["Protection received.Type of protection"]
        
        # Check if collateral location postal code is 'Non-applicable' if protection type is not in the valid set
        invalid_rows = df_protection_received[(collateral_location_postal_code != 'Non-applicable') & (~protection_types.isin(valid_collateral_types))]
        
        return "CN0963", "Protection received", invalid_rows
    
    def CN0980(self):
        # IF [Protection received.Real estate collateral location] <> <empty> THEN
        # [Protection received.Real estate collateral location country] = <empty> AND
        # [Protection received.Real estate collateral location region] = <empty> AND
        # [Protection received.Real estate collateral location postal code] = <empty>
        
        df_protection_received = self.df_dict["Protection received"]
        
        # Get the collateral location, country, region, and postal code
        collateral_location = df_protection_received["Protection received.Real estate collateral location"]
        collateral_location_country = df_protection_received["Protection received.Real estate collateral location country"]
        collateral_location_region = df_protection_received["Protection received.Real estate collateral location region"]
        collateral_location_postal_code = df_protection_received["Protection received.Real estate collateral location postal code"]
        
        # Check if collateral location is not empty, then other fields should be empty
        invalid_rows = df_protection_received[
            (collateral_location != "") &
            ((collateral_location_country != "empty") |
             (collateral_location_region != "empty") |
             (collateral_location_postal_code != "empty"))
        ]
        
        return "CN0980", "Protection received", invalid_rows
    
    
    def RI0030(self):
        # ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        # EXISTS IN {([Instrument.Observed agent identifier],[Instrument.Contract identifier],[Instrument.Instrument identifier])}
        
        df_financial = self.df_dict["Financial"]
        df_instrument = self.df_dict["Instrument"]
        
        # Create a set of tuples for ([Instrument.Observed agent identifier],[Instrument.Contract identifier],[Instrument.Instrument identifier])
        instrument_keys = set(
            tuple(row)
            for row in df_instrument[["Instrument.Observed agent identifier", "Instrument.Contract identifier", "Instrument.Instrument identifier"]].values
        )
        
        # Check if the financial keys exist in the instrument keys set
        invalid_rows = df_financial[
            ~df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].apply(tuple, axis=1).isin(instrument_keys)
        ]
        
        return "RI0030", "Financial", invalid_rows

    def RI0050(self):
        # ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        # EXISTS IN {([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])},
        # where [Counterparty-instrument.Counterparty role]='Creditor'
        
        df_financial = self.df_dict["Financial"]
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        
        # Create a set of tuples for ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])
        creditor_instrument_keys = set(
            tuple(row)
            for row in df_counterparty_instrument[df_counterparty_instrument["Counterparty-instrument.Counterparty role"] == "Creditor"]
            [["Counterparty-instrument.Observed agent identifier", "Counterparty-instrument.Contract identifier", "Counterparty-instrument.Instrument identifier"]].values
        )
        
        # Check if the financial keys exist in the creditor instrument keys set
        invalid_rows = df_financial[
            ~df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].apply(tuple, axis=1).isin(creditor_instrument_keys)
        ]
        
        return "RI0050", "Financial", invalid_rows

    def RI0060(self):
        # ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        # EXISTS IN {([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])},
        # where [Counterparty-instrument.Counterparty role]='Debtor'
        
        df_financial = self.df_dict["Financial"]
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        
        # Create a set of tuples for ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])
        debtor_instrument_keys = set(
            tuple(row)
            for row in df_counterparty_instrument[df_counterparty_instrument["Counterparty-instrument.Counterparty role"] == "Debtor"]
            [["Counterparty-instrument.Observed agent identifier", "Counterparty-instrument.Contract identifier", "Counterparty-instrument.Instrument identifier"]].values
        )
        
        # Check if the financial keys exist in the debtor instrument keys set
        invalid_rows = df_financial[
            ~df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].apply(tuple, axis=1).isin(debtor_instrument_keys)
        ]
        
        return "RI0060", "Financial", invalid_rows    
    
    def RI0070(self):
        # ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        # EXISTS IN {([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])},
        # where [Counterparty-instrument.Counterparty role]='Servicer'
        
        df_financial = self.df_dict["Financial"]
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        
        # Create a set of tuples for ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])
        servicer_instrument_keys = set(
            tuple(row)
            for row in df_counterparty_instrument[df_counterparty_instrument["Counterparty-instrument.Counterparty role"] == "Servicer"]
            [["Counterparty-instrument.Observed agent identifier", "Counterparty-instrument.Contract identifier", "Counterparty-instrument.Instrument identifier"]].values
        )
        
        # Check if the financial keys exist in the servicer instrument keys set
        invalid_rows = df_financial[
            ~df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].apply(tuple, axis=1).isin(servicer_instrument_keys)
        ]
        
        return "RI0070", "Financial", invalid_rows

    def RI0090(self):
        # ([Instrument.Observed agent identifier],[Instrument.Contract identifier],[Instrument.Instrument identifier])
        # EXISTS IN {([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])}
        
        df_instrument = self.df_dict["Instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Create a set of tuples for ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        financial_keys = set(
            tuple(row)
            for row in df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].values
        )
        
        # Check if the instrument keys exist in the financial keys set
        invalid_rows = df_instrument[
            ~df_instrument[["Instrument.Observed agent identifier", "Instrument.Contract identifier", "Instrument.Instrument identifier"]].apply(tuple, axis=1).isin(financial_keys)
        ]
        
        return "RI0090", "Instrument", invalid_rows

    def RI0110(self):
        # ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Contract identifier],[Counterparty-instrument.Instrument identifier])
        # EXISTS IN {([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])}
        
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_financial = self.df_dict["Financial"]
        
        # Create a set of tuples for ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        financial_keys = set(
            tuple(row)
            for row in df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].values
        )
        
        # Check if the counterparty instrument keys exist in the financial keys set
        invalid_rows = df_counterparty_instrument[
            ~df_counterparty_instrument[["Counterparty-instrument.Observed agent identifier", "Counterparty-instrument.Contract identifier", "Counterparty-instrument.Instrument identifier"]].apply(tuple, axis=1).isin(financial_keys)
        ]
        
        return "RI0110", "Counterparty-instrument", invalid_rows
    

    def RI0130(self):
        # ([Instrument-protection received.Observed agent identifier],[Instrument-protection received.Contract identifier],[Instrument-protection received.Instrument identifier])
        # EXISTS IN {([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])}
        
        df_instrument_protection_received = self.df_dict["Instrument-protection received"]
        df_financial = self.df_dict["Financial"]
        
        # Create a set of tuples for ([Financial.Observed agent identifier],[Financial.Contract identifier],[Financial.Instrument identifier])
        financial_keys = set(
            tuple(row)
            for row in df_financial[["Financial.Observed agent identifier", "Financial.Contract identifier", "Financial.Instrument identifier"]].values
        )
        
        # Check if the instrument-protection received keys exist in the financial keys set
        invalid_rows = df_instrument_protection_received[
            ~df_instrument_protection_received[["Instrument-protection received.Observed agent identifier", "Instrument-protection received.Contract identifier", "Instrument-protection received.Instrument identifier"]].apply(tuple, axis=1).isin(financial_keys)
        ]
        
        return "RI0130", "Instrument-protection received", invalid_rows

    def RI0191(self):
        # ([Counterparty default.Observed agent identifier],[Counterparty default.Counterparty Identifier])
        # EXISTS IN {(([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Counterparty Identifier]) | [Counterparty-instrument.Counterparty role]='Debtor')
        # UNION ([Protection received.Observed agent identifier],[Protection received.Protection provider identifier])}
        
        df_counterparty_default = self.df_dict["Counterparty default"]
        df_counterparty_instrument = self.df_dict["Counterparty-instrument"]
        df_protection_received = self.df_dict["Protection received"]
        
        # Create sets of tuples for ([Counterparty-instrument.Observed agent identifier],[Counterparty-instrument.Counterparty Identifier])
        debtor_counterparty_instrument_keys = set(
            tuple(row)
            for row in df_counterparty_instrument[df_counterparty_instrument["Counterparty-instrument.Counterparty role"] == "Debtor"]
            [["Counterparty-instrument.Observed agent identifier", "Counterparty-instrument.Counterparty Identifier"]].values
        )
        
        protection_received_keys = set(
            tuple(row)
            for row in df_protection_received[["Protection received.Observed agent identifier", "Protection received.Protection provider identifier"]].values
        )
        
        # Check if the counterparty default keys exist in the union of debtor counterparty instrument keys and protection received keys
        invalid_rows = df_counterparty_default[
            ~df_counterparty_default[["Counterparty default.Observed agent identifier", "Counterparty default.Counterparty Identifier"]].apply(tuple, axis=1).isin(debtor_counterparty_instrument_keys.union(protection_received_keys))
        ]
        
        return "RI0191", "Counterparty default", invalid_rows    


    def RI0220(self):
        # ([Protection received.Observed agent identifier],[Protection received.Protection identifier])
        # EXISTS IN {([Instrument-protection received.Observed agent identifier],[Instrument-protection received.Protection identifier])}
        
        df_protection_received = self.df_dict["Protection received"]
        df_instrument_protection_received = self.df_dict["Instrument-protection received"]
        
        # Create a set of tuples for ([Instrument-protection received.Observed agent identifier],[Instrument-protection received.Protection identifier])
        instrument_protection_received_keys = set(
            tuple(row)
            for row in df_instrument_protection_received[["Instrument-protection received.Observed agent identifier", "Instrument-protection received.Protection identifier"]].values
        )
        
        # Check if the protection received keys exist in the instrument-protection received keys set
        invalid_rows = df_protection_received[
            ~df_protection_received[["Protection received.Observed agent identifier", "Protection received.Protection identifier"]].apply(tuple, axis=1).isin(instrument_protection_received_keys)
        ]
        
        return "RI0220", "Protection received", invalid_rows

    def RI0250(self):
        # ([Instrument-protection received.Observed agent identifier],[Instrument-protection received.Protection identifier])
        # EXISTS IN {([Protection received.Observed agent identifier],[Protection received.Protection identifier])}
        
        df_instrument_protection_received = self.df_dict["Instrument-protection received"]
        df_protection_received = self.df_dict["Protection received"]
        
        # Create a set of tuples for ([Protection received.Observed agent identifier],[Protection received.Protection identifier])
        protection_received_keys = set(
            tuple(row)
            for row in df_protection_received[["Protection received.Observed agent identifier", "Protection received.Protection identifier"]].values
        )
        
        # Check if the instrument-protection received keys exist in the protection received keys set
        invalid_rows = df_instrument_protection_received[
            ~df_instrument_protection_received[["Instrument-protection received.Observed agent identifier", "Instrument-protection received.Protection identifier"]].apply(tuple, axis=1).isin(protection_received_keys)
        ]
        
        return "RI0250", "Instrument-protection received", invalid_rows
    

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

