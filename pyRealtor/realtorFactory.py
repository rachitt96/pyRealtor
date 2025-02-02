from pyRealtor.realtorCa import RealtorCa
from pyRealtor.realtorCom import RealtorCom
from pyRealtor.housingCom import HousingCom
from pyRealtor.report import ReportingService


class RealtorFactory:

    def get_realtor(self, country: str, config: str = None):

        country = country.lower()

        if config is None and country == "canada":
            config = "config/column_mapping_cfg.json"
        elif config is None and country == "united states":
            config = "config/column_mapping_cfg_realtor_com.json"
        elif config is None and country == "india":
            config = "config/column_mapping_cfg_housing_com.json"

        if country == 'canada':
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
        elif country == 'united states':
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
        elif country == 'india':
            realtor_service_obj = HousingCom(
                ReportingService(
                    column_mapping_cfg_fpath = config,
                    column_lst = [
                        'ID', 'Bedrooms', 'Bathrooms', 'Size', 
                        'House Category', 
                        'Price', 'Address', "Realtor Brokerage", "Website", "Latitude", "Longitude", "InsertedDate",
                        "SubID", "label", "SubSize", "SubPrice"
                    ],
                    summary_col_lst = ['Bedrooms',  'House Category']
                )
            )
        else:
            raise ValueError(f"Expected countries are United States, Canada, or India, however received {country}")
        
        return realtor_service_obj