# pobiera ze wszystkich geojson współrzędne i wrzuca na tabele geojson_data
# tabela geojson_data następnie jest potrzeba dla tabeli locations aby pobrało adresy z google (uzywajac API)
# z tabeli locations następnie pobierane są (innym skryptem) współrzędne do zrobienia zrzutów ekranu


import os
import json
import psycopg2
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Parametry połączenia z bazą danych PostgreSQL
db_params = {
    'dbname': 'x',
    'user': 'x',
    'password': 'x!',
    'host': 'x',
    'port': 'x'
}

def create_database():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            address TEXT,
            checked_date DATE,
            geojson_id TEXT,
            UNIQUE(latitude, longitude)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS geojson_data (
            id SERIAL PRIMARY KEY,
            geojson_id TEXT,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            data JSONB,
            checked_date DATE,
            UNIQUE(latitude, longitude)
        )
    ''')

    conn.commit()
    conn.close()

def add_missing_columns(table_name, columns):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
    existing_columns = {row[0] for row in cursor.fetchall()}

    for column, column_type in columns.items():
        if column not in existing_columns:
            print(f"Adding column {column} to table {table_name}.")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type}")

    conn.commit()
    conn.close()

def create_or_update_tables():
    create_database()

    locations_columns = {
        'geojson_id': 'TEXT',
    }
    add_missing_columns('locations', locations_columns)

    geojson_data_columns = {
        'data': 'JSONB',
    }
    add_missing_columns('geojson_data', geojson_data_columns)

def load_existing_data(table_name):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    if table_name == 'locations':
        cursor.execute(f'SELECT latitude, longitude, address, checked_date, geojson_id FROM {table_name}')
    elif table_name == 'geojson_data':
        cursor.execute(f'SELECT latitude, longitude, data, checked_date, geojson_id FROM {table_name}')
    else:
        raise ValueError("Unknown table name")

    rows = cursor.fetchall()
    data = {}
    for row in rows:
        lat, lon, address_or_data, checked_date, geojson_id = row
        coord_key = f"{lat},{lon}"
        data[coord_key] = {
            'address_or_data': address_or_data,
            'checked_date': checked_date,
            'geojson_id': geojson_id
        }
    conn.close()
    return data

def save_to_database(lat, lon, data, checked_date, geojson_id, table_name):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    try:
        if table_name == 'locations':
            cursor.execute(f'''
                INSERT INTO {table_name} (latitude, longitude, address, checked_date, geojson_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (latitude, longitude) DO UPDATE SET
                    address = EXCLUDED.address,
                    checked_date = EXCLUDED.checked_date,
                    geojson_id = EXCLUDED.geojson_id
            ''', (lat, lon, data, checked_date, geojson_id))
        elif table_name == 'geojson_data':
            cursor.execute(f'''
                INSERT INTO {table_name} (latitude, longitude, data, checked_date, geojson_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (latitude, longitude) DO UPDATE SET
                    data = EXCLUDED.data,
                    checked_date = EXCLUDED.checked_date,
                    geojson_id = EXCLUDED.geojson_id
            ''', (lat, lon, data, checked_date, geojson_id))
        conn.commit()
        print(f"Saved data for coordinates ({lat}, {lon}) to the {table_name} table.")
    except psycopg2.IntegrityError as e:
        print(f"IntegrityError: {e}")
    except Exception as e:
        print(f"Error saving data for coordinates ({lat}, {lon}): {e}")
    finally:
        conn.close()

def get_coordinates_from_geojson(geojson_file):
    with open(geojson_file, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)
    
    coordinates_list = []
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'Point':
            lon, lat = feature['geometry']['coordinates']
            geojson_id = feature.get('id', None)
            coordinates_list.append((lat, lon, geojson_id, json.dumps(feature)))
    
    return coordinates_list

def process_file(geojson_file, existing_geojson_data):
    print(f"Processing file: {geojson_file}")
    coordinates_list = get_coordinates_from_geojson(geojson_file)
    current_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Current date: {current_date}")

    for index, (lat, lon, geojson_id, feature_data) in enumerate(coordinates_list, start=1):
        coord_key = f"{lat},{lon}"

        # Wyświetlenie postępu
        total_entries = len(coordinates_list)
        print(f"Processing entry {index} of {total_entries}: Coordinates ({lat}, {lon})")

        if coord_key in existing_geojson_data:
            db_checked_date = existing_geojson_data[coord_key]['checked_date']
            print(f"Database checked_date: {db_checked_date}")
            if db_checked_date != current_date:
                print(f"Updating GeoJSON data for coordinates ({lat}, {lon})")
                save_to_database(lat, lon, feature_data, current_date, geojson_id, "geojson_data")
            else:
                print(f"Skipping GeoJSON update for coordinates ({lat}, {lon}) because data is up-to-date")
        else:
            print(f"Adding new GeoJSON data for coordinates ({lat}, {lon})")
            save_to_database(lat, lon, feature_data, current_date, geojson_id, "geojson_data")

def process_geojson_files(folder_path):
    existing_geojson_data = load_existing_data("geojson_data")

    geojson_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith('.geojson')]

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(process_file, geojson_file, existing_geojson_data) for geojson_file in geojson_files]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")

# Utworzenie bazy danych PostgreSQL i aktualizacja tabel
create_or_update_tables()

# Przetwarzanie plików GeoJSON i zapis do bazy danych PostgreSQL
folder_path = "."  # Można dostosować ścieżkę
process_geojson_files(folder_path)