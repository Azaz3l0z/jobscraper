import os
import re
import json
import requests
import pandas as pd

class Scraper(object):
    def __init__(self, url: str, pages: int, compare_list: pd.DataFrame, set) -> None:
        self.url = url
        self.pages = pages
        self.json_file = compare_list
        self.data = pd.DataFrame({})
        
        self.__get_ads()

    # Misc
    def __get_ads(self):
        self.ads: list = []
        # We paginate over n pages and get a the script that build the page
        session = requests.Session()
        start = '<script>window.__INITIAL_PROPS__ = JSON.parse("'
        end = '");</script><script>window.__INITIAL_CONTEXT_VALUE__ =' 

        for n in range(1, self.pages + 1):
            r = session.get(self.url.format(pagina=n))
            html = r.text

            if '¡Vaya! Han volado los anuncios' in html:
                break
            else:
                json_data = html[html.find(start) + len(start): 
                                html.find(end)]
                json_data = json_data.replace('\\', '')

                # We remove description tags (They cause many problems)
                json_data = self.delete_tag(json_data, '"description":', '","')
                json_data = self.delete_tag(json_data, '"seoTitle":', '","')

                json_data = re.sub(r'((?<![:,\[{])")(?![:\],}])', '', json_data)
                json_data = re.sub(r'\s\d{2}"(?!(,"))', '', json_data)                
                          
                ads = json.loads(json_data)['adListPagination']['adList']['ads']
                
                self.ads.extend(ads)  
        self.data['ads'] = self.ads   

    def to_csv(self, name: str):        
        self.data.drop(columns=['ads']).to_csv(name)

    # Set tags
    def set_all(self):
        self.set_title()
        self.set_phones()
        self.set_urls()

    def set_title(self):
        titles = []
        for ad in self.ads:
            title = ad['title']
            titles.append(title)
        
        self.data['Title'] = titles

    def set_urls(self):
        urls = []
        for ad in self.ads:
            url = 'www.milanuncios.com' + \
                '/cocineros-y-camareros/se-ofrece-recepcionista-444751622.htm'
            urls.append(url)
        
        self.data['URL'] = urls
    
    def set_phones(self):
        phones = []
        for ad in self.data['ads']:
            if 'firstPhoneNumber' in ad:
                phone = ad['firstPhoneNumber']
            else:
                phone = None
            phones.append(phone)
        self.data['Phones'] = phones

    # Filters
    def filter_all(self):
        self.filter_new()
        self.filter_phones()

    def filter_new(self):
        for i, ad in enumerate(self.data['ads']):
            if not ad['isNew']:
                self.data.drop(i)

    def filter_phones(self):
        if 'Phones' not in self.data:
            self.set_phones()
        drop = []
        for i, phone in enumerate(self.data['Phones']):
            if phone == None:
                drop.append(i)
            
        self.data.drop(drop, inplace=True)
    
    @staticmethod
    def delete_tag(json_data: str, ini_str: str, end_str):
        while (ini_str in json_data):
            ini_idx = json_data.find(ini_str)
            end_idx = json_data[ini_idx:].find(end_str) + ini_idx +\
                len(end_str) - 1
            json_data = json_data[:ini_idx]+json_data[end_idx:]

        return json_data