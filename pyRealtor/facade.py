import os
import pandas as pd

from pyRealtor.geo import GeoLocationService
from pyRealtor.realtor import RealtorService
from pyRealtor.report import ReportingService

class HousesFacade:

    def search_save_houses(
        self,
        search_area: str,
        report_file_name: str,
        listing_type: str = 'for_sale',
        use_proxy: bool = False, 
        get_summary: bool = True,
        column_mapping_cfg_fpath:str = 'config/column_mapping_cfg.json', 
        column_lst: list = [
        'MLS', 'Description', 'Bedrooms', 'Bathrooms', 'Size', 'Stories', 
        'House Category', 'Ammenities', 
        'Price', 'Address', 'Latitude', 'Longitude', 'Ownership Category', 'Nearby Ammenities', 'Open House', 'Website'],
        **kwargs
    ):
        current_directory = os.getcwd()
        file_path_to_save = os.path.join(current_directory, report_file_name)

        if 'listing_type' == 'for_rent':
            column_lst = ['Rent' if x=='Price' else x for x in column_lst]

        geo_service_obj = GeoLocationService()
        realtor_service_obj = RealtorService(
            ReportingService(
                column_mapping_cfg_fpath,
                column_lst
            )
        )

        geo_result_json = geo_service_obj.search_geo_location(city=search_area)

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
        realtor_service_obj.set_sort_method(by='listing_price', ascending_order=True)

        if 'open_house_date' in kwargs:
            open_house_date = kwargs['open_house_date']
            realtor_service_obj.set_open_house_only(open_house_date)

        #print(realtor_service_obj.search_api_params)

        houses_df = realtor_service_obj.search_houses(
            use_proxy
        ).to_dataframe()

        if houses_df.shape[0] > 0:
            if listing_type == 'for_sale':
                sorted_col_name = 'Price'
            else:
                sorted_col_name = 'Rent'

            current_min_amount = pd.to_numeric(houses_df[sorted_col_name]).values[-1]
            while True:
                realtor_service_obj.set_min_amount(
                    new_amount = current_min_amount,
                    col_name = sorted_col_name
                )

                try:
                    new_houses_df = realtor_service_obj.search_houses(
                        use_proxy
                    ).to_dataframe()
                except Exception as e:
                    break

                if new_houses_df.shape[0] > 0:
                    new_min_amount = pd.to_numeric(new_houses_df[sorted_col_name]).values[-1]

                    if new_min_amount > current_min_amount:
                        houses_df = pd.concat([houses_df, new_houses_df], axis=0).drop_duplicates(subset=['MLS'])
                        current_min_amount = new_min_amount
                    else:
                        break
                else:
                    break


        if get_summary:
            if listing_type == 'for_sale':
                summary_df = realtor_service_obj.report_obj.get_average(
                    dataframe = houses_df.copy(),
                    average_col_name = 'Price',
                    grpby_col_lst = ['Bedrooms', 'Bathrooms', 'House Category', 'Ownership Category']
                )
            elif listing_type == 'for_rent':
                """
                summary_df = realtor_service_obj.report_obj.get_average(
                    dataframe = houses_df,
                    average_col_name = 'Rent',
                    grpby_col_lst = ['Bedrooms', 'Bathrooms', 'House Category', 'Ownership Category']
                )
                """
                summary_df = pd.DataFrame()

        print(houses_df)

        if houses_df.shape[0] > 0:
            realtor_service_obj.report_obj.save_excel(
                houses_df,
                file_path_to_save,
                summary_df
            )