
curl -O https://download.geofabrik.de/europe/poland-latest.osm.pbf
call gol build poland poland-latest.osm.pbf 

call gol query --format=geojson poland n[tourism]	> tourism.geojson
call gol query --format=geojson poland n[craft]	    > craft.geojson

python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip tourism.geojson.gz tourism.geojson
move /Y "tourism.geojson.gz" "c:\MapMarket.pl\static\"
move /Y "tourism.geojson" 	 "c:\MapMarket.pl\static\" 
 
 
move /Y "craft.geojson" 	 "c:\MapMarket.pl\static\"  

timeout 15
del poland-latest.osm.pbf