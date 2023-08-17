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

Regenerate


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

