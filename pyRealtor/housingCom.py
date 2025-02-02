import requests
from requests.adapters import HTTPAdapter, Retry
import pkg_resources
import yaml
import pandas as pd
import copy
import json
import numpy as np
import re

from pyRealtor.geo import GeoLocationService
from pyRealtor.report import ReportingService
#from report import ReportingService
from pyRealtor.proxy import Proxy
from pyRealtor.realtor import Realtor

class HousingCom(Realtor):

    def __init__(self, report_obj: ReportingService):
        self.search_api_endpoint = "https://mightyzeus-mum.housing.com/api/gql"
        self.search_api_params = {
            'isBot': False,
            'emittedFrom': 'client_buy_SRP',
            'platform': 'desktop',
            'source': 'web',
            'source_name': 'AudienceWeb'
        }
        self.search_api_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://housing.com",
            "Referer": "https://housing.com"
        }
        self.search_api_body = {
            "query": "",
            "variables": {}
        }
        
        self.city_lst_api_body = copy.deepcopy(self.search_api_body)
        self.type_ahead_api_body = copy.deepcopy(self.search_api_body)
        self.hash_api_body = copy.deepcopy(self.search_api_body)

        self.report_obj = report_obj

    def set_sort_method(self, by: str, ascending_order: bool):
        pass

    def set_geo_coordinate_boundry(self, geo_location_obj: GeoLocationService):
        if "searchQuery" not in self.type_ahead_api_body["variables"]:
            self.type_ahead_api_body["variables"]["searchQuery"] = {}
        
        self.suburb = geo_location_obj.address_json["suburb"]
        self.state_district = geo_location_obj.address_json["state_district"]
        self.state = geo_location_obj.address_json["state"]

        self.type_ahead_api_body["variables"]["searchQuery"]['name'] = self.suburb
        self.type_ahead_api_body["variables"]["searchQuery"]['excludeEntities'] = []
        self.type_ahead_api_body["variables"]["searchQuery"]['rows'] = 1
        self.type_ahead_api_body["variables"]["searchQuery"]['allowedCrossCity'] = False
        self.type_ahead_api_body["variables"]["variant"] = "moondragonV2"


    def set_transaction_type(self, transaction_type: str = 'for_sale'):
        if "searchQuery" not in self.type_ahead_api_body["variables"]:
            self.type_ahead_api_body["variables"]["searchQuery"] = {}

        self.city_lst_api_body["variables"]["category"] = "residential"
        self.type_ahead_api_body["variables"]["searchQuery"]['category'] = 'residential'
        self.hash_api_body["variables"]["category"] = 'residential'
        self.search_api_body["variables"]['category'] = 'residential'
        self.search_api_body["variables"]['addSellersData'] = True
        self.search_api_body["variables"]['getStructured'] = True
        self.search_api_body["variables"]['adReq'] = False

        if transaction_type.lower() == 'for_sale':
            self.city_lst_api_body["variables"]["service"] = "buy"
            self.type_ahead_api_body["variables"]["searchQuery"]['service'] = 'buy'
            self.hash_api_body["variables"]["service"] = 'buy'
            self.search_api_body["variables"]['service'] = 'buy'
            self.search_api_body["variables"]['isRent'] = False

        elif transaction_type.lower() == 'for_rent':
            self.city_lst_api_body["variables"]["service"] = "rent"
            self.type_ahead_api_body["variables"]["searchQuery"]['service'] = 'rent'
            self.hash_api_body["variables"]["service"] = 'rent'
            self.search_api_body["variables"]['service'] = 'rent'
            self.search_api_body["variables"]['isRent'] = True

    def set_min_amount(self, new_amount, col_name):
        pass

    def set_open_house_only(self, open_house_date):
        pass

    def transform(self, df):
        if set(['SubID', 'label', 'SubSize', 'SubPrice']).intersection(set(df.columns.values)):
            sub_id_only = df['SubID'].str.contains(";")

            houses_sub_df = df[sub_id_only == True]
            df = df[sub_id_only == False]

            houses_sub_df['SubPrice'] = houses_sub_df['SubPrice'].replace('', np.nan)
            houses_sub_df = houses_sub_df.dropna(subset=['SubPrice'])

            houses_sub_df[['House Category', 'SubID', 'label', 'SubSize', 'SubPrice']] = houses_sub_df[['House Category', 'SubID', 'label', 'SubSize', 'SubPrice']].apply(lambda x: x.str.split(";"), axis=0)
            houses_sub_df['House Category'] = houses_sub_df['House Category'].apply(lambda x: list(set(x)))
            houses_sub_df['label'] = houses_sub_df['label'].apply(lambda label: [m.group(1) for m in map(re.compile(r'^(\d+).*$').match, label) if m])

            match_ids = (houses_sub_df['label'].map(len) == houses_sub_df['SubPrice'].map(len)) \
                & (houses_sub_df['label'].map(len) == houses_sub_df['SubSize'].map(len))
            houses_sub_df_match = houses_sub_df[match_ids==True]
            houses_sub_df_mismatch = houses_sub_df[match_ids==False]

            houses_sub_df_match = houses_sub_df_match.explode([ 'SubID', 'label', 'SubSize', 'SubPrice'])
            #houses_sub_df_mismatch = houses_sub_df_mismatch.explode(['SubID', 'SubSize', 'SubPrice'])
            houses_sub_df_mismatch['label'] = houses_sub_df_mismatch['label'].apply(lambda x: ';'.join(list(set(x))))
            houses_sub_df_mismatch['SubID'] = houses_sub_df_mismatch['SubID'].apply(lambda x: ';'.join(x))
            houses_sub_df_mismatch['SubSize'] = houses_sub_df_mismatch['SubSize'].apply(lambda x: ';'.join(x))
            houses_sub_df_mismatch['SubPrice'] = houses_sub_df_mismatch['SubPrice'].apply(lambda x: ';'.join(x))

            houses_sub_df = pd.concat([houses_sub_df_match, houses_sub_df_mismatch])
            houses_sub_df[['ID', 'Bedrooms', 'Size', 'Price']] = houses_sub_df[['SubID', 'label', 'SubSize', 'SubPrice']]
            
            houses_df = pd.concat([df, houses_sub_df])
            houses_df = houses_df.drop(columns=['SubID', 'label', 'SubSize', 'SubPrice'])


        houses_df['Latitude'] = houses_df['Latitude'].apply(lambda coord: coord[0])
        houses_df['Longitude'] = houses_df['Longitude'].apply(lambda coord: coord[1])

        #size_pattern = re.compile(r'^(\d+).*$')
        #houses_df['Size'] = houses_df['Size'].apply(lambda size: re.match(size_pattern, size).group(1) if re.match(size_pattern, size) else size)
        houses_df['Price'] = houses_df['Price'].apply(lambda price: ";".join(str(x) for x in price) if isinstance(price, list) else price)
        houses_df['House Category'] = houses_df['House Category'].apply(lambda cat: ";".join(str(x) for x in cat) if isinstance(cat, list) else cat)
        houses_df['Website'] = houses_df['Website'].apply(lambda url: 'https://housing.com'+url)
        houses_df['InsertedDate'] = pd.to_datetime(houses_df['InsertedDate']).dt.date

        return houses_df


    def search_houses(self, use_proxy = False):
        city_details_dict = {}

        city_lst_api_param = self.search_api_params.copy()
        type_ahead_api_param = self.search_api_params.copy()
        hash_api_param = self.search_api_params.copy()
        search_api_param = self.search_api_params.copy()

        city_lst_api_param["apiName"] = "CITY_LIST_API"
        search_api_param["apiName"] = "SEARCH_RESULTS"

        s = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[ 500, 502, 503, 504 ]
        )

        s.mount('https://', HTTPAdapter(max_retries=retries))

        graph_ql_dict = {}
        with pkg_resources.resource_stream('pyRealtor', 'config/graphql_queries_housing.yml') as graph_ql_yaml:
            graph_ql_dict = yaml.safe_load(graph_ql_yaml)

        if "city_list_function" in graph_ql_dict:
            self.city_lst_api_body["query"] = graph_ql_dict["city_list_function"]
        else:
            raise Exception("city_list_function key is expected in config graphql_queries_housing.yml")

        try:
            city_list_api_response = s.post(
                self.search_api_endpoint,
                headers=self.search_api_headers,
                json = self.city_lst_api_body,
                params = city_lst_api_param
            )
        except Exception as e:
            raise

        if city_list_api_response.status_code == 200:
            city_list_response_json = city_list_api_response.json()
            for city in city_list_response_json["data"]["cityListing"]["topCities"]:
                if city["name"].lower() == self.state_district.lower():
                    city_details_dict = city
            for city in city_list_response_json["data"]["cityListing"]["otherCities"]:
                if city["name"].lower() == self.state_district.lower():
                    city_details_dict = city
        else:
            raise Exception(f"Expected 200 response, but received CITY_LIST_API response: {city_list_api_response.status_code}")


        if "type_ahead_function" in graph_ql_dict:
            self.type_ahead_api_body["query"] = graph_ql_dict['type_ahead_function']
        else:
            raise Exception("type_ahead_function key is expected in config graphql_queries_housing.yml")

        self.type_ahead_api_body["variables"]["searchQuery"]['city'] = city_details_dict

        try:
            type_ahead_api_response = s.post(
                self.search_api_endpoint,
                headers=self.search_api_headers,
                json = self.type_ahead_api_body,
                params=type_ahead_api_param
            )
        except Exception as e:
            raise

        locality_details_dict = {}
        if type_ahead_api_response.status_code == 200:
            type_ahead_response_json = type_ahead_api_response.json()
            if "results" in type_ahead_response_json['data']['typeAhead'] and len(type_ahead_response_json['data']['typeAhead']['results'])>0:
                locality_details_dict = type_ahead_response_json['data']['typeAhead']['results'][0]
        else:
            raise Exception(f"Expected 200 response, but received TYPE_AHEAD_API response: {type_ahead_api_response.status_code}")

        canonical_url = locality_details_dict['canonical']


        if "-" in canonical_url:
            hash_val = canonical_url.split('-')[-1]
        else:
            page_type, entity_id = canonical_url.split('/')[-2:]

            if "hash_function" in graph_ql_dict:
                self.hash_api_body["query"] = graph_ql_dict['hash_function']
            else:
                raise Exception("type_ahead_function key is expected in config graphql_queries_housing.yml")

            self.hash_api_body["variables"]['city'] = city_details_dict
            self.hash_api_body["variables"]['pageType'] = page_type
            self.hash_api_body["variables"]['entityId'] = entity_id
            self.hash_api_body["variables"]['oldCall'] = False
            self.hash_api_body["variables"]['oldHash'] = None

            try:
                hash_api_response = s.post(
                    self.search_api_endpoint,
                    headers=self.search_api_headers,
                    json = self.hash_api_body,
                    params=hash_api_param
                )
            except Exception as e:
                raise

            if hash_api_response.status_code == 200:
                hash_response_json = hash_api_response.json()
                if "hash" in hash_response_json['data']['searchHash']:
                    hash_val = hash_response_json['data']['searchHash']['hash']
            else:
                raise Exception(f"Expected 200 response, but received GET_SEARCH_HASH_API response: {type_ahead_api_response.status_code}")

            

        if "search_function" in graph_ql_dict:
            self.search_api_body["query"] = graph_ql_dict['search_function']
        else:
            raise Exception("type_ahead_function key is expected in config graphql_queries_housing.yml")
        
        page_number = 1
        listings_extracted = 0

        self.search_api_body['variables']['hash'] = hash_val
        self.search_api_body['variables']['city'] = city_details_dict
        self.search_api_body['variables']['pageInfo'] = {
            'page': page_number,
            'size': 30
        }
        self.search_api_body['variables']['meta'] = {
            "filterMeta": {},
            "url": canonical_url,
            "shouldModifySearchResults": True,
            "pagination_flow": False,
            "enableExperimentalFlag": False,
            "isDeveloperSearch": False
        }

        try:
            search_api_res = s.post(
                self.search_api_endpoint,
                headers=self.search_api_headers,
                json = self.search_api_body,
                params=search_api_param
            )
        except Exception as e:
            raise
        

        if search_api_res.status_code == 200:
            search_result = search_api_res.json()
            self.report_obj.house_json_lst.extend(search_result['data']['searchResults']['properties'])

            total_available_listings = search_result["data"]["searchResults"]["config"]["pageInfo"]["totalCount"]
            total_current_page_listings = search_result["data"]["searchResults"]["config"]["pageInfo"]["size"]
            meta_api_resp = search_result["data"]["searchResults"]["meta"]["api"]

            """
            print(total_available_listings)
            print(total_current_page_listings)
            print(page_number)
            print(listings_extracted)
            print(meta_api_resp)
            print()
            """

            listings_extracted += total_current_page_listings
            page_number += 1

            while listings_extracted < total_available_listings and page_number<=40:
                self.search_api_body['variables']['pageInfo']['page'] = page_number
                self.search_api_body['variables']['meta']["api"] = meta_api_resp

                try:
                    search_api_res = s.post(
                        self.search_api_endpoint,
                        headers=self.search_api_headers,
                        json = self.search_api_body,
                        params=search_api_param
                    )
                except Exception as e:
                    raise

                if search_api_res.status_code == 200:
                    search_result = search_api_res.json()
                    self.report_obj.house_json_lst.extend(search_result['data']['searchResults']['properties'])

                    total_available_listings = search_result["data"]["searchResults"]["config"]["pageInfo"]["totalCount"]
                    total_current_page_listings = search_result["data"]["searchResults"]["config"]["pageInfo"]["size"]
                    meta_api_resp = search_result["data"]["searchResults"]["meta"]["api"]


                    """
                    print(total_available_listings)
                    print(total_current_page_listings)
                    print(page_number)
                    print(listings_extracted)
                    print(meta_api_resp)
                    print()
                    """

                    listings_extracted += total_current_page_listings
                    page_number += 1
                else:
                    raise Exception(f"Expected 200 response, but received SEARCH_API response: {search_api_res.status_code}")

        else:
            raise Exception(f"Expected 200 response, but received SEARCH_API response: {search_api_res.status_code}")
        
        return self.report_obj


    
