import requests

class GeoLocationService:

    def __init__(self):
        self.nominatim_api_endpoint = "https://nominatim.openstreetmap.org/search"
        self.latitude_max = None
        self.latitude_min = None
        self.longitude_max = None
        self.longitude_min = None

    def set_geo_location_boundry(self, geo_coordinate_1: tuple, geo_coordinate_2: tuple):
        if not ((geo_coordinate_1[0] >= -90 and geo_coordinate_1[0] <= 90) and (geo_coordinate_2[0] >= -90 and geo_coordinate_2[0] <= 90)):
            raise ValueError("Latitude of geo co-ordinate must be between -90 and 90")
        
        if not ((geo_coordinate_1[1] >= -180 and geo_coordinate_1[1] <= 180) and (geo_coordinate_2[1] >= -180 and geo_coordinate_2[1] <= 180)):
            raise ValueError("Longitude of geo co-ordinate must be between -90 and 90")

        self.latitude_min = min(geo_coordinate_1[0], geo_coordinate_2[0])
        self.latitude_max = max(geo_coordinate_1[0], geo_coordinate_2[0])
        self.longitude_min = min(geo_coordinate_1[1], geo_coordinate_2[1])
        self.longitude_max = max(geo_coordinate_1[1], geo_coordinate_2[1])

    def set_display_physical_location(self, physical_location: str):
        self.physical_location = physical_location
           
    def search_geo_location(self, city: str, province:str = None, country:str = 'Canada'):
        geo_res_json = None
        api_params = {
            'city': city,
            'country': country,
            'format': 'json'
        }

        if province:
            api_params['state'] = province

        try:
            geo_res = requests.get(
                self.nominatim_api_endpoint,
                params = api_params,
                headers={
                    'User-Agent': 'pyRealtor'
                }
            )
            #print(geo_res)
            #print(geo_res.text)
            geo_res_json_lst = geo_res.json()
            geo_res_json = None
            max_importance = 0

            for geo_json in geo_res_json_lst:
                if "canada" in geo_json["display_name"].lower() and geo_json["importance"] >= max_importance:
                    geo_res_json = geo_json
                    max_importance = geo_json["importance"]

        except Exception as e:
            print(e)
            raise
        
        return geo_res_json