import os

from pyRealtor.geo import GeoLocationService
from pyRealtor.realtor import RealtorService
from pyRealtor.report import ReportingService

class HousesFacade:

    def search_save_houses(
        self,
        search_area: str,
        report_file_name: str,
        listing_type: str = 'for_sale', 
        column_mapping_cfg_fpath:str = 'config/column_mapping_cfg.json', 
        column_lst: list = [
        'mls', 'listing_description', 'total_bathrooms', 'total_bedrooms', 'size', 'total_stories', 
        'house_type', 'house_ammenities', 
        'listing_price', 'listing_address', 'listing_address_lat', 'listing_address_long', 'listing_ownership_type', 'lising_nearby_ammenities', 'open_house', 'listing_website'],
        **kwargs
    ):
        current_directory = os.getcwd()
        file_path_to_save = os.path.join(current_directory, report_file_name)

        geo_service_obj = GeoLocationService()
        realtor_service_obj = RealtorService(
            ReportingService(
                column_mapping_cfg_fpath,
                column_lst
            )
        )

        geo_result_json = geo_service_obj.search_geo_location(city=search_area)

        """
        display_address = geo_result_json['SubArea'][0]['Location']
        geo_coord_1 = (
            geo_result_json['SubArea'][0]['Viewport']['NorthEast']['Latitude'],
            geo_result_json['SubArea'][0]['Viewport']['NorthEast']['Latitude']
        )
        geo_coord_2 = (
            geo_result_json['SubArea'][0]['Viewport']['SouthWest']['Latitude'],
            geo_result_json['SubArea'][0]['Viewport']['SouthWest']['Latitude']
        )
        """

        display_address = geo_result_json["display_name"]
        geo_coord_1 = (
            float(geo_result_json['boundingbox'][0]),
            float(geo_result_json['boundingbox'][2])
        )
        geo_coord_2 = (
            float(geo_result_json['boundingbox'][1]),
            float(geo_result_json['boundingbox'][3])
        )

        geo_service_obj.set_display_physical_location(display_address)
        geo_service_obj.set_geo_location_boundry(geo_coord_1, geo_coord_2)

        realtor_service_obj.set_geo_coordinate_boundry(geo_service_obj)
        realtor_service_obj.set_transaction_type(listing_type)

        if 'open_house_date' in kwargs:
            open_house_date = kwargs['open_house_date']
            realtor_service_obj.set_open_house_only(open_house_date)

        #print(realtor_service_obj.search_api_params)
        houses_df = realtor_service_obj.search_houses().to_dataframe()
        print(houses_df)

        if houses_df.shape[0] > 0:
            realtor_service_obj.report_obj.save_excel(
                houses_df,
                file_path_to_save
            )