if __name__ == "__main__":
    geo_service_obj = GeoLocationService()
    #country = geo_service_obj.get_country(city = 'chandkheda')
    geo_result_json = geo_service_obj.search_geo_location(city='whitefield', country='India')
    geo_service_obj.set_geo_location_boundry(geo_result_json)
    #print(country)
    print(geo_result_json)

    housing_obj = HousingCom(
                ReportingService(
                    column_mapping_cfg_fpath = "config/column_mapping_cfg_housing_com.json",
                    column_lst = [
                        'ID', 'Bedrooms', 'Bathrooms', 'Size', 
                        'House Category', 
                        'Price', 'Address', "Realtor Brokerage", "Website", "Latitude", "Longitude", "InsertedDate",
                        "SubID", "label", "SubSize", "SubPrice"
                    ],
                    summary_col_lst = ['Bedrooms', 'House Category']
                )
            )

    
    housing_obj.set_transaction_type(transaction_type='for_sale')
    housing_obj.set_geo_coordinate_boundry(geo_location_obj=geo_service_obj)
    houses_df = housing_obj.search_houses().to_dataframe()

    houses_df.to_excel('./test_1.xlsx', index=False)

    houses_df = housing_obj.transform(houses_df=houses_df)
    summary_df = housing_obj.report_obj.get_average(
        dataframe=houses_df,
        average_col_name='Price'
    )

    housing_obj.report_obj.save_excel(
                houses_df,
                "./test.xlsx",
                summary_dataframe=summary_df
            )

    print(houses_df)