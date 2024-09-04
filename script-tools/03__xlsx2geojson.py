#na podstawie wypełnionego odpowiednio arkusza excela tworzy odpowiedni plik geojson (ogłoszenia sprzedaży nieruchomości)


import pandas as pd
from geojson import Feature, Point, FeatureCollection
import json

def convert_xlsx_to_geojson(input_file, output_file):
    # Wczytanie danych z pliku XLSX
    df = pd.read_excel(input_file, sheet_name='Arkusz1')  # Zmodyfikuj nazwę arkusza, jeśli trzeba

    # Inicjalizacja listy dla obiektów GeoJSON
    features = []

    # Przetwarzanie każdego wiersza w ramce danych
    for index, row in df.iterrows():
        properties = {}
        coordinates = []

        # Przetwarzanie kolumn w wierszu
        for column, value in row.items():
            if column.lower() == 'longitude':
                coordinates.append(float(value))  # Konwertowanie na float, aby zapewnić poprawne współrzędne
            elif column.lower() == 'latitude':
                coordinates.append(float(value))  # Konwertowanie na float, aby zapewnić poprawne współrzędne
            else:
                properties[column] = str(value)  # Konwersja wartości do stringa

        # Tworzenie obiektu GeoJSON Feature dla każdego wiersza
        if coordinates:
            point = Point(coordinates)
            feature = Feature(geometry=point, properties=properties)
            features.append(feature)

    # Tworzenie kolekcji obiektów GeoJSON
    feature_collection = FeatureCollection(features)

    # Zapis do pliku GeoJSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(feature_collection, f, ensure_ascii=False)

    print(f'Konwersja zakończona. GeoJSON zapisany do: {output_file}')

# Przykład użycia funkcji
if __name__ == '__main__':
    input_excel_file = 'ogloszenia_nieruchomosci.xlsx'  # Podaj nazwę swojego pliku XLSX
    output_geojson_file = r'C:\test123\static\output.geojson'  # Nazwa pliku GeoJSON do zapisu

    convert_xlsx_to_geojson(input_excel_file, output_geojson_file)
