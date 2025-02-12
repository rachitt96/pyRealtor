import json
import importlib.resources
import pkg_resources
import re
import sys

import pandas as pd

class ReportingService:  

    def __init__(
            self, 
            column_mapping_cfg_fpath:str = 'realtor_json_normalize_mapping.json', 
            column_lst: list = [
                'MLS', 'Description', 'Bathrooms', 'Bedrooms', 'Size', 'Stories', 
                'House Category', 'Ammenities', 
                'Price', 'Address', 'Latitude', 'Longitude', 'Ownership Category', 'Nearby Ammenities', 'Open House', 'Website'
            ],
            summary_col_lst: list = ['Bedrooms', 'Bathrooms', 'House Category', 'Ownership Category']
    ):
        self.house_json_lst = []
        self.column_lst = column_lst
        self.summary_col_lst = summary_col_lst
        self.column_mapping_dict = self.load_mapping_cfg(
            config_path=column_mapping_cfg_fpath
        )

    def load_mapping_cfg(self, config_path:str):
        config_dict = {}
        
        with pkg_resources.resource_stream('pyRealtor', config_path) as f:
            config_dict = json.load(f)
        
        return config_dict

    def get_json_value(self, json_data, key_chain):
        if key_chain in json_data:
            return json_data[key_chain]
        elif key_chain.split(".")[0] in json_data:
            key, value = key_chain.split(".", 1)
            return self.get_json_value(
                json_data[key],
                value
            )
        elif key_chain.split("->")[0] in json_data:
            key, value = key_chain.split("->", 1)
            val_lst = [
                    self.get_json_value(
                        ele,
                        value
                    )
                    for ele in json_data[key] 
                ]
            val_lst = [str(val).strip() for val in val_lst if val is not None]

            return ";".join(filter(None, val_lst))
            
        else:
            return None


    def to_dataframe(self):
        dataframe_values = []
        
        for mls_listing_json in self.house_json_lst:
            dataframe_row_values = []
            for col_to_report in self.column_lst:
                json_copy = mls_listing_json.copy()

                json_copy = self.get_json_value(json_copy, self.column_mapping_dict[col_to_report])
                #json_copy = ";".join(filter(None, json_copy))

                """
                if "->" in self.column_mapping_dict[col_to_report]:
                    col_hierarchy_lst = self.column_mapping_dict[col_to_report].split("->")

                    if "." in col_hierarchy_lst[0]:
                        new_col_hierarchy_lst = col_hierarchy_lst[0].split(".")

                        for col in new_col_hierarchy_lst[:-1]:
                            if col in json_copy:
                                json_copy = json_copy[col]
                            else:
                                json_copy = ''

                        col_hierarchy_lst = new_col_hierarchy_lst[-1:] + col_hierarchy_lst[1:]

                    if (len(col_hierarchy_lst) == 2) and (col_hierarchy_lst[0] in json_copy):
                        json_copy = ";".join(
                            filter(
                                None,
                                [
                                    ele[col_hierarchy_lst[1]] if col_hierarchy_lst[1] in ele else 
                                    ele[col_hierarchy_lst[1].split(".")[0]][col_hierarchy_lst[1].split(".")[1]] if (col_hierarchy_lst[1].split(".")[0] in ele) and (col_hierarchy_lst[1].split(".")[1] in ele[col_hierarchy_lst[1].split(".")[0]]) else 
                                    ''
                                    for ele in json_copy[col_hierarchy_lst[0]] 
                                ]
                            )
                        )
                    else:
                        json_copy = ''
                    
                else:
                    col_hierarchy_lst = self.column_mapping_dict[col_to_report].split(".")
                    for col_hierarchy in col_hierarchy_lst:
                        if col_hierarchy in json_copy:
                            json_copy = json_copy[col_hierarchy]
                        else:
                            json_copy = ''
                """
                dataframe_row_values.append(json_copy)

            dataframe_values.append(dataframe_row_values)
        
        listing_dataframe = pd.DataFrame(dataframe_values, columns=self.column_lst)
        self.house_json_lst = []

        return listing_dataframe

    def get_average(self, dataframe: pd.DataFrame, average_col_name: str):
        if (dataframe[average_col_name].dtype == 'object') and (dataframe[average_col_name].str.contains(';').any()):
            dataframe[average_col_name] = dataframe[average_col_name].str.split(';')
            dataframe[average_col_name] = dataframe[average_col_name].apply(lambda row: [float(x) for x in row if x!=''])
            dataframe[average_col_name] = dataframe[average_col_name].apply(lambda row: sum(row)/len(row) if len(row)>0 else row)
        dataframe[average_col_name] = pd.to_numeric(dataframe[average_col_name])
        dataframe['Bedrooms'] = dataframe['Bedrooms'].fillna('').astype("string")

        dataframe['Bedrooms'] = dataframe['Bedrooms'].apply(
            lambda row: 0 if row=='' else row if ";" in row else eval(row)
        )

        summary_df = dataframe.groupby(
            self.summary_col_lst,
            as_index = True
        )[average_col_name].mean()

        summary_df = summary_df.rename('Average '+average_col_name)

        return summary_df

    def save_excel(self, dataframe_to_report, file_path, summary_dataframe):
        
        with pd.ExcelWriter(file_path) as excel_writer:
            summary_dataframe.to_excel(excel_writer, sheet_name = 'Summary', freeze_panes = (1,0))
            dataframe_to_report.to_excel(excel_writer, sheet_name = 'Listings', index=False, freeze_panes = (1,0))



def test(listing_dataframe):
    print(listing_dataframe['Bedrooms'].tail(20))
    listing_dataframe['Bedrooms'] = listing_dataframe['Bedrooms'].apply(lambda row: 0 if row=='' else eval(row))
    print(listing_dataframe['Bedrooms'].tail(20))
    summary_df = listing_dataframe.groupby(
                ['Bedrooms', 'Bathrooms', 'House Category', 'Ownership Category'],
                as_index = True
            )['Price'].mean()
    print(summary_df)

    #print(summary_df.get_group(('3', '1', 'Row / Townhouse', 'Condominium/Strata'))[['mls', 'listing_price']])
    #print(summary_df.get_group(('3', '1', 'Row / Townhouse', 'Condominium/Strata'))['listing_price'].mean())

    #summary_df.to_excel('../summary_test_1.xlsx')

if __name__ == "__main__":
    current_df = pd.read_excel('../ottawa_all_listings.xlsx', sheet_name='Listings', na_filter = False)
    test(listing_dataframe=current_df.copy())