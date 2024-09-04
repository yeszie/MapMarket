
call gol query --format=geojson poland n[railway=station]	> railway_station.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip railway_station.geojson.gz railway_station.geojson
move /Y railway_station.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\railway_station\*.html
python create_www1_railway_station.py
move /Y c:\temp\bin\railway_station.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   											   	 c:\MapMarket.pl\static\railway_station\*.html
move  c:\temp\bin\static\railway_station\*.html 	 	 c:\MapMarket.pl\static\railway_station\
 
timeout 10