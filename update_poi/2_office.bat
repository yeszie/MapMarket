
call gol query --format=geojson poland n[office]	> office.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip office.geojson.gz office.geojson
move /Y office.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\office\*.html
python create_www1_office.py
move /Y c:\temp\bin\office.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   	   						   	 	 c:\MapMarket.pl\static\office\*.html
move  c:\temp\bin\static\office\*.html 	 	 c:\MapMarket.pl\static\office\
 
