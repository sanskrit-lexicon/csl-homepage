echo "Remaking index_cologne.html"
python3 index_cologne.py indexdirs.xml index_cologne.html
echo "Copying index_cologne.html to /docs/index.html home page"
cp index_cologne.html ../../index.html
