# -*- coding: utf-8 -*-

'''
    This only needs to run on every third friday of march, june, september and december, 
    that is, when the composition of the Amsterdam Stock Exchange indexes AEX, AMX, and AScX may change.
    
    - read stoxlist = list of dicts with stock info from .\pickles\alles.pkl, 
    - retrieve symbollist with names and symbols from http://www.aandelencheck.nl/aandelen/
    - match symbols to stock names
    - make list containing 
    
        stoxlist stock name, symbollist name found, symbol with exchange name, 
        Google finance formula for price, 52 week high, 52 week low
    
    - generate AxX.csv and upload it to google doc AxX. 

    All this is because the 52-week values in stoxlist (from beleggen.nl) are useless: they're reset on january 1st. 
    
'''

import pickle
import requests
import bs4
import os
import sys
import argparse
import gspread
from operator import itemgetter
from oauth2client.service_account import ServiceAccountCredentials

APP_PATH = os.path.dirname(os.path.realpath(__file__))  

SPECIALS = [{'name': 'Aegon',             'symbol': 'AGN'},
            {'name': 'Ahold Delhaize',    'symbol': 'AD'},
            {'name': 'ASMI',              'symbol': 'ASM'},
            {'name': 'Avantium',          'symbol': 'AVTX'},
            {'name': 'Hunter Douglas',    'symbol': 'HDG'},
            {'name': 'KasBank',           'symbol': 'KA'},
            {'name': 'Nieuwe Steen Inv.', 'symbol': 'NSI'},
            {'name': 'Takeaway.com',      'symbol': 'TKWY'},
            {'name': 'VastNed Retail',    'symbol': 'VASTN'},
           ]

CORRECTION = [{'name': 'Air France-KLM',    'symbol': 'EPA:AF'},
              {'name': 'Ahold',             'symbol': 'AD'},
              {'name': 'Van Lanschot',      'symbol': 'VLK'},
              {'name': 'VolkerWessels',     'symbol': 'KVW'},
              {'name': 'Unibail Rodamco Westfield', 'symbol': 'URW'}

             ] 

def upload():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('Gspreadintro-8cc9b473b2af.json', scope)
    gc = gspread.authorize(credentials)
    sh = gc.open('AxX')

    with open('AxX.csv', 'r') as f:
        p = f.read()
        
    gc.import_csv(sh.id, p)
             
def load_all():

    def pickle_path(filename):  
        mypath = os.path.join(APP_PATH, 'pickles', filename)  
        if os.path.isfile(mypath):  
            return(mypath)  
        else:  
            print '{} bestaat niet!'.format(mypath)  
            exit()  
            
    def load_thing(path):  
        with open(path, 'rb') as f:  
            return pickle.load(f)  
    
    return load_thing(pickle_path('alles.pkl')) 
    
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", help="Show results on console", 
                        action="store_true")
    args = parser.parse_args()
    if args.show:
        return True
    else:
        return False    
    
def get_symlist():
    '''retrieve list of stock names and symbols'''
    page = requests.get('http://www.aandelencheck.nl/aandelen/')
    page.raise_for_status()  
    soup = bs4.BeautifulSoup(page.text, 'lxml')  

    table = soup.find('tbody')  
    rows = table.find_all('tr')
    
    symlist = []
    nosyms = []
    for row in rows:
        record = row.find_all('td')
        name = record[1].find('a').contents[0]
        try: 
            symbol = record[3].contents[0]
            symlist.append({'name': name, 'symbol': symbol})    
        except IndexError:
            nosyms.append(name)
            
    return symlist, nosyms

# helper for lookup()    
def fetch(name, symbols, key):
    '''retrieve name by dict[key] in list of dicts symbols'''
    return next((
            item 
            for item in symbols 
            if name.strip('.') in item[key]
            or name.split()[0] in item[key]
        ), None)

def methods(entry, symbols):
    yield next((item for item in symbols if entry['stock'] == item['name']), None)
    yield fetch(entry['stock'], symbols, 'name')
    yield fetch(entry['stock'].upper(), symbols, 'symbol')
    yield fetch(entry['stock'], SPECIALS, 'name')        
        
def lookup(stox, symbols):
    '''lookup symbol for stock name'''
    hits = []
    misses = []
    for entry in stox:
        for symbol in methods(entry, symbols):
            try:
                hits.append({'source': entry['stock'],
                             'found' : symbol['name'],
                             'symbol': symbol['symbol']})
                break
            except TypeError:
                continue
        else:
            misses.append(entry['stock'])

    for entry in CORRECTION:
        fetch(entry['name'], hits, 'source').update({'symbol': entry['symbol']})
        
    for entry in hits:
        if not ':' in entry['symbol']:
            extsym = '{}{}'.format('EPA:', entry['symbol'])
            entry.update({'symbol': extsym})

    # sort result by stock name
    hits_sorted = sorted(hits, key=itemgetter('source')) 

    # convert to list of tuples so as to retain order
    hitsl = []
    for i in hits_sorted:
        hitsl.append((i['source'], i['found'], i['symbol']))
    
    return hitsl, misses  
    
def show(hits):
    line = '{0:25} {1:40} {2:10}'
    for item in hits: 
        print line.format(*item)  

def save_csv(tuplist): 
    # head = 'source,found,symbol,price,high52,low52\n'
    line = '{0},{1},{2},=GoogleFinance("{2}"; "Price"),\
         =GoogleFinance("{2}"; "high52"),\
         =GoogleFinance("{2}"; "low52")\n'
         
    with open('AxX.csv', 'w') as f:
        # f.write(head)
        for item in tuplist:
            f.write(line.format(*item))
            
    upload()        
        
def main():
    global __SHOW__
    __SHOW__ = get_args()

    stoxlist = load_all()
    symbollist, nosyms = get_symlist()
    hits, misses = lookup(stoxlist, symbollist)
    save_csv(hits)
    
    if __SHOW__: 
        show(hits)

    if misses:
        print '\nmisses: \n', misses

if __name__ == "__main__":
    main()
    