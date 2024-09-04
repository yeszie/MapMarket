import os
import psycopg2
from psycopg2 import sql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw
import io
import time
from datetime import datetime, timedelta

# Parametry do połączenia z bazą danych
db_params = {
    'dbname': 'xxxxxx',
    'user': 'xxxxx',
    'password': 'xxxxxxx!',
    'host': 'xxxxx',
    'port': 'xxxxxx'
}

# Funkcja do łączenia się z bazą danych
def connect_to_db():
    conn = psycopg2.connect(**db_params)
    return conn

# Funkcja do tworzenia tabeli, jeśli nie istnieje
def create_table_if_not_exists():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # Tworzenie tabeli map_screenshots
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS map_screenshots (
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                screenshot BYTEA,
                date DATE NOT NULL,
                PRIMARY KEY (latitude, longitude)
            );
            '''
            cursor.execute(create_table_query)
            conn.commit()
    finally:
        conn.close()


import random

# Funkcja do pobierania współrzędnych, które nie mają jeszcze zrzutów ekranu, w losowej kolejności
def get_coordinates_from_db():
    conn = connect_to_db()
    coordinates = []
    try:
        with conn.cursor() as cursor:
            # Pobierz współrzędne z tabeli locations, które nie mają jeszcze zrzutu ekranu
            query_locations = """
                SELECT l.latitude, l.longitude
                FROM locations l
                LEFT JOIN map_screenshots ms
                ON l.latitude = ms.latitude AND l.longitude = ms.longitude
                WHERE ms.latitude IS NULL
                ORDER BY RANDOM();
            """
            cursor.execute(query_locations)
            coordinates += cursor.fetchall()

            # Pobierz współrzędne z tabeli geojson_data, które nie mają jeszcze zrzutu ekranu
            query_geojson = """
                SELECT g.latitude, g.longitude
                FROM geojson_data g
                LEFT JOIN map_screenshots ms
                ON g.latitude = ms.latitude AND g.longitude = ms.longitude
                WHERE ms.latitude IS NULL
                ORDER BY RANDOM();
            """
            cursor.execute(query_geojson)
            coordinates += cursor.fetchall()

            # Tasowanie listy współrzędnych
            random.shuffle(coordinates)

    finally:
        conn.close()
    return coordinates


# Funkcja do usuwania starego zdjęcia z bazy danych
def delete_old_screenshot(latitude, longitude):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            delete_query = sql.SQL(
                "DELETE FROM map_screenshots WHERE latitude = %s AND longitude = %s;"
            )
            cursor.execute(delete_query, (latitude, longitude))
            conn.commit()
    finally:
        conn.close()

# Funkcja do zapisywania zrzutu ekranu w bazie danych
def save_screenshot_to_db(latitude, longitude, screenshot_data):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            insert_query = sql.SQL(
                "INSERT INTO map_screenshots (latitude, longitude, screenshot, date) VALUES (%s, %s, %s, %s) ON CONFLICT (latitude, longitude) DO UPDATE SET screenshot = EXCLUDED.screenshot, date = EXCLUDED.date;"
            )
            date = datetime.now().date()
            cursor.execute(insert_query, (latitude, longitude, psycopg2.Binary(screenshot_data), date))
            conn.commit()
    finally:
        conn.close()

import uuid

def print_processing_stats():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # Liczba wszystkich współrzędnych w tabelach locations i geojson_data
            total_query = """
                SELECT 
                    (SELECT COUNT(*) FROM locations) +
                    (SELECT COUNT(*) FROM geojson_data) AS total_records;
            """
            cursor.execute(total_query)
            total_records = cursor.fetchone()[0]
            
            # Liczba rekordów z obrazkami w tabeli map_screenshots
            processed_query = "SELECT COUNT(*) FROM map_screenshots;"
            cursor.execute(processed_query)
            processed_records = cursor.fetchone()[0]
            
            # Liczba rekordów bez obrazków
            to_process_records = total_records - processed_records
            
            # Obliczenie udziału procentowego
            if total_records > 0:
                percentage_left = (to_process_records / total_records) * 100
            else:
                percentage_left = 0.0
            
            # Wyświetlenie statystyk
            print(f"Łączna liczba rekordów: {total_records}")
            print(f"Liczba przetworzonych rekordów (z obrazkami): {processed_records}")
            print(f"Liczba rekordów do przetworzenia: {to_process_records}")
            print(f"Udział procentowy pozostałych do przetworzenia: {percentage_left:.2f}%")
    
    finally:
        conn.close()

# Funkcja do robienia zrzutu ekranu mapy
def take_map_screenshot(latitude, longitude):
    try:
        # Konfiguracja WebDrivera
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Uruchom przeglądarkę w trybie bezgłowym
        chrome_options.add_argument("--window-size=1600,1200")  # Rozmiar okna przeglądarki
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # URL do OSM z określonymi współrzędnymi
        zoom_level = 18  # Poziom powiększenia mapy
        url = f'https://www.openstreetmap.org/#map={zoom_level}/{latitude}/{longitude}'
        
        # Otwórz stronę
        driver.get(url)
        
        # Zwiększ czas oczekiwania na załadowanie mapy do 30 sekund
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'map'))
        )
        
        # Dodatkowe opóźnienie, aby upewnić się, że mapa się w pełni załadowała
        time.sleep(5)  # Czekaj dodatkowe 5 sekund
        
        # Generowanie unikalnej nazwy pliku na podstawie UUID
        unique_id = uuid.uuid4()
        screenshot_path = f'full_map_screenshot_{unique_id}.png'
        
        # Zrób zrzut ekranu
        driver.save_screenshot(screenshot_path)
        
        # Dodaj okrąg na środku przed przycięciem
        with Image.open(screenshot_path) as img:
            width, height = img.size
            draw = ImageDraw.Draw(img)
            marker_radius = 0  # promień okręgu
            center_x, center_y = width // 2, height // 2
            draw.ellipse(
                (center_x - marker_radius, center_y - marker_radius, center_x + marker_radius, center_y + marker_radius),
                outline='red', width=3  # kolor i szerokość linii okręgu
            )
            
            # Przycięcie obrazu (jeśli to konieczne)
            crop_percentage = 0.50  # procent przycięcia
            left = width * ((1 - crop_percentage) / 2)
            top = height * ((1 - crop_percentage) / 2)
            right = width * (1 - (1 - crop_percentage) / 2)
            bottom = height * (1 - (1 - crop_percentage) / 2)
            cropped_img = img.crop((left, top, right, bottom))
            
            # Konwersja obrazu do bajtów
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format='PNG')
            screenshot_data = img_byte_arr.getvalue()
        
        # Usuń ewentualnie istniejący stary zrzut ekranu
        delete_old_screenshot(latitude, longitude)
        
        # Zapisz do bazy danych
        save_screenshot_to_db(latitude, longitude, screenshot_data)
    
    except Exception as e:
        print(f"Wystąpił błąd przy robieniu zrzutu ekranu. Błąd: {e}")
    finally:
        driver.quit()
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


# Główna część skryptu
create_table_if_not_exists()
coordinates = get_coordinates_from_db()

for latitude, longitude in coordinates:
    # Sprawdź, czy istnieje już zrzut ekranu w bazie danych i czy jest nowszy niż 30 dni
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            query = "SELECT date FROM map_screenshots WHERE latitude = %s AND longitude = %s;"
            cursor.execute(query, (latitude, longitude))
            result = cursor.fetchone()
            if result:
                last_update_date = result[0]
                if datetime.now().date() - last_update_date <= timedelta(days=30):
                    print(f"Zrzut ekranu dla współrzędnych ({latitude}, {longitude}) jest aktualny. Pomijam.")
                    continue
    finally:
        conn.close()
    
    # Wykonaj zrzut ekranu
    take_map_screenshot(latitude, longitude)
    
    print_processing_stats()
