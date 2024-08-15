import requests

class GeoLocationService:

    def __init__(self):
        self.nominatim_api_endpoint = "https://nominatim.openstreetmap.org/search"
        self.latitude_max = None
        self.latitude_min = None
        self.longitude_max = None
        self.longitude_min = None
        self.polygon_boundry = None


    def set_geo_location_boundry(self, geo_json):

        geo_coord_1 = (
            float(geo_json['boundingbox'][0]),
            float(geo_json['boundingbox'][2])
        )
        geo_coord_2 = (
            float(geo_json['boundingbox'][1]),
            float(geo_json['boundingbox'][3])
        )

        if not ((geo_coord_1[0] >= -90 and geo_coord_1[0] <= 90) and (geo_coord_2[0] >= -90 and geo_coord_2[0] <= 90)):
            raise ValueError("Latitude of geo co-ordinate must be between -90 and 90")
        
        if not ((geo_coord_1[1] >= -180 and geo_coord_1[1] <= 180) and (geo_coord_2[1] >= -180 and geo_coord_2[1] <= 180)):
            raise ValueError("Longitude of geo co-ordinate must be between -90 and 90")
        
        self.latitude_min = min(geo_coord_1[0], geo_coord_2[0])
        self.latitude_max = max(geo_coord_1[0], geo_coord_2[0])
        self.longitude_min = min(geo_coord_1[1], geo_coord_2[1])
        self.longitude_max = max(geo_coord_1[1], geo_coord_2[1])

        if "geojson" in geo_json:
            self.polygon_boundry = geo_json["geojson"]

    def set_display_physical_location(self, physical_location: str):
        self.physical_location = physical_location

    def get_country(self, city:str):
        country_name = ""
        max_importance = 0
        api_params = {
            'city': city,
            'addressdetails': 1,
            'format': 'json'
        }

        try:
            geo_res = requests.get(
                self.nominatim_api_endpoint,
                params = api_params,
                headers={
                    'User-Agent': 'pyRealtor'
                }
            )
            for geo_json in geo_res.json():
                if geo_json["importance"] >= max_importance:
                    country_name = geo_json["address"]["country"]

        except Exception as e:
            print(e)
            raise

        return country_name


           
    def search_geo_location(self, city: str, country:str, province:str = None):
        geo_res_json = None
        api_params = {
            'city': city,
            'country': country,
            'format': 'json'
        }
        is_polygon_boundry = False

        if province:
            api_params['state'] = province

        if country.lower() == 'united states':
            api_params['polygon_geojson'] = 1
            is_polygon_boundry = True

        try:
            geo_res = requests.get(
                self.nominatim_api_endpoint,
                params = api_params,
                headers={
                    'User-Agent': 'pyRealtor'
                }
            )
            
            geo_res_json_lst = geo_res.json()
            geo_res_json = None
            max_importance = 0

            if len(geo_res_json_lst) == 0:
                raise Exception(f"pyRealtor is only for Canadian or United States region, area {city} not found in either Canada or United States")

            for geo_json in geo_res_json_lst:
                if is_polygon_boundry:
                    if (geo_json["importance"] >= max_importance) and ("geojson" in geo_json) and ("polygon" in geo_json["geojson"]["type"].lower()):
                        geo_res_json = geo_json
                        max_importance = geo_json["importance"]

                elif geo_json["importance"] >= max_importance:
                    geo_res_json = geo_json
                    max_importance = geo_json["importance"]

        except Exception as e:
            print(e)
            raise
        
        return geo_res_json