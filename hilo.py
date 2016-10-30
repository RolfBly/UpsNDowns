import requests
import bs4
import re
from datetime import date

def txt2float(numtext):
    return float(numtext.replace(',', '.'))

def match_class(target):                                                        
    def do_match(tag):                                                          
        classes = tag.get('class', [])                                          
        return all(c in classes for c in target)                                
    return do_match

def month_num2txt_NL(str):
    months = ['jan', 'feb', 'mar', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
    return months[int(str)-1]

    
def stockpage(stock):

    page=requests.get('http://www.beleggen.nl' + stock)
    page.raise_for_status()
    soup = bs4.BeautifulSoup(page.text, 'lxml')

    koersgeg = soup.find_all(match_class(["koersgegevens"]))
    
    for item in koersgeg:
        cells = item.find_all('td')
        
    # print cells # uncomment to debug
    return cells    
    
    
def hi_lo(cells):
    '''' extract high and low (year or to date), with dates, from stock detail table data cells'''
    
    def cellsfrom(offset): 
        minmax = []
        for i in cells[offset:offset+2]:
            minmax.append(i.contents[0])
            
        return minmax
        
    def parse_yrhilo(cells, prefix):
        max, datum = cells[1].split(' ')
        max = txt2float(max)
        datum = re.sub('[\(\)0]', '', datum)
        day, month_num = datum.split('-')
        month_txt = month_num2txt_NL(month_num)
        datum = '{} {} {}'.format(day, month_txt, date.today().year)
        return prefix, max, datum

    def stripzero(s):
        s = re.sub('[0]', '', s)
        return s
        
    def parse_everhilo(cells, prefix):
        nix, max, datum = cells[1].split(' ')
        max = txt2float(max)
        datum = re.sub('[\(\)]', '', datum)
        day, month_num, year = datum.split('-')
        month_txt = month_num2txt_NL(stripzero(month_num))
        datum = '{} {} {}'.format(stripzero(day), month_txt, year)
        return prefix, max, datum

        
    try: 
        if 'Hoogste jaarkoers (delayed)' in cellsfrom(13)[0]:
            hi_cells = cellsfrom(13)
            lo_cells = cellsfrom(18)
            high = parse_yrhilo(hi_cells, 'Hoo') 
            low = parse_yrhilo(lo_cells, 'Laa')
        elif 'Hoogste koers ooit' in cellsfrom(10)[0]: 
            hi_cells = cellsfrom(10)
            lo_cells = cellsfrom(15)
            high = parse_everhilo(hi_cells, 'Hoo')
            low = parse_everhilo(lo_cells, 'Laa')
        else:
            high = low = None, -1,0, None
    except IndexError: 
        high = low = None, -1,0, None
            
        
    return high, low
    

def main():
    
    stockdetails = stockpage('/BESI')
    # stockdetails = stockpage('/VastNed_Retail')
    hilo = hi_lo(stockdetails)
    for item in hilo:
        print '{}gste: {} euro op {}'.format(*item)
        
if __name__ == "__main__":
    main()
