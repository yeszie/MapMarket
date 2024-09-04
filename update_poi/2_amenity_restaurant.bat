
call gol query --format=geojson poland n[amenity=restaurant]	> amenity_restaurant.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip amenity_restaurant.geojson.gz amenity_restaurant.geojson
move /Y amenity_restaurant.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\amenity_restaurant\*.html
python create_www1_amenity_restaurant.py
move /Y c:\temp\bin\amenity_restaurant.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   						 c:\MapMarket.pl\static\amenity_restaurant\*.html
move  c:\temp\bin\static\amenity_restaurant\*.html 	 	 c:\MapMarket.pl\static\amenity_restaurant\
 
