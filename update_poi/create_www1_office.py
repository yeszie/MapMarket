import os
import json
from jinja2 import Template
import re
import unicodedata
import base64
import psycopg2

# Parametry połączenia z bazą danych PostgreSQL
db_params = {
    'dbname': 'x',
    'user': 'x',
    'password': 'x!',
    'host': 'x',
    'port': 'x'
}

# Funkcja do pobierania danych binarnych obrazka i konwersji na Base64
def get_thumbnail_base64(lat, lon):
    try:
        # Nawiązanie połączenia z bazą danych PostgreSQL
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        # Zapytanie SQL do pobrania danych binarnych obrazka z tabeli map_screenshots
        cursor.execute("SELECT screenshot FROM map_screenshots WHERE latitude = %s AND longitude = %s;", (lat, lon))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Zakodowanie danych binarnych w Base64
            thumbnail_base64 = base64.b64encode(result[0]).decode('utf-8')
            # Zwrócenie pełnego URL dla HTML
            return f"data:image/png;base64,{thumbnail_base64}"
        return None
    except Exception as e:
        print(f"Error fetching screenshot: {e}")
        return None

# Funkcja do czyszczenia nazw plików
def sanitize_filename(name):
    # Mapa zamiany znaków specjalnych i polskich znaków diakrytycznych
    replacements = {
        'ć': 'c', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ć': 'C', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
        'ą': 'a', 'Ą': 'A', 'ę': 'e', 'Ę': 'E', 
        ' ': '-', '&': '_and_', '@': '_at_', '%': '_percent_', '$': '_dollar_',
        '€': 'E', '+': '_', '=': '', '#': '', '!': '',
        '^': '', '~': '', '`': '', 
        '{': '', '}': '', ';': '', ',': '', '\'': '', '"': '', '©': '(c)', '®': '(r)'
    }
    
    # Zamiana znaków na odpowiedniki
    for key, value in replacements.items():
        name = name.replace(key, value)
    
    # Normalizacja unicode i usunięcie znaków akcentowanych
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    
    # Usuń znaki nowej linii i inne znaki sterujące
    name = re.sub(r'[\r\n\x00-\x1F\x7F]', '', name)
    
    # Usuń wszelkie niealfanumeryczne znaki (z wyjątkiem '-', '_')
    name = re.sub(r'[^a-zA-Z0-9\-_]', '', name)
    
    # Ogranicz długość do 254 znaków dla zgodności z systemem plików
    name = name[:254]
    
    # Usuń białe znaki na początku i końcu
    return name.strip()

# Funkcja do generowania unikalnej nazwy pliku
def get_unique_filename(folder, base_name, extension):
    if not base_name:  # Sprawdzenie, czy nazwa pliku jest pusta
        base_name = "office"
    counter = 1
    new_name = f"{base_name}{extension}"
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return new_name

# Ścieżka do folderu z danymi i do zapisywania plików HTML                          ############
data_file = 'office.geojson'                                
output_folder = 'static/office'

# Funkcja do generowania kodu HTML z danymi
def generate_html(data, template_file, output_file, all_files, index_url):
    with open(template_file, 'r', encoding='utf-8') as file:
        template_content = file.read()
    template = Template(template_content)
    data['index_url'] = index_url  # Dodaj URL do indeksu do danych
    html_content = template.render(data=data, all_files=all_files)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
        print(output_file)

# Funkcja do generowania strony indeksowej
index_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-M5YN420L44"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-M5YN420L44');
    </script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Indeks stron">
    <title>Indeks Stron - Office</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        header {
            width: 100%;
            background-color: #007bff;
            padding: 15px 0;
            text-align: center;
        }

        header h1 {
            margin: 0;
            color: white;
            font-size: 24px;
        }

        ul {
            list-style-type: none;
            padding: 0;
            margin: 20px 0;
            width: 90%;
            max-width: 800px;
        }

        li {
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fff;
            padding: 10px;
            transition: transform 0.2s;
        }

        li:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        a {
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }

        a:hover {
            text-decoration: underline;
        }

        footer {
            width: 100%;
            background-color: #f1f1f1;
            padding: 30px 0;
            text-align: center;
            font-size: 14px;
            color: #666;
            position: fixed;
            bottom: 0;
        }

        footer a {
            color: #007bff;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <header>
        <h1>Indeks Stron - Office</h1>
    </header>

    <ul>
        {% for link in links %}
            <li><a href="{{ link }}">{{ link.split('/')[-1].rsplit('.', 1)[0] }}</a></li>
        {% endfor %}
    </ul>

    <footer>
        <p><small><a href="https://MapMarket.pl">MapMarket.pl</a></small></p>
    </footer>
</body>
</html>
"""

def generate_index_page(links, output_file, output_folder):
    template = Template(index_template)
    html_content = template.render(links=links, output_folder=output_folder)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

# Wczytaj dane GeoJSON
with open(data_file, 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

# Szablon HTML
template_file = 'template.html'

# Lista wygenerowanych plików
files_generated = []

# URL do strony indeksowej
index_url = f'https://mapmarket.pl/{output_folder}/index.html'

# Procesowanie danych i generowanie plików HTML
for feature in geojson_data['features']:
    properties = feature['properties']
    name = properties.get('name', '_office_')
    description = properties.get('description', '')
    sanitized_name = sanitize_filename(name)
    base_filename = sanitized_name
    extension = '.html'
    GPS_adres = properties.get('GPS_adres', '')
    alt_map = f"{GPS_adres} [{name}]"
    
    if not sanitized_name:  # Jeśli po sanitacji nazwa jest pusta, ustaw domyślną nazwę
        base_filename = "_office_"
    
    unique_filename = get_unique_filename(output_folder, base_filename, extension)
    output_file = os.path.join(output_folder, unique_filename)
    
    #
    latitude = feature['geometry']['coordinates'][1]
    longitude = feature['geometry']['coordinates'][0]
    map_screenshot_base64 = get_thumbnail_base64(latitude, longitude)
    #
    
    data = {
        'name': name,
        'properties': properties,
        'latitude': latitude,
        'longitude': longitude,
        'google_maps_url': f'https://www.google.com/maps?q={feature["geometry"]["coordinates"][1]},{feature["geometry"]["coordinates"][0]}',
        'street_view_url': f'https://maps.googleapis.com/maps/api/streetview?size=800x600&location={feature["geometry"]["coordinates"][1]},{feature["geometry"]["coordinates"][0]}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        'street_view_url_pano': f'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={feature["geometry"]["coordinates"][1]},{feature["geometry"]["coordinates"][0]}',
        'street_view_alt': properties.get('name', 'Street View Image'),
        'canonical_url': f'https://mapmarket.pl/{output_folder}/{unique_filename}',
        'output_folder': output_folder,
        'filename': unique_filename,
        'description': description,
        'alt_map' : alt_map,
        'map_screenshot': map_screenshot_base64  # Przekazanie zakodowanego obrazka do szablonu

    }
    
    generate_html(data, template_file, output_file, files_generated, index_url)
    files_generated.append(f'https://mapmarket.pl/{output_folder}/{unique_filename}')

# Generowanie strony indeksowej
index_file = os.path.join(output_folder, 'index.html')
generate_index_page(files_generated, index_file, output_folder)

print("Pliki HTML oraz strona indeksowa zostały wygenerowane.")
