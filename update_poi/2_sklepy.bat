
call gol query --format=geojson poland n[shop]	> sklepy.geojson


python join_adres.py
python sql2geojson_GPSadres.py
python translate_geojson.py
python remove_empty_values.py
python clean_geojson_files.py

"C:\Program Files\7-Zip\7z.exe" a -tgzip sklepy.geojson.gz sklepy.geojson
move /Y sklepy.geojson.gz 					 c:\MapMarket.pl\static\

del   c:\temp\bin\static\shop\*.html
python create_www1_sklepy.py
move /Y c:\temp\bin\sklepy.geojson  		 c:\MapMarket.pl\static\ 

python clean_html_files.py
del   	   						   	 	 c:\MapMarket.pl\static\shop\*.html
move  c:\temp\bin\static\shop\*.html 	 	 c:\MapMarket.pl\static\shop\
 
timeout 60