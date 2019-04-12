from __future__ import division  
import requests  
import bs4  
import re  
import pickle
import os
import argparse 
import gspread
from operator import itemgetter, lt, le, gt, ge  
from oauth2client.service_account import ServiceAccountCredentials

import tops2html 

# find out where we are
APP_PATH = os.path.dirname(os.path.realpath(__file__))

# helper functions
def pct2float(pct):  
    return float(pct.replace(',', '.').strip('%'))/100  

def txt2float(numtext):  
    return float(numtext.replace(',', '.'))  
    
def make_path(filename, dir='pickles'):
    pickledir = os.path.join(APP_PATH, 'pickles') 
    if not os.path.exists(pickledir):
        os.makedirs(pickledir)

    file = '{}.pkl'.format(filename)
    picklepath = os.path.join(APP_PATH, dir, file)
    return picklepath
    
def save_thing(thing, path):
    with open(path, 'wb') as f:
        pickle.dump(thing, f, pickle.HIGHEST_PROTOCOL)

def get_topX_index(lst, threshold, key='pct_change_num'):  
    for i, dic in enumerate(lst):  
        if abs(dic[key]) >= threshold:  
            pass  
        else:  
            return i  
    return i + 1  

def filter_topX(lst, threshold, key='pct_BW', op='<='):  
    ops = {'>'  : gt,  
           '>=' : ge,  
           '<'  : lt,  
           '<=' : le}  
    func = ops[op]  
    outlist = []  
    for i, dic in enumerate(lst):  
        if func(abs(dic[key]), threshold):  
           outlist.append(dic)  

    return outlist  

def make_table(Top, head, name):  
    '''Takes Top and header data, name, 
       creates neat header & table, 
       outputs it to console if __SHOW__ is True,
       saves the table data in a pickle named name.'''
       
    N = len(Top)  
    
    if not 'Alles' in head:  
        head = 'Top {} {} '.format(N, head)  
   
    hdat = head, 'change', 'price', 'yrHi', 'yrLo', 'pct_BW', 'BW', 'index'  
    if __SHOW__: 
        widthl = [28, 7, 7, 4] # column widths in hline and underline  
        widthd = {'w{}'.format(index): value for index, value in enumerate(widthl, 1)}  
        under = 8 * '='  
        hline = '  {0:{ul}<{w1}}  {1:{ul}>{w2}}  {2:{ul}>{w3}}  {3:{ul}>{w3}}  {4:{ul}>{w3}}  {5:{ul}>{w3}}  {6:{ul}>{w3}}  {7:{ul}<{w4}}'  
        print '\n'  
        print hline.format(*hdat, ul='', **widthd)  
        print hline.format(*under, ul='=', **widthd)  
        
        line = '  {:.<28}  {:>7}  {:>7.2f}  {:>7.2f}  {:>7.2f}  {:>6.1f}%  {:>7.2f}  {:<4}'  

    dlines = []
    for item in Top:  
        items = [item['stock'],  
                 item['pct_change_txt'],  
                 item['last_price'],  
                 item['yr_hi_val'],  
                 item['yr_lo_val'],  
                 item['pct_BW'],  
                 item['BW'],  
                 item['stock_index']]  

        dlines.append(items)
        if __SHOW__: 
            print line.format(*items)

    save_thing((hdat, dlines), make_path(name))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", help="Show results on console", 
                        action="store_true")
    args = parser.parse_args()
    if args.show:
        return True
    else:
        return False    
    
