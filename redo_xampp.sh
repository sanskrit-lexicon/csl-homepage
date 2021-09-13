echo "Remaking index_xampp.html"
python3 index_xampp.py indexdirs.xml index_xampp.html
echo "Copying index_xampp.html to /docs/index.html home page"
cp index_xampp.html ../index.html
