dt=$(date '+%Y%m%d%H%M%S');
echo "STEP 1. UPDATE THE .VERSION FILE."
cd ../csl-orig
echo "2.0.`git log | grep '^commit' | wc -l`" > .version

echo "STEP 2. UPDATE COLOGNE HOMEPAGE TO DISPLAY TODAY'S DATE."
cd ../csl-homepage
bash redo_xampp.sh
cd ../csl-pywork/v02