# scrapers    
def getRates(beursindex):  
    '''extract from stock pages: stock name, last price, pct change  
       return stock name, last price as float,  
       pct change as text and float, index name, and link to stock page.  
    '''  

    page = requests.get('http://www.beleggen.nl/' + beursindex)  
    page.raise_for_status()  
    soup = bs4.BeautifulSoup(page.text, 'lxml')  
    
    table = soup.find('table', id=re.compile('koersOverzicht\d{1,2}'))  
    rows = table.find_all('tr')  
    
    stoxlist = []  
    for row in rows[2:]:        # skip header and index  
        ticker = row.find('a').contents[0]  
        link = row.find('a')['href']
        last_price = row.find('span').contents[0]
        tabledata = row.find_all('td')  
        rowdata = []  
        for cell in tabledata:  
            try:  
                rowdata.append(cell.contents[0])
                  
            except IndexError:  
                # tolerate empty rows for new stocks  
                pass  
       
        stock = {'stock': ticker,  
                 'last_price': txt2float(last_price),  
                 'pct_change_txt': rowdata[3],  
                 'pct_change_num': pct2float(rowdata[3]),  
                 'stock_index': beursindex,  
                 'link' : link}  

        stoxlist.append(stock)  

    return stoxlist  
    
def get_52hilo():
    scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('Gspreadintro-8cc9b473b2af.json', scope)

    gc = gspread.authorize(credentials)

    sh = gc.open('AxX')
    return sh.sheet1.get_all_values()
    
def add_52hilo(Top):
    
    symbols = get_52hilo()

    for item in zip(Top, symbols):
        # print "{}\t\t{}\t\t{}".format(item[0]['stock'], item[1][0], item[1][2])
    
        item[0]['yr_hi_val'] = txt2float(item[1][4])
        item[0]['yr_lo_val'] = txt2float(item[1][5])
        item[0]['BW'] = item[0]['yr_hi_val'] - item[0]['yr_lo_val']
        if item[0]['BW'] > 0:  
            item[0]['pct_BW'] = 100 * (item[0]['last_price'] - item[0]['yr_lo_val']) / item[0]['BW']  
        else:  
            item[0]['pct_BW'] = 0.0  
        
def main():  
    global __SHOW__
    __SHOW__ = get_args()
    
    all_rates = getRates('aex') + getRates('amx') + getRates('ascx')
    all_sorted_alfa = sorted(all_rates, key=itemgetter('stock'))
    save_thing(all_sorted_alfa, make_path('alles'))
    add_52hilo(all_sorted_alfa)  
    all_sorted = sorted(all_rates, key=itemgetter('pct_change_num'), reverse=True)  
    
    # Top X climbers  
    top10_ups = all_sorted[:10]  
    N = get_topX_index(top10_ups, threshold=0.01)  
    make_table(top10_ups[:N], 'climbers', 'ups')  

    # Top X fallers  
    top10_downs = list(reversed(all_sorted[-10:]))  
    M = get_topX_index(top10_downs, threshold=0.01)  
    topX_downs = filter_topX(top10_downs[:M], threshold=30)  
    make_table(topX_downs, 'fallers, pct_BW < 30%', 'downs')  

    # Top X bandwidth, pct_BW < 40%  
    all_sorted_by_BW = sorted(all_rates, key=itemgetter('BW'), reverse=True)  
    topP_BW = filter_topX(all_sorted_by_BW[:10], threshold=40)  
    make_table(topP_BW, 'BW, pct_BW < 40%', 'BW')  

    # Top X low scale, BW > 3 euro  
    all_sorted_by_scale = sorted(all_rates, key=itemgetter('pct_BW'))  
    topX_scale_low = filter_topX(all_sorted_by_scale[:10], threshold=3, key='BW', op='>')  
    make_table(topX_scale_low, 'bottom BW, BW > 3', 'low_BW')  

    # Top X penny stock, pct_BW < 25%  
    all_sorted_by_price = sorted(all_rates, key=itemgetter('last_price'))  
    topX_cheap = filter_topX(all_sorted_by_price[:10], threshold=25)  
    make_table(topX_cheap, 'El Chipo, pct_BW < 25%', 'cheap')  

    # top10_expensive = list(reversed(all_sorted_by_price[-10:]))  
    # make_table(top10_expensive, 'DUUR!')
    tops2html.tables2html(*tops2html.get_tables())

if __name__ == "__main__":  
    main()  
