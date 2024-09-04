#Pobiera adres z tabeli locations i dodaje do plików geojson do pola GPS_adres.

import os
import psycopg2
import json
import logging

# Konfiguracja logowania do konsoli i pliku
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Parametry połączenia z bazą danych PostgreSQL
db_params = {
    'dbname': 'x',
    'user': 'x',
    'password': 'x!',
    'host': 'x',
    'port': 'x'
}

# Połączenie z bazą danych
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    logging.info('Połączenie z bazą danych zostało nawiązane.')
except Exception as e:
    logging.error(f'Błąd połączenia z bazą danych: {e}')
    raise

# Pobieranie danych z tabeli locations, które mają uzupełnione adresy
try:
    cursor.execute("""
        SELECT geojson_id, address
        FROM locations
        WHERE address IS NOT NULL
    """)
    location_records = cursor.fetchall()
    logging.info('Dane z tabeli locations zostały pobrane.')
except Exception as e:
    logging.error(f'Błąd podczas pobierania danych z tabeli locations: {e}')
    raise

# Przygotowanie słownika z adresami do szybkiego wyszukiwania
address_dict = {record[0]: record[1] for record in location_records}
logging.info('Słownik adresów został przygotowany.')

# Przetwarzanie wszystkich plików GeoJSON w bieżącym folderze
folder_path = '.'
files = [f for f in os.listdir(folder_path) if f.endswith('.geojson')]

if not files:
    logging.info('Brak plików GeoJSON w bieżącym folderze.')
else:
    for file_name in files:
        try:
            logging.info(f'Rozpoczynanie przetwarzania pliku {file_name}...')
            
            # Wczytaj plik GeoJSON
            with open(file_name, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            logging.info(f'Plik {file_name} został wczytany.')

            # Aktualizacja pliku GeoJSON na podstawie danych z PostgreSQL
            updated = False
            for feature in geojson_data['features']:
                feature_id = feature['id']
                
                # Sprawdź, czy istnieje odpowiadający rekord w bazie danych
                if feature_id in address_dict:
                    # Dodaj lub zaktualizuj pole 'GPS_adres' w properties
                    feature['properties']['GPS_adres'] = address_dict[feature_id]
                    updated = True

            if updated:
                # Nadpisz oryginalny plik GeoJSON
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(geojson_data, f, ensure_ascii=False, indent=2)
                logging.info(f'Plik {file_name} został zaktualizowany i nadpisany.')
            else:
                logging.info(f'Plik {file_name} nie wymagał aktualizacji.')

        except Exception as e:
            logging.error(f'Błąd podczas przetwarzania pliku {file_name}: {e}')

# Zamknięcie połączenia z bazą danych
try:
    cursor.close()
    conn.close()
    logging.info('Połączenie z bazą danych zostało zamknięte.')
except Exception as e:
    logging.error(f'Błąd podczas zamykania połączenia z bazą danych: {e}')
