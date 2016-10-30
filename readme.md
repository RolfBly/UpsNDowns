## UpsNDowns readme  

Ups 'N' Downs is a screen-scraping exercise. It reads data from the Amsterdam Stock Exchange, and computes some information from it. That information can be made available on the console or in a text file, or in a separate Flask application.

- `ud.py` (ups and downs) reads all 75 AEX, AMC, AScX stocks, and some additional data, from a public web site. 
- `ud.py` calls `hilo.py` and `tops2html.py`  
- `hilo.py` reads 52 week High and Low for each stock, from each individual stock page on the same site. It also calculates a few additional  parameters for each stock.  
- When all data is collected, five shortlists are extracted, and then stored as pickles.  
- The shortlists can be output to the console, nicely formatted (or to a file if redirected), with the --show or -s command line option.  
- `tops2html.py` reads the pickles and output them to an html-table. That table is input for a Flask app called StoxSNSchulz, in a Git repository by the same name, next to this one.  
- The reasoning behind the shortlists is explained in the About-page of StoxSNSchulz.  

### License  

Copyright 2016 Rolf Blijleven  

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at  

    http://www.apache.org/licenses/LICENSE-2.0  

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.  
