#Pobiera adresy z plikow geojson uzywajac google api
#sprawdza wszystkie gps w tabeli pobranej z plikow geojson i przypisuje numer punktu OSM

import psycopg2
import requests
import json
import os
from datetime import datetime, date

# Klucz API Google
api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Parametry połączenia z bazą danych PostgreSQL
db_params = {
    'dbname': 'x',
    'user': 'x',
    'password': 'x!',
    'host': 'x',
    'port': 'x'
}

def get_existing_location(conn, lat, lon):
    """Helper function to get existing address and geojson_id from the database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT address, geojson_id FROM locations 
        WHERE latitude = %s AND longitude = %s
    """, (lat, lon))
    result = cursor.fetchone()
    return result if result else (None, None)

def get_geojson_id(conn, lat, lon):
    """Function to get geojson_id from geojson_data for the given coordinates."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT geojson_id FROM geojson_data
        WHERE latitude = %s AND longitude = %s
    """, (lat, lon))
    result = cursor.fetchone()
    return result[0] if result else None

def get_address(api_key, lat, lon):
    """Function to get an address using Google Maps API."""
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        print(data)

        if data['status'] == 'OK':
            address = data['results'][0]['formatted_address']
            print('     Pobrano: ', address)
            return address
        else:
            print(f"Error in geocoding: {data['status']}")
            #Dodaj pauzę np 5 minut 
            return None
    except Exception as e:
        print(f"Error getting address: {e}")
        return None

def days_old(date_obj):
    """Helper function to calculate the number of days since a given date."""
    if isinstance(date_obj, date):
        date_value = date_obj
    elif isinstance(date_obj, str):
        try:
            date_value = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(f"Incorrect date format for {date_obj}. Expected 'YYYY-MM-DD'.")
    else:
        raise TypeError("Date object must be a string or datetime.date instance.")
    
    return (datetime.now().date() - date_value).days

def read_geojson_files(directory):
    """Read GeoJSON files from the given directory and extract coordinates."""
    coordinates = []
    for filename in os.listdir(directory):
        if filename.endswith('.geojson'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for feature in data.get('features', []):
                        coords = feature.get('geometry', {}).get('coordinates', [])
                        if len(coords) >= 2:
                            lon, lat = coords[0], coords[1]
                            geojson_id = feature.get('id', None)
                            coordinates.append((lat, lon, geojson_id))
            except UnicodeDecodeError as e:
                print(f"Unicode decoding error for file {filename}: {e}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for file {filename}: {e}")
    return coordinates

def add_new_locations():
    """Function to add new locations to the database if they do not exist."""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    directory = os.getcwd()  # Get the current working directory
    coords_list = read_geojson_files(directory)

    for lat, lon, geojson_id in coords_list:
        existing_address, existing_geojson_id = get_existing_location(conn, lat, lon)
        
        if existing_address:
            if existing_geojson_id is None:
                print(f"Updating geojson_id for coordinates ({lat}, {lon})")
                try:
                    cursor.execute("""
                        UPDATE locations
                        SET geojson_id = %s
                        WHERE latitude = %s AND longitude = %s
                    """, (geojson_id, lat, lon))
                    conn.commit()
                except psycopg2.Error as e:
                    print(f"Database error: {e}")
                    conn.rollback()
            print(f"Location for coordinates ({lat}, {lon}) already exists. Skipping...")
            continue

        address = get_address(api_key, lat, lon)
        if address:
            try:
                cursor.execute("""
                    INSERT INTO locations (latitude, longitude, address, checked_date, geojson_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (latitude, longitude) DO NOTHING
                """, (lat, lon, address, datetime.now().strftime('%Y-%m-%d'), geojson_id))
                conn.commit()
                print(f"Added new location for coordinates ({lat}, {lon})")
            except psycopg2.Error as e:
                print(f"Database error: {e}")
                conn.rollback()

    conn.close()

def update_addresses():
    """Function to update addresses for locations that haven't been checked recently."""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute("SELECT latitude, longitude, address, checked_date, geojson_id FROM locations")
    rows = cursor.fetchall()

    for lat, lon, address, checked_date, geojson_id in rows:
        if address and days_old(checked_date) <= 30:
            print(f"    Skipping address update for coordinates ({lat}, {lon}) because address is up-to-date (last checked {checked_date})")
            continue

        print(f"Updating address for coordinates ({lat}, {lon})")
        new_address = get_address(api_key, lat, lon)
        if new_address:
            cursor.execute("""
                UPDATE locations
                SET address = %s, checked_date = %s
                WHERE latitude = %s AND longitude = %s
            """, (new_address, datetime.now().strftime('%Y-%m-%d'), lat, lon))
            conn.commit()

    conn.close()

def main():
    add_new_locations()  # First add any new locations from GeoJSON files
    update_addresses()   # Then update existing addresses if needed

main()
