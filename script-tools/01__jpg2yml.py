#Odczytuje GPS ze wszystkich zdjęć i tworzy plik YML


import os
import yaml
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

def get_exif_data(image):
    """Extract EXIF data from an image and return it as a dictionary."""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def get_if_exist(data, key):
    """Return the value of a key if it exists in the dictionary."""
    return data.get(key)

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees in float format."""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def convert_ifd_rational_to_degrees(value):
    """Convert IFD Rational to degrees."""
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Extract latitude and longitude from EXIF data."""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = get_if_exist(gps_info, "GPSLatitudeRef")
        gps_longitude = get_if_exist(gps_info, "GPSLongitude")
        gps_longitude_ref = get_if_exist(gps_info, "GPSLongitudeRef")

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            if isinstance(gps_latitude[0], tuple):
                lat = convert_ifd_rational_to_degrees(gps_latitude)
            else:
                lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = -lat

            if isinstance(gps_longitude[0], tuple):
                lon = convert_ifd_rational_to_degrees(gps_longitude)
            else:
                lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = -lon

    return lat, lon

def get_file_date(file_path):
    """Return the modification date of the file in MM_RRRR format."""
    timestamp = os.path.getmtime(file_path)
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%m_%Y")

def main(output_file):
    yaml_data = {'points': []}

    directory = r'C:\test123\tools\FotoOriginal'  # Specify your image directory here

    for filename in os.listdir(directory):
        if filename.lower().endswith('.jpg'):
            try:
                file_path = os.path.join(directory, filename)
                with Image.open(file_path) as img:
                    exif_data = get_exif_data(img)
                    lat, lon = get_lat_lon(exif_data)
                    file_date = get_file_date(file_path)
                    
                    # Add photoUrl field with filename
                    file_info = {
                        'file': filename,
                        'latitude': lat,
                        'longitude': lon,
                        'photoUrl': filename,  # Assuming 'photoUrl' should be the same as 'file'
                        'date': file_date,
                        'geoportal': ''
                    }
                    yaml_data['points'].append(file_info)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    with open(output_file, 'w') as file:
        yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    output_file_path = r'C:\test123\static\foto.yaml'
    main(output_file=output_file_path)
