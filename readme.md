## UpsNDowns readme  

Ups 'N Downs is a screen-scraping exercise.  

- `ud.py` (for **U**ps and **D**owns) reads all 75 AEX, AMC, AScX stocks, and a few interesting numbers about them, from a public web site. `ud.py` calls `hilo.py`  
- `hilo.py` reads 52 week **HI**gh and **LO**w from each individual stock page on the same site. A few extra parameters are calculated for each stock.  
- When all data is collected, five shortlists are computed, and then stored as pickles. They can also be output to the console, nicely formatted (or to a file if redirected).  
- `convert2html.py` reads the pickles and output them to an html-table. That table is input for a small Flask app, StoxSNSchulz, in a repo by the same name.  

### if anyone should ask
Q: Why is this on GitHub at all?
A: Because it might be easier to deploy elsewhere. 

### License  

UpsNDowns is part of a project called Stox S.N.Schulz.  

The following license applies to the entire Stox S.N. Schulz project  

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



