<p align='center'>
    <img src="https://github.com/rachitt96/pyRealtor/blob/main/pyRealtor.png?raw=true" width="300" height="300" />
</p>


[![PyPI](https://img.shields.io/pypi/v/pyrealtor?label=pypi)](https://pypi.org/project/pyRealtor/)
[![Downloads](https://img.shields.io/pepy/dt/pyrealtor
)](https://pepy.tech/project/pyRealtor)
[![Python](https://img.shields.io/badge/Python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://badge.fury.io/py/pyrealtor)
[![PyPI - License](https://img.shields.io/pypi/l/pyrealtor?color=yellow)](https://github.com/rachitt96/pyRealtor/blob/main/LICENSE.md)




pyRealtor is a python package that provides fast and easy way to extract Multiple Listing Service (MLS) details from REALTOR.CA and REALTOR.COM, such as house sale/rent price, number of bedrooms, stories, ammenities nearby etc. of any city / region within Canada or United States. The library provides functionality to easily store the extracted data in excel sheet for further analysis. 

pyRealtor can be used to 
- Analyze and extract all real estate listing in Canada or United States.
- Find only **Open House** on a specifc day in a particular area.

## Installing

- The easiest way to install the library is to execute (preferably in a virtualenv) the command:

```shell
pip install pyRealtor
```

- From the source code
```shell
git clone https://github.com/rachitt96/pyRealtor.git
cd pyRealtor
python setup.py install
```


### Usage

1. To get all real estate properties for sale in specific area

If the area is within Canada, then pyRealtor will fetch listings from **REALTOR.CA**

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Barrhaven'
)
```

If the area is within **United States**, then pyRealtor will fetch listings from **REALTOR.COM** 

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Bentonville'
)
```

If the city/area name is common between United States and Canada, then by default pyRealtor will extract listings from either country. To externally request pyRealtor to fetch listing from a specific country:

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Ottawa',
    country='Canada'
)
```

RELTOR.CA API has the rate limit, and it may block IP in case you trigger API multiple times in short period. In that case, you can use `use_proxy` argument. 

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Barrhaven',
    use_proxy=True
)
```

2. To get only **Open House** listings in a specific area

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='CITY/SUBURB',
    open_house_date = 'MM/DD/YYYY'
)
```

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Barrhaven',
    open_house_date = '10/29/2023'
)
```

### Terms of Use

pyRealtor is a tool to extract, filter and analyze publicly accessible MLS listings provided by REALTOR.CA. More information on the use of this data can be found on REALTOR.CA website: [https://www.realtor.ca/terms-of-use](https://www.realtor.ca/terms-of-use)


> "REALTOR.CA website/database is a copyright-protected work which is owned by CREA. Part of the contents of REALTOR.CA website/database, including all real estate listings and related information, images and photographs (collectively, "Listing Content"), are also protected by copyright, which is owned by the CREA members who supplied the content and/or by third parties, and is reproduced in REALTOR.CA website/database under license. The contents of REALTOR.CA website/database, including the Listing Content, are intended for the private, non-commercial use by individuals. Any commercial use of the website/database, including the Listing Content, in whole or in part, directly or indirectly, is specifically forbidden except with the prior written authority of the owner of the copyright."

