majorminor="2.9"  # major and minor part of semantic version.
# minor number is same as number of dictionaries added to
# the base collection developed at Cologne.
# LAN, ARMH, PWKVN, LRV, ABCH, ACPH, ACSJ, FRI
patchbase=1538
echo "STEP 0: majorminor=$majorminor, patchbase=$patchbase"
# patchbase. This is number of csl-orig commits at time majorminor changed.
# We can compute this (in csl-orig) initially by this command in csl-orig
# git log | grep '^commit' | wc -l
#
echo "STEP 1. UPDATE THE .VERSION FILE"
cd ../csl-orig
versionold=`cat .version`
echo "versionold=$versionold"
ncommit=`git log | grep '^commit' | wc -l`
patch=$((ncommit-patchbase)) # patch relative to majorminor
versionnew="$majorminor.$patch"  # new version
echo $versionnew > .version
echo "../csl-orig/.version revised from $versionold to $versionnew"

cd ../csl-homepage
echo "STEP 2: RERUN REDO_XAMPP.SH OR REDO_COLOGNE.SH, AS APPROPRIATE"
