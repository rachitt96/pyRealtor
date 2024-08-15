import requests
import lxml.html as lh
from lxml import etree
#import urllib2

class Proxy:

    def __init__(self):
        self.current_proxy = None
        self.available_proxies_lst = []
        self.rotation_index = 0
        self.max_rotation_index = 0
        self.proxy_provider_url = "https://free-proxy-list.net/"

    def set_proxies(self):
        response = requests.get(self.proxy_provider_url)
        doc = lh.document_fromstring(response.text)
        
        available_proxies_rows_lst = doc.xpath("//section[@id='list']//table/tbody/tr[td[7][contains(text(),'yes')]]")
        self.available_proxies_lst = [[td.text for td in tr.xpath('td')]  
            for tr in available_proxies_rows_lst]
        self.max_rotation_index = len(self.available_proxies_lst)
        print(f"Total proxies available to test: {self.max_rotation_index}")

    def rotate_proxy(self):
        if self.rotation_index >= self.max_rotation_index:
            return False
        
        proxy_str = f'{self.available_proxies_lst[self.rotation_index][0]}:{self.available_proxies_lst[self.rotation_index][1]}'
        
        try:
            proxy_check_resp = requests.get(
                "https://httpbin.org/ip", 
                proxies = {
                    'http': proxy_str, 
                    'https': proxy_str
                },
                timeout = 10
            )

            if proxy_check_resp.status_code == 200:
                print(proxy_check_resp.json())
                self.current_proxy = proxy_str
        except Exception as e:
            self.rotation_index += 1
            return self.rotate_proxy()

        self.rotation_index += 1
        
        return True

if __name__ == "__main__":
    proxy = Proxy()
    proxy.set_proxies()
    c = 0

    while c < 50:
        if proxy.rotate_proxy():
            print(proxy.current_proxy)
        c += 1
