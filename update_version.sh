echo "STEP 1. UPDATE THE .VERSION FILE."
cd ../csl-orig
echo "2.0.`git log | grep '^commit' | wc -l`" > .version

cd ../csl-homepage
echo "STEP 2: RERUN REDO_XAMPP.SH OR REDO_COLOGNE.SH, AS APPROPRIATE"
