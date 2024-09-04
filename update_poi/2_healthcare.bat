
call gol query --format=geojson poland n[healthcare]	> healthcare.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip healthcare.geojson.gz healthcare.geojson
move /Y healthcare.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\healthcare\*.html
python create_www1_healthcare.py
move /Y c:\temp\bin\healthcare.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   	   						   	 	         c:\MapMarket.pl\static\healthcare\*.html
move  c:\temp\bin\static\healthcare\*.html 	 	 c:\MapMarket.pl\static\healthcare\
 
