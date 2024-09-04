import json
import os

# Przykładowy słownik tłumaczeń kluczy
translation_dict_keys = {
    "colour": "kolor",
    "butcher": "rzeźnik",
    "bench": "ławka",
    "building": "budynek",
    "shop": "sklep",
    "amenity": "udogodnienie",
    "craft": "rzemiosło",
    "service": "usługa",
    "cuisine": "kuchnia",
    "tourism": "turystyka",
    "religion": "religia",
    "ref": "odnośnik",
    "social_facility": "ośrodek społeczny",
    "toilets": "toalety",
    "wheelchair": "dostępność dla wózków inwalidzkich",
    "roof": "dach",
    "railway": "kolej",
    "subway": "metro",
    "station": "stacja",
    "platforms": "perony",
    "network": "sieć",
    "operator": "operator",
    "public_transport": "transport publiczny",
    "shelter": "schronienie",
    "smoking": "palenie",
    "opening_hours": "godziny otwarcia",
    "uic_ref": "odnośnik UIC",
    "website": "strona internetowa",
    "brand": "marka",
    "train": "pociąg",
    "healthcare":"opieka zdrowotna",
    "pharmacy": "apteka",
    "office":"biuro",
    "speciality": "specjalizacja",
    "lawyer":"prawnik"

}

# Przykładowy słownik tłumaczeń wartości
translation_dict_values = {
    "I":"1",
    "II":"2",
    "III":"3",
    "IV":"4",
    "V":"5",
    "VI":"6",
    "VII":"7",
    "VIII":"8",
    "IX":"9",
    "X":"10",
    "XI":"11",
    "XII":"12",
    "plumber":"hydraulik",
    "association":"stowarzyszenie",
    "charity":"działalność charytatywna",
    "townhall":"ratusz",
    "government":"administracja rządowa",
    "energy_supplier":"dostawca energii",
    "doctors": "przychodnia lekarska",
    "optometrist":"optometrysta",
    "jewish":"żydowska",
    "international":"międzynarodowa",
    "microbrewery":"browar rzemieślniczy",
    "takeaway":"na wynos",
    "outdoor_seating":"miejsca na zewnątrz",
    "indoor_seating":"miejsca wewnątrz",
    "ngo":"organizacja pozarządowa",
    "estate_agent":"pośrednik nieruchomości",
    "insurance":"ubezpieczenia",
    "office":"biuro",
    "educational_institution":"instytucja edukacyjna",
    "lawyer":"prawnik",
    "honorary_consul":"konsul honorowy",
    "diplomatic":"dyplomatyczne",
    "floor":"piętro",
    "occupational_therapist":"terapeuta zajęciowy",
    "psychotherapist":"psychoterapeuta",
    "ophthalmology":"okulistyka",
    "rehabilitation":"rehabilitacja",
    "gynaecology":"ginekologia",
    "orthopaedics":"ortopedia",
    "veterinary":"weterynarz",
    "laboratory":"laboratorium",
    "healthcare":"opieka zdrowotna",
    "dentist":"dentysta",
    "stomatology":"stomatologia",
    "sample_collection":"pobieranie próbek",
    "clinic":"klinika",
    "pharmacy":"apteka",
    "limited":"ograniczona",
    "train": "pociąg",
    "butcher": "mięsny",
    "red": "czerwony",
    "green": "zielony",
    "blue": "niebieski",
    "school": "szkoła",
    "yes": "tak",
    "no": "nie",
    "clothes" : "odzieżowy",
    "shoes" : "obuwniczy",
    "convenience":"spożywczy",
    "beauty": "kosmetyczny",
    "car_repair": "warsztat samochodowy",
    "wholesale":"hurtownia",
    "pastry":"cukiernia",
    "restaurant": "restauracja",
    "bailiff": "komornik",
    "interior_decoration":"dekoracja wnętrz",
    "educational_institution":"instytucja edukacyjna",
    "bakery":"piekarnia",
    "medical_supply":"zaopatrzenie medyczne",
    "car_parts":"części samochodowe",
    "tattoo":"tatuaże",
    "hairdresser":"fryzjer",
    "furniture":"meble",
    "hearing_aids":"aparaty słuchowe",
    "variety_store":"wielobranżowy",
    "printer_ink":"tusze do drukarki",
    "financial_advisor":"doradca finansowy",
    "notary":"notariusz",
    "funeral_directors":"zakład pogrzebowy",
    "florist":"kwiaciarnia",
    "antiques":"antyki",
    "animal_breeding":"hodowla zwierząt",
    "garden_centre":"centrum ogrodnicze",
    "jewelry":"biżuteria",
    "travel_agency":"biuro podróży",
    "gift":"upominki",
    "mobile_phone":"telefony komórkowe",
    "flooring":"podłogi",
    "e-cigarette":"e-papierosy",
    "doityourself":"majsterkowanie",
    "greengrocer":"warzywniak"
}

def translate_properties(properties):
    translated_properties = {}
    for key, value in properties.items():
        # Tłumaczenie klucza
        translated_key = translation_dict_keys.get(key, key)
        # Tłumaczenie wartości
        translated_value = translation_dict_values.get(value, value)
        
        # Formatowanie tłumaczeń w zależności od tego, co zostało przetłumaczone
        if translated_key != key and translated_value != value:
            translated_properties[key] = f"{value} ({translated_key}: {translated_value})"
        elif translated_key != key:
            translated_properties[key] = f"{value} ({translated_key})"
        elif translated_value != value:
            translated_properties[key] = f"{value} ({translated_value})"
        else:
            translated_properties[key] = value
            
    return translated_properties

def process_geojson(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    for feature in geojson_data['features']:
        feature['properties'] = translate_properties(feature['properties'])
    
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
