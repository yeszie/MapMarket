#skrypt łączy pola adresowe i usuwa zbędne pola z plikow geojson

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

# Klucze, które mają być połączone i usuniete
keys_to_concatenate = {
    "railway:ref",
    "entrance",
    "dispensing",
    "check_date:opening_hours",
    "esr:user",
    "ref:csioz",
    "name:ru",
    "name:uk",
    "name:szl",
    "name:ar",
    "name:de",
    "name:en",
    "name:lt",
    "addr:street",
    "addr:place",
    "addr:housenumber",
    "addr:housename",
    "addr:unit",
    "addr:postcode",
    "addr:city",
    "addr:state",
    "addr:province",
    "addr:district",
    "addr:county",
    "addr:country",
    "addr:city:simc",
    "addr:subdistrict",
    "addr:suburb",
    "addr:street:sym_ul",
    "source:addr",
    "ref:addr",
    "ref:ruian:addr",
    "name:de",
    "name:en",
    "name:pl",
    "source",
    "payment:notes",
    "opening_hours:covid19",
    "brand:wikidata",
    "mapillary",
    "brand:wikipedia",
    "ref:storeid",
    "payment:cash",
    "payment:visa_debit",
    "payment:coins",
    "payment:credit_cards",
    "payment:debit_cards",
    "ref:rspo",
    "ref:csioz"
}

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

            # Połączenie wartości kluczy w jedno pole 'adres'
            updated = False
            for feature in geojson_data['features']:
                properties = feature['properties']
                
                # Sprawdź, czy w properties są klucze do połączenia
                if any(key in properties for key in keys_to_concatenate):
                    address_parts = [
                        properties.get("addr:housename", ""),
                        properties.get("addr:street", ""),
                        properties.get("addr:place", ""),
                        properties.get("addr:housenumber", ""),
                        properties.get("addr:unit", ""),
                        properties.get("addr:postcode", ""),
                        properties.get("addr:city", ""),
                        properties.get("addr:addr:suburb", ""),
                        properties.get("addr:state", ""),
                        properties.get("addr:province", ""),
                        properties.get("addr:district", ""),
                        properties.get("addr:county", ""),
                        properties.get("addr:country", "")
                    ]
                    # Połącz adresy w jeden ciąg tekstowy, oddzielając przecinkami
                    full_address = ', '.join(part for part in address_parts if part)
                    properties['adres'] = full_address
                    # Usuń stare klucze po połączeniu
                    for key in keys_to_concatenate:
                        if key in properties:
                            del properties[key]
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
