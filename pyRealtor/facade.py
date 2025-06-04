import os
import pandas as pd
import datetime

from pyRealtor.geo import GeoLocationService
from pyRealtor.realtorFactory import RealtorFactory
from pyRealtor.report import ReportingService

class HousesFacade:

    def search_save_houses(
        self,
        search_area: str,
        report_file_name: str = None,
        country: str = None,
        state: str = None,
        listing_type: str = 'for_sale',
        use_proxy: bool = False, 
        get_summary: bool = True,
        price_from: int = None,
        sorted_col_name:str = None,
        sorted_col_asc:bool = True,
        realtor_name_filter: str = None,
        realtor_brokerage_filter: str = None,
        column_mapping_cfg_fpath:str = None, 
        column_lst: list = None,
        **kwargs
    ):
        
        geo_service_obj = GeoLocationService()

        if country is None:
            country = geo_service_obj.get_country(city = search_area, state=state)

        realtor_service_obj = RealtorFactory().get_realtor(
            country = country,
            config = column_mapping_cfg_fpath
        )

        geo_result_json = geo_service_obj.search_geo_location(
            city=search_area,
            province=state,
            country=country
        )

        display_address = geo_result_json["name"]
        geo_service_obj.set_display_physical_location(display_address)
        realtor_service_obj.set_transaction_type(listing_type)
    
        geo_service_obj.set_geo_location_boundry(geo_result_json)

        if report_file_name is None:
            report_file_name = f"{geo_service_obj.physical_location}_{listing_type.lower()}_{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')}.xlsx"

        current_directory = os.getcwd()
        file_path_to_save = os.path.join(current_directory, report_file_name)

        try:
            realtor_service_obj.set_geo_coordinate_boundry(geo_service_obj)
        except Exception:
            raise ValueError(f"Area: {search_area} in Country: {country} does not fit geographic requirements") 
        
        if price_from is not None:
            realtor_service_obj.set_min_amount(
                new_amount = int(price_from),
                col_name = sorted_col_name
            )

        if sorted_col_name is not None:
            realtor_service_obj.set_sort_method(by=sorted_col_name, ascending_order=sorted_col_asc)

        if 'open_house_date' in kwargs:
            open_house_date = kwargs['open_house_date']
            realtor_service_obj.set_open_house_only(open_house_date)

        if (realtor_name_filter or realtor_brokerage_filter):
            if 'Realtor Name' not in column_lst:
                realtor_service_obj.report_obj.column_lst.append('Realtor Name')
            if 'Realtor Brokerage' not in column_lst:
                realtor_service_obj.report_obj.column_lst.column_lst.append('Realtor Brokerage')

        self.houses_df_preprocess = realtor_service_obj.search_houses(
            use_proxy
        ).to_dataframe()
        houses_df = self.houses_df_preprocess

        loop_counter = 0

        if houses_df.shape[0] > 0 and sorted_col_name == 'listing_price':

            current_min_amount = pd.to_numeric(
                houses_df[sorted_col_name],
                downcast="integer"
            ).values[-1]

            while True:
                print(f"Fetching listings with minimum price: {current_min_amount}")
                
                if loop_counter > 10:
                    print(f"The Maximun Limit has reached. Please use the function with parameter price_from={current_min_amount} after some time")
                    break
                
                realtor_service_obj.set_min_amount(
                    new_amount = int(current_min_amount),
                    col_name = sorted_col_name
                )

                try:
                    new_houses_df = realtor_service_obj.search_houses(
                        use_proxy
                    ).to_dataframe()
                except Exception as e:
                    print(f"Exception raised while searching from Minimum Price: {current_min_amount}: {e}")
                    break

                if new_houses_df.shape[0] > 0:
                    new_min_amount = pd.to_numeric(
                        new_houses_df[sorted_col_name],
                        downcast="integer"
                    ).values[-1]

                    if new_min_amount > current_min_amount:
                        houses_df = pd.concat([houses_df, new_houses_df], axis=0).drop_duplicates(subset=['MLS'])
                        current_min_amount = new_min_amount
                    else:
                        break
                else:
                    break

                loop_counter += 1

        if realtor_name_filter and "Realtor Name" in houses_df.columns:
            print(f"Filtering for Realtor Name: {realtor_name_filter}")
            houses_df = houses_df[
                houses_df["Realtor Name"].str.contains(realtor_name_filter, case=False)
            ]
            print(f"Number of listings found after filtering: {houses_df.shape[0]}")
        elif realtor_brokerage_filter and "Realtor Brokerage" in houses_df.columns:
            print(f"Filtering for Realtor's Brokerage Name: {realtor_brokerage_filter}")
            houses_df = houses_df[
                houses_df["Realtor Brokerage"].str.contains(realtor_brokerage_filter, case=False)
            ]
            print(f"Number of listings found after filtering: {houses_df.shape[0]}")

        self.houses_df = realtor_service_obj.transform(df=houses_df)
        houses_df = self.houses_df

        if get_summary:
            if listing_type == 'for_sale':
                summary_df = realtor_service_obj.report_obj.get_average(
                    dataframe = houses_df.copy(),
                    average_col_name = 'Price',
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

    def search_by_listing_id(
        self, 
        listing_id: str, 
        country: str = 'Canada', 
        use_proxy: bool = False
    ):
        """ Get the listing details for a specific listing id
        
        Args:
            listing_id (str): Real Estate Website's listing id 
            country (str): Country Name 
            use_proxy (bool): To use proxies for hiding your IP Address while fetching data
        
        Returns:
            DataFrame: pandas dataframe with the listing details
        """
        
        if country.lower() != 'canada':
            raise ValueError(f"Expecting Canada as country name, however received {country}")
        
        mls_df = RealtorFactory().get_realtor(
            country = country
        ).set_listing_id(
            listing_id
        ).search_houses(
            use_proxy
        ).to_dataframe()

        return mls_df