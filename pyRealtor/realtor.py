import requests

from pyRealtor.geo import GeoLocationService
from pyRealtor.report import ReportingService

class RealtorService:

    def __init__(self, report_obj: ReportingService):
        self.search_api_endpoint = "https://api2.realtor.ca/Listing.svc/PropertySearch_Post"
        self.search_api_params = {
            'Version': '7.0',
            'ApplicationId': '1',
            'CultureId': '1',
            'Currency': 'CAD',
            'RecordsPerPage': 200
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

    def set_sort_method(self, by: str, ascending_order: bool=True):
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

    def search_houses(self):
        search_result = None
        json_search_payload = self.search_api_params.copy()
        current_page_number = 1


        try:
            s = requests.Session()

            
            
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

            s.headers.update(self.search_api_headers)

            #print(s.cookies.get_dict())
            

            """
            reeser84_token_res = s.post(
                "https://www.realtor.ca/dnight-Exit-shall-Braith-Then-why-vponst-is-proc",
                params={'d': 'www.realtor.ca'},
                json = {"solution":{"interrogation":None,"version":"beta"},"old_token":None,"error":None,"performance":{"interrogation":1897}}
            )
            if reeser84_token_res.status_code == 200:
                token = reeser84_token_res.json()["token"]
                s.headers.update({'reese84': token})
            print(reeser84_token_res.status_code)
            print(reeser84_token_res.text)
            sys.exit(0)
            """

            json_search_payload['CurrentPage'] = str(current_page_number)
            realtor_api_response = s.post(
                self.search_api_endpoint,
                headers=self.search_api_headers,
                data = json_search_payload
            )

            
            if realtor_api_response.status_code == 200:
                search_result = realtor_api_response.json()
                self.report_obj.house_json_lst.extend(search_result["Results"])

                

                total_available_pages = search_result["Paging"]["TotalPages"]

                #print(total_available_pages)
                while current_page_number < total_available_pages:
                    current_page_number += 1
                    json_search_payload['CurrentPage'] = str(current_page_number)
                    
                    #time.sleep(1000)

                    realtor_api_response = s.post(
                        self.search_api_endpoint,
                        headers=self.search_api_headers,
                        data = json_search_payload
                    )
                    #print(s.cookies.get_dict())

                    if realtor_api_response.status_code == 200:
                        search_result = realtor_api_response.json()
                        self.report_obj.house_json_lst.extend(search_result["Results"])
                    else:
                        print(realtor_api_response.status_code)
                        raise
        except Exception as e:
            raise

        return self.report_obj