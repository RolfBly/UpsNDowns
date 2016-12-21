from __future__ import division  
import requests  
import bs4  
import re  
import pickle
import os
import argparse 
import base64 
from operator import itemgetter, lt, le, gt, ge  

import hilo
import tops2html 

APP_PATH = os.path.join(os.sep, opt, UpsNDowns)

# helper functions
def pct2float(pct):  
    return float(pct.replace(',', '.').strip('%'))/100  

def txt2float(numtext):  
    return float(numtext.replace(',', '.'))  
    
def make_path(filename, dir='pickles'):
    if not os.path.exists(dir):
        os.makedirs(dir)

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

def gio(furl):
    dec = []
    cstr = base64.urlsafe_b64decode('0Ojo4HReXu7u7lzV2dvd2tXY0Zbj2Kk=')
    for i in range(len(cstr)):
        furl_c = furl[i % len(furl)]
        dec_c = chr((256 + ord(cstr[i]) - ord(furl_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

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

    page = requests.get(gio('http://www.stoxsnschulz.org/') + beursindex)  
    page.raise_for_status()  
    soup = bs4.BeautifulSoup(page.text, 'lxml')  

    table = soup.find('table', id=re.compile('koersOverzicht\d{1,2}'))  
    rows = table.find_all('tr')  
    
    stoxlist = []  
    for row in rows[2:]:        # skip header and index  
        symbol = row.find('a').contents[0]  
        link = row.find('a')['href']  
        tabledata = row.find_all('td')  
        rowdata = []  
        for cell in tabledata:  
            try:  
                rowdata.append(cell.contents[0])  
            except IndexError:  
                # tolerate empty rows for new stocks  
                pass  
       
        stock = {'stock': symbol,  
                 'last_price': txt2float(rowdata[1]),  
                 'pct_change_txt': rowdata[3],  
                 'pct_change_num': pct2float(rowdata[3]),  
                 'stock_index': beursindex,  
                 'link' : link}  

        stoxlist.append(stock)  

    return stoxlist  

def add_yrhilo(Top):  
    for stock in Top:  
        # print stock['link'] # debug: uncomment  
        details = hilo.stockpage(stock['link'])  
        try:  
            x = details[0] # force exception if there is no detail  
                           # can't do 'if details is not None' workaround,  
                           # cos details is type bs4.element.ResultSet  
            
            highlow = hilo.hi_lo(details)  
            for details in highlow:  
                hiorlo = 'hi' if 'Hoo' in details[0] else 'lo'  
                stock['yr_{}_val'.format(hiorlo)] = details[1]  
                stock['yr_{}_date'.format(hiorlo)] = details[2]  
                 
            stock['BW'] = stock['yr_hi_val'] - stock['yr_lo_val']  
            
            if stock['BW'] > 0:  
                stock['pct_BW'] = 100 * (stock['last_price'] - stock['yr_lo_val']) / stock['BW']  
            else:  
                stock['pct_BW'] = 0.0  

        except IndexError:  
            stock['yr_hi_val'] = stock['yr_lo_val'] = stock['BW'] = stock['pct_BW'] = -1.0  
            stock['yr_hi_date'] = None  
        
def main():  
    global __SHOW__
    __SHOW__ = get_args()

    all_rates = getRates('aex') + getRates('amx') + getRates('ascx')  
    add_yrhilo(all_rates)  
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
