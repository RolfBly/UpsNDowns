import pickle  
import os  
import datetime  
from jinja2 import Environment, FileSystemLoader  
from shutil import copyfile

# this is all you need to hand-edit
# WEB_PATH wordt gebruikt om de html-tabel in de site te updaten, is commented out (regel 10 en 68). 
# WEB_PATH = os.path.join(os.sep, 'mnt', 'u1', 'ud', 'stox', 'stoxapp', 'templates')
# WEB_PATH = os.path.join('O:', 'stoxsnschulz', 'stoxapp', 'templates')

# this is so we can run this both stand-alone and as a callable
APP_PATH = os.path.dirname(os.path.realpath(__file__))  

def get_tables():  
    '''retrieves table data from pickles and the last pickle's modify date'''  

    def make_path(filename):  
        # from:  \path\to\app\pickles\*.pkl  
        # ? must be absolute path in order to be scriptable? really?   
   
        mypath = os.path.join(APP_PATH, 'pickles', filename)  
        if os.path.isfile(mypath):  
            return(mypath)  
        else:  
            print '{} bestaat niet!'.format(mypath)  
            exit()  
            
    def load_thing(path):  
        with open(path, 'rb') as f:  
            return pickle.load(f)  
            
    def mod_date(path):  
        t = os.path.getmtime(path)  
        return datetime.datetime.fromtimestamp(t)  
        
    tablenames = 'ups', 'downs', 'BW', 'low_BW', 'cheap'  
    tablelist = []  
    for name in tablenames:  
        filename = '{}.pkl'.format(name)  
        mypath = make_path(filename)  
        table = load_thing(mypath)  
        tablelist.append(table)  
        
    collect_date = mod_date(mypath)  
        
    return tablelist, collect_date.strftime('%A %d %B %Y, %H:%M CET')  
    
def tables2html(tablelist, rundate):  
    '''Jinja templates are used to write to a new file instead of rendering when a request is received. Run this function whenever you need to create a static file'''  

    template_path = os.path.join(APP_PATH)  
    # tell Jinja to use the templates directory  
    env = Environment(loader=FileSystemLoader(template_path))  

    # Look for the results template  
    template = env.get_template('table_template.html')  

    # render it once. Pass in whatever values you need.  
    tablelist, rundate = get_tables()  
    html_output = template.render(rundate=rundate,  
                                  tablelist=tablelist)  

    outfile = os.path.join(APP_PATH, 'main_table.html')  
    with open(outfile, 'w') as f:  
        f.write(html_output.encode('utf-8'))  
        
    # copyfile(outfile, os.path.join(WEB_PATH, 'main_table.html'))        

def main():  
    tables2html(*get_tables())  
    
if __name__ == "__main__":  
    main() 