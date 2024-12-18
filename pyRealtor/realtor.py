from abc import ABC, abstractmethod

from pyRealtor.geo import GeoLocationService


class Realtor(ABC):
    @abstractmethod
    def set_geo_coordinate_boundry(self, geo_location_obj: GeoLocationService):
        pass

    @abstractmethod
    def set_sort_method(self, by: str, ascending_order: bool):
        pass

    @abstractmethod
    def set_transaction_type(self, transaction_type: str):
        pass

    @abstractmethod
    def set_min_amount(self, new_amount, col_name):
        pass

    @abstractmethod
    def set_open_house_only(self, open_house_date):
        pass

    @abstractmethod
    def transform(self, df):
        pass

    @abstractmethod
    def search_houses(self, use_proxy = False):
        pass


