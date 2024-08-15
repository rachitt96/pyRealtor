import requests
from requests.adapters import HTTPAdapter, Retry

from pyRealtor.geo import GeoLocationService
from pyRealtor.report import ReportingService
from pyRealtor.proxy import Proxy
from pyRealtor.realtor import Realtor

class RealtorCa(Realtor):

    def __init__(self, report_obj: ReportingService):
        self.search_api_endpoint = "https://api2.realtor.ca/Listing.svc/PropertySearch_Post"
        self.search_api_params = {
            'Version': '7.0',
            'ApplicationId': '1',
            'CultureId': '1',
            'Currency': 'CAD',
            'RecordsPerPage': 200,
            'MaximumResults': 600
        }
        self.search_api_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "DNT": "1",
            "Host": "api2.realtor.ca",
            "Origin": "https://www.realtor.ca",
            "Pragma": "no-cache",
            "Referer": "https://www.realtor.ca/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36"
        }
        self.report_obj = report_obj

    def set_geo_coordinate_boundry(self, geo_location_obj: GeoLocationService):
        try:
            self.search_api_params["LatitudeMin"] = geo_location_obj.latitude_min
            self.search_api_params["LongitudeMin"] = geo_location_obj.longitude_min
            self.search_api_params["LatitudeMax"] = geo_location_obj.latitude_max
            self.search_api_params["LongitudeMax"] = geo_location_obj.longitude_max
            self.search_api_params["ZoomLevel"] = 10
        except Exception as e:
            raise

    def set_sort_method(self, by: str = 'listing_price', ascending_order: bool=True):
        if by.lower() not in ["listing_price", "listing_date_posted"]:
            raise ValueError("Expected value for sort arguments are 'listing_price' or 'listing_date_posted'")

        realtor_sorting_api_str = None

        try:
            if by.lower() == 'listing_price':
                realtor_sorting_api_str = "1"
            elif by.lower() == 'listing_date_posted':
                realtor_sorting_api_str = "6"
            
            if ascending_order:
                realtor_sorting_api_str += "-A"
            else:
                realtor_sorting_api_str += "-D"
            
            self.search_api_params["Sort"] = realtor_sorting_api_str
        except Exception as e:
            raise

    def set_transaction_type(self, transaction_type: str = 'for_sale'):
        if transaction_type.lower() not in ["for_sale", "for_rent", "for_sale_or_rent"]:
            raise ValueError(f"Possible values for Transaction Type argument are 'for_sale' or 'for_rent', however received {transaction_type}")
        
        transaction_type_to_id_dict = {
            'for_sale': '2',
            'for_rent': '3'
        }

        self.search_api_params["TransactionTypeId"] = transaction_type_to_id_dict[transaction_type.lower()]
        
        if transaction_type.lower() == "for_sale":
            keep_col = "Price"
            remove_col = "Rent"
        else:
            keep_col = "Rent"
            remove_col = "Price"

        if remove_col in self.report_obj.column_lst:
            self.report_obj.column_lst.remove(remove_col)
        if keep_col not in self.report_obj.column_lst:
            self.report_obj.column_lst.append(keep_col)

    def set_built_year_range(self, built_year_range: tuple):
        built_year_min, built_year_max = built_year_range
        if built_year_min:
            self.search_api_params["BuildingAgeMin"] = built_year_min
        if built_year_max:
            self.search_api_params["BuildingAgeMax"] = built_year_max

    def set_open_house_only(self, open_house_date):
        self.search_api_params["OpenHouse"] = 1
        self.search_api_params["OpenHouseStartDate"] = open_house_date
        self.search_api_params["OpenHouseEndDate"] = open_house_date

    def set_min_amount(self, new_amount, col_name):
        if col_name not in ['Price', 'Rent']:
            raise Exception(f"col_name must be either Price or Rent, however found {col_name}")
        api_param_key = f"{col_name}Min"
        self.search_api_params[api_param_key] = new_amount
    
    def search_houses(self, use_proxy = False):
        search_result = None
        json_search_payload = self.search_api_params.copy()
        current_page_number = 1


        try:
            s = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ]
            )

            s.mount('http://', HTTPAdapter(max_retries=retries))
            
            
            get_api_response = s.get(
                'https://realtor.ca/',
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                }
            )

            #print(get_api_response)

            json_search_payload['CurrentPage'] = str(current_page_number)
            s.headers.update(self.search_api_headers)

            def update_reese84_cookie(sess):
                resp = requests.post(
                    "https://www.realtor.ca/dnight-Exit-shall-Braith-Then-why-vponst-is-proc",
                    json = {
                        "solution":{
                                "interrogation":None,
                                "version":"beta"
                            },
                            "old_token":None,
                            "error":None,
                            "performance":{"interrogation":1897}
                    },
                    params = {"d": "www.realtor.ca"}
                )

                if resp.status_code == 200:
                    sess.headers.update({
                        "Cookie": f"reese84={resp.json()['token']};"
                    })
                else:
                    raise Exception(f"Status code {resp.status_code} received while updating reese84 cookie")
            
                return sess
            
            s = update_reese84_cookie(sess=s)

            if use_proxy:
                proxy = Proxy()
                proxy.set_proxies()

                while proxy.rotate_proxy():
                    try:
                        print(f"Using proxy with IP Address: {proxy.current_proxy}")
                        realtor_api_response = s.post(
                            self.search_api_endpoint,
                            headers=self.search_api_headers,
                            data = json_search_payload,
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
                    data = json_search_payload
                )

            
            if realtor_api_response.status_code == 200:
                search_result = realtor_api_response.json()
                self.report_obj.house_json_lst.extend(search_result["Results"])
                total_available_pages = search_result["Paging"]["TotalPages"]
     
                while current_page_number < total_available_pages:
                    current_page_number += 1
                    json_search_payload['CurrentPage'] = str(current_page_number)
                    
                    s = update_reese84_cookie(sess=s)
                    #time.sleep(1000)

                    if use_proxy:
                        realtor_api_response = None
                        while proxy.rotate_proxy():
                            try:
                                print(f"Using proxy with IP Address: {proxy.current_proxy}")
                                realtor_api_response = s.post(
                                    self.search_api_endpoint,
                                    headers=self.search_api_headers,
                                    data = json_search_payload,
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
                                else:
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
                            data = json_search_payload
                        )
                        #print(s.cookies.get_dict())

                    if realtor_api_response is None:
                        listings_received = len(self.report_obj.house_json_lst)
                        print(f"Total listings received: {listings_received}, no more proxies available to connect, please try after some time")
                    elif realtor_api_response.status_code == 200:
                        search_result = realtor_api_response.json()
                        self.report_obj.house_json_lst.extend(search_result["Results"])
                    
            elif realtor_api_response.status_code == 403:
                print(realtor_api_response.text)
                print("IP address is blocked by REALTOR.CA, please try using Proxy with parameter use_proxy=True")

        except Exception as e:
            raise

        return self.report_obj