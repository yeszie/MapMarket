
call gol query --format=geojson poland n[tourism=hotel]	> tourism_hotel.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip tourism_hotel.geojson.gz tourism_hotel.geojson
move /Y tourism_hotel.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\tourism_hotel\*.html
python create_www1_tourism_hotel.py
move /Y c:\temp\bin\tourism_hotel.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   											   	 c:\MapMarket.pl\static\tourism_hotel\*.html
move  c:\temp\bin\static\tourism_hotel\*.html 	 	 c:\MapMarket.pl\static\tourism_hotel\
 
