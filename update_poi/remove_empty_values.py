import json
import os

def remove_empty_properties(properties):
    # Tworzymy nowy słownik bez pustych kluczy
    return {k: v for k, v in properties.items() if v}

def process_geojson(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    for feature in geojson_data['features']:
        # Usuwanie pustych kluczy z sekcji 'properties'
        feature['properties'] = remove_empty_properties(feature['properties'])
    
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

def process_all_geojson_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.geojson'):
            input_file = os.path.join(directory, filename)
            process_geojson(input_file)
            print(f'Przetworzono plik: {filename}')

# Przykład użycia
geojson_directory = '.'  # Zmień na ścieżkę do katalogu z plikami GeoJSON
process_all_geojson_files(geojson_directory)
