import json
import importlib.resources
import pkg_resources

import pandas as pd

class ReportingService:  

    def __init__(self, column_mapping_cfg_fpath:str = 'realtor_json_normalize_mapping.json', column_lst: list = [
        'mls', 'listing_description', 'total_bathrooms', 'total_bedrooms', 'size', 'total_stories', 
        'house_type', 'house_ammenities', 
        'listing_price', 'listing_address', 'listing_address_lat', 'listing_address_long', 'listing_ownership_type', 'lising_nearby_ammenities', 'open_house', 'listing_website'
    ]):
        self.house_json_lst = []
        self.column_lst = column_lst
        self.column_mapping_dict = self.load_mapping_cfg(
            config_path=column_mapping_cfg_fpath
        )

    def load_mapping_cfg(self, config_path:str):
        config_dict = {}
        
        with pkg_resources.resource_stream('pyRealtor', config_path) as f:
            config_dict = json.load(f)
        
        return config_dict


    def to_dataframe(self):
        dataframe_values = []
        #print(self.house_json_lst)
        for mls_listing_json in self.house_json_lst:
            dataframe_row_values = []
            for col_to_report in self.column_lst:
                json_copy = mls_listing_json.copy()
                col_hierarchy_lst = self.column_mapping_dict[col_to_report].split(".")
                for col_hierarchy in col_hierarchy_lst:
                    if col_hierarchy in json_copy:
                        json_copy = json_copy[col_hierarchy]
                    else:
                        json_copy = ''
                dataframe_row_values.append(json_copy)
            dataframe_values.append(dataframe_row_values)
        #print(dataframe_values)
        dataframe = pd.DataFrame(dataframe_values, columns=self.column_lst)
        
        return dataframe

    def save_excel(self, dataframe_to_report, file_path):
        dataframe_to_report.to_excel(file_path, index=False, freeze_panes = (1,0))