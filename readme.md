### sanlexhome

This repository contains the code and assets used to construct the 
[sanskrit lexicon homepage](http://www.sanskrit-lexicon.uni-koeln.de/index.html).

At Cologne, it is the /scans/csl-homepage directory.

The script `update_version.sh` updates ../csl-orig/.version and
 is used by the next two scripts.
Thus, it should be run BEFORE the next script.

The script `redo_cologne.sh` :
* runs a python script `index_cologne.py` which generates `index_cologne.html`
* copies it to appropriate spot at Cologne.

The script `redo_xampp.sh` :
* runs a python script `index_xampp.py` which generates `index_xampp.html`
* copies it to appropriate spot in a local installation.

The url for local installation is:
 http://localhost/cologne/index.html

---------------------------------------
12-27-2022
Old: /scans/MWScan/tamil/index.html
New: /scans/csl-santam/php/index.html
Remove /cgi-bin/tamil/recherche

