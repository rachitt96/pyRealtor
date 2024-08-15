from pyRealtor.realtorCa import RealtorCa
from pyRealtor.realtorCom import RealtorCom
from pyRealtor.report import ReportingService


class RealtorFactory:

    def get_realtor(self, country: str, config: str = None):

        if config is None and country == "Canada":
            config = "config/column_mapping_cfg.json"
        elif config is None and country == "United States":
            config = "config/column_mapping_cfg_realtor_com.json"

        if country == 'Canada':
            realtor_service_obj = RealtorCa(
                ReportingService(
                    column_mapping_cfg_fpath = config,
                    column_lst = [
                        'MLS', 'Description', 'Bedrooms', 'Bathrooms', 'Size', 'Stories', 
                        'House Category', 'Ammenities', 
                        'Price', 'Address', 'Latitude', 'Longitude', 'Ownership Category', 'Nearby Ammenities', 'Open House', 'Website'
                    ],
                    summary_col_lst = ['Bedrooms', 'Bathrooms', 'House Category', 'Ownership Category']
                )
            )
        elif country == 'United States':
            realtor_service_obj = RealtorCom(
                ReportingService(
                    column_mapping_cfg_fpath = config,
                    column_lst = [
                        'ID', 'Bathrooms', 'Bedrooms', 'Size', 'House Category',
                        'Price', 'street name', 'city', 'state', 'Latitude', 'Longitude', 'InsertedDate'
                    ],
                    summary_col_lst = ['Bedrooms', 'Bathrooms', 'House Category']
                )
            )
        else:
            raise ValueError(f"Expected countries are United States or Canada, however received {country}")
        
        return realtor_service_obj