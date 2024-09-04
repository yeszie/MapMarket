from flask import Flask, request, send_from_directory, jsonify, render_template, redirect, url_for,  after_this_request
#from flask_cors import CORS
import os
import yaml
from PIL import Image
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
#CORS(app) # To enable Cross-Origin Resource Sharing

# Konfiguracja logowania
if not app.debug:
    # Logowanie do pliku
    file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)

    # Logowanie błędów do pliku
    error_handler = RotatingFileHandler('app_error.log', maxBytes=10000, backupCount=1)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    app.logger.addHandler(error_handler)

# Logowanie do konsoli
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
app.logger.addHandler(console_handler)

# Funkcja do generowania miniaturki
def generate_thumbnail(filename):
    filepath = os.path.join(app.root_path, 'static', 'foto', filename)
    thumbpath = os.path.join(app.root_path, 'static', 'thumbnails', filename)

    # Wczytaj obraz
    img = Image.open(filepath)
    
    # Utwórz miniaturkę (zmniejsz do rozmiaru 450x450 px)
    img.thumbnail((450, 450))
    
    # Zapisz miniaturkę
    img.save(thumbpath, 'JPEG')

# Wczytanie danych z pliku YAML
def load_points_from_yaml():
    yaml_file = os.path.join(app.root_path, 'static', 'foto.yaml')
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    return data['points']

# Trasa główna
@app.route('/')
def index():
    app.logger.info('Index page accessed')
    return app.send_static_file('index.html')
    
#@app.route('/map')
#def map_view():
#    app.logger.info('Map page accessed')
#    return send_from_directory('static', 'map.html')

@app.route('/galeria')
def map_view():
    app.logger.info('Galeria')
    return send_from_directory('static', 'galeria_zdjec.html')
    
@app.route('/galeria_zdjec_wedlug_kodow_pocztowych')
def gallery2():
    app.logger.info('Galeria_zdjec_wedlug_kodow_pocztowych')
    return send_from_directory('static', 'galeria_zdjec_wedlug_kodow_pocztowych.html')
    
@app.route('/galeria_zdjec_wedlug_ulic')
def gallery3():
    app.logger.info('galeria_zdjec_wedlug_ulic')
    return send_from_directory('static', 'galeria_zdjec_wedlug_ulic.html')
    
@app.route('/monitoring_ksiag_wieczystych')
def monitoringkw():
    app.logger.info('monitoring_ksiag_wieczystych')
    return send_from_directory('static', 'monitoring_ksiag_wieczystych.html')

@app.route('/wyszukiwarka_ksiag_wieczystych')
def monitoringkw_empty():
    app.logger.info('wyszukiwarka_ksiag_wieczystych')
    return send_from_directory('static', 'monitoring_ksiag_wieczystych.html')   

@app.route('/PolitykaOchronyPrywatnosci')
def politykaochronyprywatnosci():
    return send_from_directory('static', 'PolitykaOchronyPrywatnosci.html')      
    
@app.route('/e404')
def e404():
    return send_from_directory('static', '404.html') 

# Obsługa błędu 404 i przekierowanie na stronę główną
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('e404'))

    
@app.route('/amenity_restaurant.geojson')
def amenity_restaurant():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'amenity_restaurant.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'amenity_restaurant.geojson') 

@app.route('/amenity_restaurant')
def amenity_restaurant_index():
    return send_from_directory('static/amenity_restaurant','index.html')
### 

        
    
@app.route('/defibrillator.geojson')
def defibrillator():
    return send_from_directory('static', 'defibrillator.geojson')
    
###
@app.route('/railway_station.geojson')
def railway_station():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'railway_station.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'railway_station.geojson')       
    
@app.route('/railway_station')
def railway_station_index():
    return send_from_directory('static/railway_station','index.html')
### 
 
@app.route('/amenity_hospital.geojson')
def amenity_hospital():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'amenity_hospital.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'amenity_hospital.geojson')

    
@app.route('/healthcare.geojson')
def healthcare():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'healthcare.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'healthcare.geojson')    
    
@app.route('/healthcare')
def healthcare_index():
    return send_from_directory('static/healthcare','index.html')
        
    

@app.route('/sklepy.geojson')
def sklepy():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'sklepy.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'sklepy.geojson') 
        
@app.route('/shop')
def shop_index():
    return send_from_directory('static/shop','index.html')   
   
@app.route('/office')
def office_index():
    return send_from_directory('static/office','index.html')

@app.route('/office.geojson')
def office():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'office.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'office.geojson')
    
@app.route('/craft.geojson')
def craft():
    return send_from_directory('static', 'craft.geojson')
     

@app.route('/tourism.geojson')
def tourism():
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        @after_this_request
        def add_header(response):
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return send_from_directory('static', 'tourism.geojson.gz', mimetype='application/json')
    else:
        return send_from_directory('static', 'tourism.geojson')


# Trasa do wyświetlania plików JPEG z folderu foto
@app.route('/foto/<path:filename>')
def get_photo(filename):
    app.logger.info(f'Fetching photo: {filename}')
    return send_from_directory(os.path.join(app.root_path, 'static', 'foto'), filename)

# Trasa do pobierania punktów z pliku YAML
@app.route('/points')
def get_points():
    points = load_points_from_yaml()
    app.logger.info('Points data fetched')
    return jsonify(points=points)

# Trasa do generowania i pobierania miniaturki
@app.route('/thumbnails/<path:filename>')
def get_thumbnail(filename):
    app.logger.info(f'Generating thumbnail: {filename}')
    generate_thumbnail(filename)
    return send_from_directory(os.path.join(app.root_path, 'static', 'thumbnails'), filename)

@app.route('/oferty_dzialek')
def oferty_dzialek():
    app.logger.info('Oferty działek page accessed')
    try:
        return send_from_directory('static', 'oferty_dzialek.html')
    except Exception as e:
        app.logger.error(f'Error serving file: {e}')
        return "Error", 500

# Trasa do pobierania pliku sitemap.xml
@app.route('/sitemap.xml')
def sitemap():
    app.logger.info('Sitemap page accessed')
    try:
        return send_from_directory('static', 'sitemap.xml')
    except Exception as e:
        app.logger.error(f'Error serving sitemap file: {e}')
        return "Error", 500

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')


# Uruchomienie aplikacji
from waitress import serve

if __name__ == '__main__':
    serve(app, host='0.0.0.0', 
    port=12345,
    threads=16, # liczba wątków
    backlog=2048,       # zwiększa rozmiar kolejki zadań
    #connections=1000,  # zwiększa maksymalną liczbę połączeń
    expose_tracebacks = False    #  tracebacki błędów w odpowiedzi HTTP
    )
