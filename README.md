# pyRealtor

pyRealtor is a python package that provides fast an easy way to extract Multiple Listing Service (MLS) details, such as house sale/rent price, number of bedrooms, stories, ammenities nearby etc. of any city within Canada. The library provides functionality to easily store the extracted data in excel sheet for further analysis. 

pyRealtor can be used to 
- Analyze all real estate listing in a specific area.
- Find only **Open House** on a specifc day in a particular area.

## Installation

- Cloning the source code
```shell
git clone https://github.com/rachitt96/pyRealtor.git
cd pyRealtor
```

- Installing the package
```shell
pip install --upgrade .
```

### Usage

1. To get all real estate properties for sale in specific area

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Barrhaven',
    report_file_name='barrhaven_all_listings.xlsx'
)
```

2. To get only Open House listings in a specific area

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='CITY/SUBURB',
    report_file_name='FILES_TO_LOAD_LISTINGS.xlsx',
    open_house_date = 'MM/DD/YYYY'
)
```

```python
import pyRealtor

house_obj = pyRealtor.HousesFacade()
house_obj.search_save_houses(
    search_area='Barrhaven',
    report_file_name='barrhaven_all_listings.xlsx',
    open_house_date = '10/29/2023'
)
```