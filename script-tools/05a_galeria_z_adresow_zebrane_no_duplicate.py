#Galeria w innej wersji

import os
import yaml
import re
from datetime import datetime

# Ścieżka do pliku YAML
yaml_file_path = "adresy_galeria.yml"

# Wczytanie danych z pliku YAML
if not os.path.exists(yaml_file_path):
    raise FileNotFoundError(f"Plik YAML '{yaml_file_path}' nie został znaleziony.")

with open(yaml_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# Ścieżki
folder_path = r"C:\test123\tools\FotoOriginal"
relative_folder_path = "/thumbnails"
fullsize_folder_path = "/foto"

# Funkcja do wyodrębniania kodu pocztowego
def extract_postal_code(address):
    match = re.search(r'\b\d{2}-\d{3}\b', address)
    return match.group(0) if match else None

# Tworzenie unikalnych adresów na podstawie kodu pocztowego
unique_addresses = {}
for item in data:
    address = item['address']
    postal_code = extract_postal_code(address)
    
    if postal_code:
        # Ścieżka do pliku
        file_path = os.path.join(folder_path, item['filename'])
        
        # Jeśli adres nie jest jeszcze w słowniku, dodaj go
        if postal_code not in unique_addresses:
            unique_addresses[postal_code] = item
        else:
            # Porównanie daty modyfikacji
            existing_item = unique_addresses[postal_code]
            existing_file_path = os.path.join(folder_path, existing_item['filename'])
            
            if os.path.getmtime(file_path) > os.path.getmtime(existing_file_path):
                unique_addresses[postal_code] = item

# Tworzenie HTML
html_content = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Galeria zdjęć z lokalizacji, gdzie każde zdjęcie jest unikalne według kodu pocztowego, wyświetlane w porządku najnowszych dat modyfikacji">
    <meta name="keywords" content="zdjęcia, galeria, lokalizacja, zdjęcia lokalizacji">
    <title>MapMarket.pl - Galeria zdjęć według kodów pocztowych</title>
    <style>
        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .photo {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            width: calc(33.333% - 20px); /* Responsywność dla trzech zdjęć w rzędzie */
        }
        .photo img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        @media (max-width: 768px) {
            .photo {
                width: calc(50% - 20px); /* Dwa zdjęcia w rzędzie na mniejszych ekranach */
            }
        }
        @media (max-width: 480px) {
            .photo {
                width: 100%; /* Jedno zdjęcie w rzędzie na małych ekranach */
            }
        }
    </style>
</head>
<body>
    <h1>Galeria zdjęć z lokalizacji, gdzie każde zdjęcie jest unikalne według kodu pocztowego, wyświetlane w porządku najnowszych dat modyfikacji</h1> 
    <p><a href="/galeria">Pełna galeria bez filtrowania</a></p>
    <div class="gallery" id="gallery">
"""

for item in unique_addresses.values():
    filename = item['filename']
    address = item['address']
    latitude = item['latitude']
    longitude = item['longitude']
    
    # Ścieżka do pliku
    file_path = os.path.join(folder_path, filename)
    
    if not os.path.exists(file_path):
        print(f"Plik '{file_path}' nie istnieje.")
        continue

    # Ścieżka względna do pliku
    relative_file_path = os.path.join(relative_folder_path, filename)
    # Zmiana linku do pliku HTML zamiast pliku obrazka
    html_file_name = os.path.splitext(filename)[0] + ".html"
    fullsize_file_path = os.path.join(fullsize_folder_path, html_file_name)
    
    # Nazwa pliku
    file_name = os.path.basename(file_path)
    
    # Data pliku w formacie MM_RRRR
    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%m_%Y')
    
    # Link do mapy
    map_link = f"http://mapmarket.pl/#18/{latitude}/{longitude}"

    # Dodanie zdjęcia i opisu do HTML
    html_content += f"""
    <div class="photo" data-src="{relative_file_path}" data-address="{address}" data-map-link="{map_link}" data-file-name="{file_name}" data-file-date="{file_date}">
        <!-- Placeholder for JavaScript to fill in content -->
    </div>
    """

# Zakończenie HTML
html_content += """
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const gallery = document.getElementById('gallery');
            const photos = Array.from(gallery.getElementsByClassName('photo'));

            photos.forEach(photo => {
                const src = photo.getAttribute('data-src');
                const address = photo.getAttribute('data-address');
                const mapLink = photo.getAttribute('data-map-link');
                const fileName = photo.getAttribute('data-file-name');
                const fileDate = photo.getAttribute('data-file-date');
                // Zmiana linku do pliku HTML zamiast pliku obrazka
                const htmlLink = `/foto/${fileName.replace('.JPG', '.html').replace('.jpg', '.html')}`;

                photo.innerHTML = `
                    <a href="${htmlLink}" target="_self" title="${address}">
                        <img src="${src}" alt="${address}" loading="lazy">
                    </a>
                    <p>
                    Data : ${fileDate}       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    Adres: ${address}          
                    </p>
                    <p>
                    <a href="${mapLink}">Pokaż na mapie</a>
                    </p>
                `;
            });
        });
    </script>  
    
<p>
    <small><center>
        <a href="/">MapMarket.pl</a>
        <a href="/oferty_dzialek">Oferty działek</a>
    </center><small>
</p>
</body>
</html>
"""

# Zapisanie do pliku HTML
html_file_path = "galeria_zdjec_wedlug_kodow_pocztowych.html"
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"Galeria zdjęć została zapisana do pliku {html_file_path}")
