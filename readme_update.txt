
csl-homepage/readme_update.txt

02-02-2025  FRI dictionary available in specialized dictionaries
1. Add entry for FRI in indexdirs.xml
2. Revise index_xampp.py
  - add FRI to san_special 
3. Revise index_cologne.py
4. revise update_version.sh 
 4a. majorminor="2.8" -> 2.9
 4b. patchbase  1538
    cd /c/xampp/htdocs/cologne/csl-orig
    git log | grep '^commit' | wc -l
    1538 <----  change patchbase to this in update_version.sh
   
5. install on xampp server
 sh update_version.sh  # Script rewrites ../csl-orig/.version
 ===
STEP 0: majorminor=2.8, patchbase=1383
STEP 1. UPDATE THE .VERSION FILE
../csl-orig/.version revised from 2.8.0 to 2.8.155
STEP 2: RERUN REDO_XAMPP.SH OR REDO_COLOGNE.SH, AS APPROPRIATE
===
 sh redo_xampp.sh
6. push csl-homepage to github

7. install on cologne server
 sh update_version.sh  # Script rewrites ../csl-orig/.version 
 sh redo_cologne.sh 


-------------------------------------

07-07-2025  AP now public
1. check entry in indexdirs.xml  (it looks ok)
2. Revise index_xampp.py
3. Revise index_cologne.py
4. revise update_version.sh
 4a. majorminor="2.8"
 4b. patchbase  1383
    cd /c/xampp/htdocs/cologne/csl-orig
    git log | grep '^commit' | wc -l
    1383
5. install on xampp server
 sh update_version.sh  # Script rewrites ../csl-orig/.version 
 sh redo_xampp.sh
6. push csl-homepage to github

7. install on cologne server
 sh update_version.sh  # Script rewrites ../csl-orig/.version 
 sh redo_cologne.sh 


-------------------------------------

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

