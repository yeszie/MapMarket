#usuwa ze wszystkich geojson entery i spacje zeby zmniejszyc rozmiar pliku


import os
import json
import logging

# Konfiguracja logowania do konsoli
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

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

            # Zapisz plik GeoJSON w kompaktowym formacie bez niepotrzebnych białych znaków
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, ensure_ascii=False, separators=(',', ':'))
            logging.info(f'Plik {file_name} został zaktualizowany i nadpisany.')

        except Exception as e:
            logging.error(f'Błąd podczas przetwarzania pliku {file_name}: {e}')
