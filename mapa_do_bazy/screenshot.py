#pobiera z bazy screenshot map i tworzy plik który je wyświetla (html)

import psycopg2
import base64

# Parametry do połączenia z bazą danych
db_params = {
    'dbname': 'xxx',
    'user': 'xxxxx',
    'password': 'xxxxxx!',
    'host': 'xxxx',
    'port': 'xxxxx'
}

def connect_to_db():
    conn = psycopg2.connect(**db_params)
    return conn

def fetch_all_screenshots():
    conn = connect_to_db()
    screenshots = []
    try:
        with conn.cursor() as cursor:
            query = "SELECT latitude, longitude, screenshot FROM map_screenshots;"
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                latitude, longitude, screenshot = row
                screenshots.append((latitude, longitude, screenshot))
    finally:
        conn.close()
    return screenshots

def create_html_file(screenshots, output_html_file='screenshot.html'):
    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en">\n')
        f.write('<head>\n')
        f.write('    <meta charset="UTF-8">\n')
        f.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        f.write('    <title>Map Screenshots</title>\n')
        f.write('    <style>\n')
        f.write('        body { font-family: Arial, sans-serif; margin: 20px; }\n')
        f.write('        .container { display: flex; flex-wrap: wrap; gap: 10px; }\n')
        f.write('        .image-wrapper { border: 1px solid #ddd; border-radius: 5px; padding: 5px; }\n')
        f.write('        img { max-width: 100%; height: auto; display: block; }\n')
        f.write('    </style>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('    <h1>Map Screenshots</h1>\n')
        f.write('    <div class="container">\n')

        for latitude, longitude, screenshot_data in screenshots:
            # Encode the screenshot as base64
            base64_image = base64.b64encode(screenshot_data).decode('utf-8')
            image_data_url = f'data:image/png;base64,{base64_image}'
            # Write image with coordinates
            f.write('        <div class="image-wrapper">\n')
            f.write(f'            <h2>Latitude: {latitude}, Longitude: {longitude}</h2>\n')
            f.write(f'            <img src="{image_data_url}" alt="Screenshot">\n')
            f.write('        </div>\n')

        f.write('    </div>\n')
        f.write('</body>\n')
        f.write('</html>\n')

    print(f"Plik HTML został zapisany do: {output_html_file}")

# Pobierz wszystkie zrzuty ekranów z bazy danych
screenshots = fetch_all_screenshots()

# Utwórz plik HTML zawierający obrazy
create_html_file(screenshots)
