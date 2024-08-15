import requests
from requests.adapters import HTTPAdapter, Retry
import pkg_resources
import yaml
import json
import datetime

from pyRealtor.geo import GeoLocationService
from pyRealtor.report import ReportingService
from pyRealtor.proxy import Proxy
from pyRealtor.realtor import Realtor

class RealtorCom(Realtor):

    def __init__(self, report_obj: ReportingService):
        self.search_api_endpoint = "https://www.realtor.com/api/v1/rdc_search_srp"
        self.search_api_params = {
            'client_id': 'rdc-search-for-sale-search',
            'schema': 'vesta'
        }
        self.search_api_headers = {
            "Accept": "application/json, text/javascript",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.realtor.com",
            "Sec-Fetch-Site": "same-origin"
        }
        self.search_api_body = {
            "query": "",
            "variables": {
                "limit": 200,
                "offset": 0,
                "client_data": {
                    "device_data": {
                        "device_type": "desktop"
                    }
                },
                "query": {
                    "primary": True,
                    "status": [],
                    "boundary": {}
                }
            }
        }
        self.report_obj = report_obj

    def set_geo_coordinate_boundry(self, geo_location_obj: GeoLocationService):
        if geo_location_obj.polygon_boundry:
            self.search_api_body["variables"]["query"]["boundary"] = geo_location_obj.polygon_boundry
        else:
            raise TypeError("REALTOR.COM expects Polygon boundary to search real estate listings")

    def set_sort_method(self, by: str = 'relevant', ascending_order: bool=True):
        if by.lower() not in ["listing_price", "listing_date_posted", "relevant"]:
            raise ValueError("Expected value for sort arguments are 'relevant', 'listing_price' or 'listing_date_posted'")
        
        order = ''
        if ascending_order:
            order = "asc"
        else:
            order = "desc"


        if by.lower() == "relevant":
            self.search_api_body["variables"]["sort_type"] = "relevant"
        elif by.lower() == "listing_price":
            self.search_api_body["variables"]["sort"] = [{
                "field": "list_price",
                "direction": order
            }]
        elif by.lower() == "listing_date_posted":
            self.search_api_body["variables"]["sort"] = [{
                "field": "list_date",
                "direction": order
            }]


    def set_transaction_type(self, transaction_type: str = 'for_sale'):
        if transaction_type.lower() not in ["for_sale", "for_rent"]:
            raise ValueError(f"Possible values for Transaction Type argument are 'for_sale' or 'for_rent', however received {transaction_type}")

        if transaction_type.lower() == 'for_sale':
            self.search_api_params["client_id"] = "rdc-search-for-sale-search"
            self.search_api_body["variables"]["query"]["status"].append("for_sale")
        else:
            self.search_api_params["client_id"] = "rdc-search-rentals-search"
            self.search_api_body["variables"]["query"]["status"].append("for_rent")

    def set_min_amount(self, new_amount: float, col_name: str = None):
        self.search_api_body["variables"]["query"]["list_price"] = {
            "min": new_amount
        }

    def set_open_house_only(self, open_house_date: str):
        if open_house_date != datetime.datetime.strptime(open_house_date, "%Y-%m-%d").strftime("%Y-%m-%d"):
            raise ValueError(f"Open House Date is Expected in YYYY-MM-DD format, however received {open_house_date}")
        
        self.search_api_params["open_house"]["min"] = open_house_date
        self.search_api_params["open_house"]["max"] = open_house_date


    def search_houses(self, use_proxy = False):
        search_result = None
        self.search_api_body["query"] = ""

        with pkg_resources.resource_stream('pyRealtor', 'config/graphql_queries.yml') as graph_ql_yaml:
            try:
                search_params_dict = yaml.safe_load(graph_ql_yaml)
                search_query = search_params_dict["search_function_graphql"]
                search_cols = search_params_dict["search_houses_columns"]

                search_cols.format(
                        EXTRA_PROPERTIES_COLUMNS = ''
                    )
                
                search_query_formatted = search_query.format(
                    SEARCH_COLUMNS = search_cols.format(
                        EXTRA_PROPERTIES_COLUMNS = ''
                    )
                )
            except yaml.YAMLError as exc:
                print(exc)
                raise

        self.search_api_body["query"] = search_query_formatted

        json_search_payload = self.search_api_body.copy()

        current_limit = 200
        current_offset = 0

        try:
            s = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ]
            )

            s.mount('https://', HTTPAdapter(max_retries=retries))
            s.headers.update(self.search_api_headers)

            json_search_payload["variables"]["limit"] = current_limit
            json_search_payload["variables"]["offset"] = current_offset

            if use_proxy:
                proxy = Proxy()
                proxy.set_proxies()

                while proxy.rotate_proxy():
                    try:
                        print(f"Using proxy with IP Address: {proxy.current_proxy}")
                        realtor_api_response = s.post(
                            self.search_api_endpoint,
                            headers=self.search_api_headers,
                            json = json_search_payload,
                            params = self.search_api_params,
                            proxies = {
                                'http': proxy.current_proxy, 
                                'https': proxy.current_proxy
                            }
                        )

                        if realtor_api_response.status_code == 200:
                            break
                        elif realtor_api_response.status_code == 403:
                            print(f"Proxy {proxy.current_proxy} is blocked by REALTOR.CA")
                            continue

                    except requests.exceptions.ChunkedEncodingError as chunkEncodingException:
                        continue
                    except requests.exceptions.ProxyError as proxyException:
                        continue
                    except requests.exceptions.ConnectionError as connectionException:
                        continue
            else:
                realtor_api_response = s.post(
                    self.search_api_endpoint,
                    headers=self.search_api_headers,
                    json = json_search_payload,
                    params = self.search_api_params
                )

            print(realtor_api_response.status_code)

            if realtor_api_response.status_code == 200:
                search_result = realtor_api_response.json()
                self.report_obj.house_json_lst.extend(search_result["data"]["home_search"]["properties"])

                total_available_listings = search_result["data"]["home_search"]["total"]
                total_current_page_listings = search_result["data"]["home_search"]["count"]

                while total_current_page_listings > 0 or current_offset < total_available_listings:
                    print(current_offset, total_available_listings, total_current_page_listings)

                    current_offset += total_current_page_listings
                    json_search_payload["variables"]['offset'] = current_offset

                    if use_proxy:
                        realtor_api_response = None
                        while proxy.rotate_proxy():
                            try:
                                print(f"Using proxy with IP Address: {proxy.current_proxy}")
                                realtor_api_response = s.post(
                                    self.search_api_endpoint,
                                    headers=self.search_api_headers,
                                    json = json_search_payload,
                                    params = self.search_api_params,
                                    proxies = {
                                        'http': proxy.current_proxy, 
                                        'https': proxy.current_proxy
                                    }
                                )

                                if realtor_api_response.status_code == 200:
                                    break
                                elif realtor_api_response.status_code == 403:
                                    print(f"Proxy {proxy.current_proxy} is blocked by REALTOR.CA")
                                    continue

                            except requests.exceptions.ChunkedEncodingError as chunkEncodingException:
                                continue
                            except requests.exceptions.ProxyError as proxyException:
                                continue
                            except requests.exceptions.ConnectionError as connectionException:
                                continue
                    else:
                        realtor_api_response = s.post(
                            self.search_api_endpoint,
                            headers=self.search_api_headers,
                            json = json_search_payload,
                            params = self.search_api_params
                        )

                    #print(realtor_api_response.status_code)
                    if realtor_api_response is None:
                        listings_received = len(self.report_obj.house_json_lst)
                        print(f"Total listings received: {listings_received}, no more proxies available to connect, please try after some time")
                    elif realtor_api_response.status_code == 200:
                        search_result = realtor_api_response.json()
                        self.report_obj.house_json_lst.extend(search_result["data"]["home_search"]["properties"])

                        total_available_listings = search_result["data"]["home_search"]["total"]
                        total_current_page_listings = search_result["data"]["home_search"]["count"]
                    elif realtor_api_response.status_code == 403:
                        print("IP address is blocked by REALTOR.COM, please try using Proxy with parameter use_proxy=True")

            elif realtor_api_response.status_code == 403:
                print("IP address is blocked by REALTOR.COM, please try using Proxy with parameter use_proxy=True")

        except Exception as e:
            raise

        return self.report_obj