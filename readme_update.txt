
csl-homepage/readme_update.txt

12-08-2023  ABCH added.
1. Add entry into indexdirs.xml
2. Revise index_xampp.py
 2a. asteriskData : add entry
 2b. pfxs_sandict
3. Revise index_cologne.py
 3a. asteriskData : add entry
 3b. pfxs_sandict
4. revise update_version.sh
 4a. majorminor="2.5"
 4b. patchbase  853 -> 999
 
 cd /c/xampp/htdocs/cologne/csl-orig
 git log | grep '^commit' | wc -l
  999
 sh update_version.sh
 # ../csl-orig/.version revised from 2.4.66 to 2.5.0
-------------------------------------
02-18-2025
# ----- local machine
sh update_version.sh
sh redo_xampp.sh
# push to github  (readme_update.txt and index_xampp.html)
git add .
git commit -m "update local homepage version 2.7.286."
git push
# ----- cologne
git pull
sh update_version.sh
sh redo_cologne.sh
#  Due to .gitignore, index_cologne.html is not tracked. So no
#  changes tracked by git.

