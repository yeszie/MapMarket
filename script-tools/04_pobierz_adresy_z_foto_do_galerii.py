#Uzupełnienie adresów do galerii


import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests
import yaml

api_key = "XXXXXXXXXXXXXXXXXXXXXX"       #google api klucz
folder_path = r"C:\test123\tools\FotoOriginal"
output_file = "adresy_galeria.yml"

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]
                    exif_data[tag_name] = gps_data
                else:
                    exif_data[tag_name] = value
        return exif_data
    except Exception as e:
        print(f"Error getting EXIF data from {image_path}: {e}")
        return {}

def get_decimal_coordinates(gps_data):
    try:
        def convert_to_degrees(value):
            d = value[0] + value[1]/60.0 + value[2]/3600.0
            return d

        lat = convert_to_degrees(gps_data["GPSLatitude"])
        if gps_data["GPSLatitudeRef"] != "N":
            lat = -lat

        lon = convert_to_degrees(gps_data["GPSLongitude"])
        if gps_data["GPSLongitudeRef"] != "E":
            lon = -lon

        return lat, lon
    except KeyError as e:
        print(f"Error converting GPS data: {e}")
        return None, None

def get_address(api_key, lat, lon):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'OK':
            return data['results'][0]['formatted_address']
        else:
            print(f"Error in geocoding: {data['status']}")
            return None
    except Exception as e:
        print(f"Error getting address: {e}")
        return None

def process_images(folder_path, api_key, output_file):
    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('jpg', 'jpeg', 'png')):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing {image_path}...")
            exif_data = get_exif_data(image_path)
            if "GPSInfo" in exif_data:
                gps_data = exif_data["GPSInfo"]
                lat, lon = get_decimal_coordinates(gps_data)
                if lat is not None and lon is not None:
                    address = get_address(api_key, lat, lon)
                    if address:
                        results.append({
                            'filename': filename,
                            'latitude': lat,
                            'longitude': lon,
                            'address': address
                        })
                    else:
                        print(f"No address found for coordinates: {lat}, {lon}")
                else:
                    print(f"Could not convert GPS data to coordinates for {image_path}")
            else:
                print(f"No GPS data found in {image_path}")

    with open(output_file, 'w', encoding='utf-8') as file:
        yaml.dump(results, file, allow_unicode=True, default_flow_style=False)
    print(f"Results written to {output_file}")

# Run the function
process_images(folder_path, api_key, output_file)
