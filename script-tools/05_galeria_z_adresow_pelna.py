#Tworzy plik galerii

import os
import yaml
from datetime import datetime

# Ścieżka do pliku YAML
yaml_file_path = "adresy_galeria.yml"

# Wczytanie danych z pliku YAML
if not os.path.exists(yaml_file_path):
    raise FileNotFoundError(f"Plik YAML '{yaml_file_path}' nie został znaleziony.")

with open(yaml_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# Ścieżka do folderu ze zdjęciami
folder_path = r"C:\test123\tools\FotoOriginal"
relative_folder_path = "/thumbnails"
fullsize_folder_path = "/foto"

# Tworzenie folderu na wygenerowane pliki HTML
output_folder = r"C:\test123\static\foto"
os.makedirs(output_folder, exist_ok=True)

# Generowanie plików HTML dla każdego zdjęcia
for i, item in enumerate(data):
    filename = item.get('filename')
    address = item.get('address')
    latitude = item.get('latitude')
    longitude = item.get('longitude')

    # Ścieżka do pliku
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        print(f"Plik '{file_path}' nie istnieje.")
        continue

    # Ścieżka względna do pliku
    relative_file_path = os.path.join(relative_folder_path, filename)
    fullsize_file_path = os.path.join(fullsize_folder_path, filename)

    # Nazwa pliku bez rozszerzenia
    file_name_pure = os.path.splitext(os.path.basename(filename))[0]

    # Data pliku w formacie MM_RRRR
    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%m_%Y')

    # Link do mapy
    map_link = f"http://mapmarket.pl/#18/{latitude}/{longitude}"

    # Nazwy plików HTML dla poprzedniego i następnego zdjęcia
    prev_filename = f"{data[i-1]['filename']}" if i > 0 else None
    next_filename = f"{data[i+1]['filename']}" if i < len(data) - 1 else None

    prev_html_filename = f"{os.path.splitext(prev_filename)[0]}.html" if prev_filename else None
    next_html_filename = f"{os.path.splitext(next_filename)[0]}.html" if next_filename else None

    # Generowanie sekcji z miniaturkami
    thumbnails_html = ""
    for thumb_item in data:
        thumb_filename = thumb_item.get('filename')
        thumb_address = thumb_item.get('address')
        thumb_file_name_pure = os.path.splitext(thumb_filename)[0]
        thumb_relative_file_path = os.path.join(relative_folder_path, thumb_filename)
        
        thumbnails_html += f"""
        <div class="thumbnail">
            <a href="{thumb_file_name_pure}.html" title="{thumb_address}">
                <img src="{thumb_relative_file_path}" alt="{thumb_address}" loading="lazy">
            </a>
        </div>
        """

    # Treść HTML dla pojedynczego zdjęcia
    single_html_content = f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Zdjęcie lokalizacji: {address}.">
        <meta name="keywords" content="zdjęcia, galeria, lokalizacja, {address}">
        <title>MapMarket.pl - {address}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                color: #333;
            }}
            .container {{
                width: 90%;
                margin: auto;
                overflow: hidden;
            }}
            .photo {{
                text-align: center;
                margin: 20px 0;
            }}
            .photo img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ccc;
                padding: 10px;
                background: #fff;
            }}
            .navigation {{
                display: flex;
                justify-content: space-between;
                margin: 20px 0;
            }}
            .breadcrumbs {{
                margin: 10px 0;
            }}
            .breadcrumbs a {{
                text-decoration: none;
                color: #0275d8;
                margin: 0 5px;
            }}
            .map {{
                width: 100%;
                height: 400px;
                margin: 20px 0;
            }}
            .thumbnails {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
            }}
            .thumbnail {{
                width: calc(20% - 10px);
                border: 1px solid #ddd;
                padding: 5px;
                text-align: center;
            }}
            .thumbnail img {{
                max-width: 100%;
                height: auto;
            }}
            @media (max-width: 768px) {{
                .thumbnail {{
                    width: calc(33.333% - 10px);
                }}
            }}
            @media (max-width: 480px) {{
                .thumbnail {{
                    width: calc(50% - 10px);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="breadcrumbs">
                <a href="/">Mapa</a> / <a href="/galeria">Galeria</a> / {address}
            </div>
            <h1>{address}</h1>
            <div class="photo">
                <img src="{fullsize_file_path}" alt="{address}">
                <p>Data: {file_date} &nbsp;&nbsp;&nbsp;&nbsp; Adres: {address}</p>
                <p><a href="{map_link}" target="_self" title="{address}">Pokaż na mapie</a></p>
            </div>
            <div class="navigation">
                {'<a href="'+prev_html_filename+'">Poprzednie</a>' if prev_html_filename else '<span>Poprzednie</span>'}
                {'<a href="'+next_html_filename+'">Następne</a>' if next_html_filename else '<span>Następne</span>'}
            </div>
            <div class="thumbnails">
                {thumbnails_html}
            </div>
            <small><center>
                <a href="/">MapMarket.pl</a>
                <a href="/oferty_dzialek">Oferty działek</a>
            </center></small>
        </div>
    </body>
    </html>
    """

    # Zapisanie pojedynczego pliku HTML
    single_html_file_path = os.path.join(output_folder, f"{file_name_pure}.html")
    with open(single_html_file_path, 'w', encoding='utf-8') as file:
        file.write(single_html_content)

# Generowanie strony głównej galerii
gallery_html_content = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Galeria zdjęć z lokalizacji.">
    <meta name="keywords" content="zdjęcia, galeria, lokalizacja, zdjęcia lokalizacji">
    <title>MapMarket.pl - Galeria zdjęć</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            width: 90%;
            margin: auto;
            overflow: hidden;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        .thumbnail {
            width: calc(33.333% - 20px);
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            background-color: #fff;
        }
        .thumbnail img {
            max-width: 100%;
            height: auto;
        }
        .thumbnail p {
            margin: 10px 0 0;
        }
        @media (max-width: 768px) {
            .thumbnail {
                width: calc(50% - 20px);
            }
        }
        @media (max-width: 480px) {
            .thumbnail {
                width: 100%;
            }
        }
        .links a {
            text-decoration: none;
            color: #0275d8;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Galeria zdjęć</h1>
        <a href="/galeria_zdjec_wedlug_kodow_pocztowych">galeria zdjec wedlug unikalnych kodów pocztowych</a><br>
        <a href="/galeria_zdjec_wedlug_ulic">galeria zdjec wedlug unikalnych ulic</a><br>
        <div class="gallery">
"""

# Dodanie miniaturek do galerii
for item in data:
    filename = item.get('filename')
    address = item.get('address')
    file_name_pure = os.path.splitext(os.path.basename(filename))[0]
    relative_file_path = os.path.join(relative_folder_path, filename)
    
    # Data pliku w formacie MM_RRRR dla strony głównej
    file_date = datetime.fromtimestamp(os.path.getmtime(os.path.join(folder_path, filename))).strftime('%m_%Y')

    gallery_html_content += f"""
    <div class="thumbnail">
        <a href="foto/{file_name_pure}.html" title="{address}">
            <img src="{relative_file_path}" alt="{address}" loading="lazy" id="_{file_name_pure}">
        </a>
        <p>Data: {file_date} &nbsp;&nbsp;&nbsp;&nbsp; Adres: {address}</p>
        <p><a href="http://mapmarket.pl/#18/{item.get('latitude')}/{item.get('longitude')}" target="_self">Pokaż na mapie</a></p>
    </div>
    """

# Zakończenie HTML strony głównej galerii
gallery_html_content += """
        </div>
        
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
      
        
        
        <small><center>
            <a href="/">MapMarket.pl</a>
            <a href="/oferty_dzialek">Oferty działek</a>
        </center></small>
    </div>
</body>
</html>
"""

# Zapisanie pliku HTML strony głównej galerii
gallery_html_file_path = os.path.join(os.path.dirname(output_folder), "galeria_zdjec.html")
with open(gallery_html_file_path, 'w', encoding='utf-8') as file:
    file.write(gallery_html_content)

print(f"Pliki HTML dla zdjęć oraz strona główna galerii zostały wygenerowane w folderze {output_folder}")
