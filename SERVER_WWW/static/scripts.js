// Inicjalizacja mapy
var map = L.map('map').setView([52.0, 19.0], 7); 

// Dodanie funkcji hash do mapy
var hash = new L.Hash(map);

// Dodanie warstwy kafelkowej OpenStreetMap jako domyślna
var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// Dodanie warstwy kafelkowej Mapy Satelitarnej
var satLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

/////////////////////////////////////////////////

// Niestandardowa kontrola z przyciskiem lokalizacji
var locateControl = L.Control.extend({
    options: {
        position: 'topright' // Pozycja kontrolki na mapie
    },

    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');

        container.style.backgroundColor = 'yellow'; 
        container.style.backgroundImage = "url('https://cdn-icons-png.flaticon.com/512/16/16001.png')"; // Ikona lokalizacji
        container.style.backgroundSize = "30px 30px";
        container.style.width = '30px';
        container.style.height = '30px';

        container.onclick = function(){
            locateUser(); // Wywołanie funkcji lokalizacji użytkownika po kliknięciu przycisku
        }

        return container;
    }
});

// Dodanie kontrolki do mapy
map.addControl(new locateControl());

// Funkcja do ustawienia mapy na lokalizację użytkownika
function locateUser() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLatLng = [position.coords.latitude, position.coords.longitude];
            map.setView(userLatLng, 15); // Ustawienie widoku mapy na lokalizację użytkownika

            // Dodanie markera do lokalizacji użytkownika
            L.marker(userLatLng).addTo(map)
                .bindPopup("Jesteś tutaj!")
                .openPopup();
        }, function(error) {
            console.error("Błąd przy uzyskiwaniu lokalizacji użytkownika: ", error);
            alert("Nie udało się uzyskać Twojej lokalizacji.");
        });
    } else {
        alert("Twoja przeglądarka nie wspiera geolokalizacji.");
    }
}

//////////////////////////////////////////////////

// Tworzenie grupy warstw dla przełącznika
var baseLayers = {
    "Mapa": osmLayer,
    "Satelitarna": satLayer
};

// Dodanie grupy warstw do mapy
L.control.layers(baseLayers).addTo(map);

// Ustawienie warstwy OpenStreetMap jako domyślnej
osmLayer.addTo(map);

// Warstwa z ogłoszeniami nieruchomości
var geojsonMarkers = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({ 
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-geojson',
            iconSize: L.point(40, 40)
        });
    }
});

// Wczytanie danych GeoJSON z pliku (output.geojson)
fetch('static/output.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: function(feature, layer) {
                var popupContent = '<b>ID ogłoszenia: ' + feature.properties.ID_lokalizacji + '</b><br>';
                popupContent += '<b>Adres: ' + feature.properties.Adres + '</b><br>';
                popupContent += 'Rodzaj: ' + feature.properties.rodzaj + '<br>';
                popupContent += 'Powierzchnia: ' + feature.properties.powierzchnia + ' m²';
                popupContent += ' Cena: ' + feature.properties.cena + ' PLN';
                popupContent += ' (' + feature.properties.cena_m2 + ' PLN/m²)<br>';
                if (feature.properties.uwagi && feature.properties.uwagi !== "nan") {
                    popupContent += 'Uwagi: ' + feature.properties.uwagi + '<br>';
                }
                if (feature.properties.geoportal) {
                    popupContent += '<a href="' + feature.properties.geoportal + '" target="_blank">geoportal</a>';
                }
                if (feature.properties.googlemaps) {
                    popupContent += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<a href="' + feature.properties.googlemaps + '" target="_blank">google</a>';
                }
                if (feature.properties.website) {
                    popupContent += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<a href="' + feature.properties.website + '" target="_blank">ogłoszenie</a><br>';
                }
                if (feature.properties.photo_url) {
                    popupContent += '<img src="' + feature.properties.photo_url + '">';
                }

                // Dodanie tooltipu
                layer.bindTooltip(popupContent, { sticky: true }).openTooltip();

                // Dodanie popupu
                layer.bindPopup(popupContent, { maxWidth: 'auto' });

                // Dodanie do warstwy markerów z grupą znaczników
                geojsonMarkers.addLayer(layer);
            }
        });

        // Dodanie warstwy markerów z GeoJSON do mapy
        map.addLayer(geojsonMarkers);
    })
    .catch(error => console.error('Error loading GeoJSON data:', error));

// Funkcja tworząca niestandardową zieloną ikonę znacznika
//function createFirmIcon() {
//    return L.icon({
//        iconUrl: 'https://www.pikpng.com/pngl/b/66-660381_business-icon-company-name-icon-clipart.png', // Ścieżka do ikony znacznika
//        iconSize: [25, 41], // Rozmiar ikony znacznika (standardowy rozmiar Leaflet)
//        iconAnchor: [12, 41], // Punkt przypięcia ikony (środek dołu)
//        popupAnchor: [1, -34] // Punkt, w którym popup będzie przypięty do znacznika
//    });
//}

// Warstwa z ogłoszeniami firm z klastrowaniem
//var firmsLayer = L.markerClusterGroup({
//    iconCreateFunction: function(cluster) {
//        var childCount = cluster.getChildCount();
//        return L.divIcon({
//            html: '<div><span>' + childCount + '</span></div>',
//            className: 'marker-cluster marker-cluster-firms',
//            iconSize: L.point(40, 40)
//        });
//    }
//});

/////////////////////////////////////////////////////////
//Restauracje

var amenity_restaurant = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-amenity_restaurant',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon1 = L.divIcon({
    className: 'custom-icon1'
});

fetch('/amenity_restaurant.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon1 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    //let tooltipContent = '<strong>' + (feature.properties.name || '') + '</strong>';
                    let tooltipContent = '';
                    
                    // Iteracja przez wszystkie właściwości obiektu properties
                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  // Zmieniamy z tooltip na popup, aby było możliwe kliknięcie
                }
            }
        }).eachLayer(function(layer) {
            amenity_restaurant.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });

        // Add the MarkerClusterGroup to the map
        // map.addLayer(amenity_restaurant);
    })
    .catch(error => console.error('Błąd ładowania restauracji:', error));




// Dodanie funkcji obsługi checkboxa dla restauracje
var restauracjeCheckbox = document.getElementById('restauracjeCheckbox');
restauracjeCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(amenity_restaurant);   
    } else {
        map.removeLayer(amenity_restaurant);   
    }
});

//End Restauracje
/////////////////////////////////////////////////////////
//defibrillator

var defibrillator = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-defibrillator',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon2 = L.divIcon({
    className: 'custom-icon2'
});

fetch('/defibrillator.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon2 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = '<strong>' + 'Dostępność: ' + (feature.properties.access || 'Brak informacji') + '</strong>';

                    // Iteracja przez wszystkie właściwości obiektu properties
                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            // Dodaj właściwości do popupu, jeśli mają wartość
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  // Zmieniamy z tooltip na popup, aby było możliwe kliknięcie
                }
            }
        }).eachLayer(function(layer) {
            defibrillator.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });

        // Add the MarkerClusterGroup to the map
        // map.addLayer(defibrillator);
    })
    .catch(error => console.error('Błąd ładowania defibrillator:', error));


// Funkcja pomocnicza do kapitalizacji pierwszej litery
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


// Dodanie funkcji obsługi checkboxa dla defibrillator
var restauracjeCheckbox = document.getElementById('defibrillatorCheckbox');
defibrillatorCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(defibrillator);   
    } else {
        map.removeLayer(defibrillator);   
    }
});

//End defibrillator
//////////////////////////////////////////

//railway_station

var railway_station = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-railway_station',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon3 = L.divIcon({
    className: 'custom-icon3'
});

fetch('/railway_station.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon3 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Stacja kolejowa';

                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  
                }
            }
        }).eachLayer(function(layer) {
            railway_station.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania railway_station:', error));


// Funkcja pomocnicza do kapitalizacji pierwszej litery
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Dodanie funkcji obsługi checkboxa dla railway_station
var restauracjeCheckbox = document.getElementById('railway_stationCheckbox');
railway_stationCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(railway_station);   
    } else {
        map.removeLayer(railway_station);   
    }
});

//End railway_station
///////////////////////////////////////





//amenity_hospital

var amenity_hospital = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-amenity_hospital',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon4 = L.divIcon({
    className: 'custom-icon4'
});

fetch('/amenity_hospital.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon4 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Szpital';

                    // Dodajemy właściwości do treści tooltipa
                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Przyjmujemy pierwszą dostępną parę współrzędnych
                    let lat, lon;

                    try {
                        if (feature.geometry.type === "Point" && Array.isArray(feature.geometry.coordinates) && feature.geometry.coordinates.length === 2) {
                            lat = feature.geometry.coordinates[1];
                            lon = feature.geometry.coordinates[0];
                        } else if (feature.geometry.type === "GeometryCollection") {
                            const firstGeometry = feature.geometry.geometries.find(g => g.type === "Point");
                            if (firstGeometry && Array.isArray(firstGeometry.coordinates) && firstGeometry.coordinates.length === 2) {
                                lat = firstGeometry.coordinates[1];
                                lon = firstGeometry.coordinates[0];
                            }
                        } else if (feature.geometry.type === "Polygon") {
                            const firstCoords = feature.geometry.coordinates[0];
                            if (Array.isArray(firstCoords) && firstCoords.length > 0) {
                                lat = firstCoords[0][1];
                                lon = firstCoords[0][0];
                            }
                        }

                        if (lat !== undefined && lon !== undefined) {
                            // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                            const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                            tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                            // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                            const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                            const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                            tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;
                        } else {
                            console.warn('Nie znaleziono współrzędnych dla tego obiektu:', feature);
                            tooltipContent += `<br><em>Brak współrzędnych</em>`;
                        }
                    } catch (error) {
                        console.error('Błąd przy przetwarzaniu współrzędnych:', error);
                        tooltipContent += `<br><em>Błąd przy przetwarzaniu współrzędnych</em>`;
                    }

                    layer.bindPopup(tooltipContent);
                }
            }
        }).eachLayer(function(layer) {
            amenity_hospital.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania amenity_hospital:', error));

// Funkcja pomocnicza do kapitalizacji pierwszej litery
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}



// Dodanie funkcji obsługi checkboxa dla amenity_hospital
var amenity_hospitalCheckbox = document.getElementById('amenity_hospitalCheckbox');
amenity_hospitalCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(amenity_hospital);   
    } else {
        map.removeLayer(amenity_hospital);   
    }
});

//End amenity_hospital
/////////////


//healthcare

var healthcare = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-amenity_hospital',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon4 = L.divIcon({
    className: 'custom-icon4'
});

fetch('/healthcare.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon4 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Opieka zdrowotna';

                    // Dodajemy właściwości do treści tooltipa
                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Przyjmujemy pierwszą dostępną parę współrzędnych
                    let lat, lon;

                    try {
                        if (feature.geometry.type === "Point" && Array.isArray(feature.geometry.coordinates) && feature.geometry.coordinates.length === 2) {
                            lat = feature.geometry.coordinates[1];
                            lon = feature.geometry.coordinates[0];
                        } else if (feature.geometry.type === "GeometryCollection") {
                            const firstGeometry = feature.geometry.geometries.find(g => g.type === "Point");
                            if (firstGeometry && Array.isArray(firstGeometry.coordinates) && firstGeometry.coordinates.length === 2) {
                                lat = firstGeometry.coordinates[1];
                                lon = firstGeometry.coordinates[0];
                            }
                        } else if (feature.geometry.type === "Polygon") {
                            const firstCoords = feature.geometry.coordinates[0];
                            if (Array.isArray(firstCoords) && firstCoords.length > 0) {
                                lat = firstCoords[0][1];
                                lon = firstCoords[0][0];
                            }
                        }

                        if (lat !== undefined && lon !== undefined) {
                            // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                            const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                            tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                            // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                            const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                            const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                            tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;
                        } else {
                            console.warn('Nie znaleziono współrzędnych dla tego obiektu:', feature);
                            tooltipContent += `<br><em>Brak współrzędnych</em>`;
                        }
                    } catch (error) {
                        console.error('Błąd przy przetwarzaniu współrzędnych:', error);
                        tooltipContent += `<br><em>Błąd przy przetwarzaniu współrzędnych</em>`;
                    }

                    layer.bindPopup(tooltipContent);
                }
            }
        }).eachLayer(function(layer) {
            healthcare.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania healthcare:', error));

// Funkcja pomocnicza do kapitalizacji pierwszej litery
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


// Dodanie funkcji obsługi checkboxa dla healthcare
var healthcareCheckbox = document.getElementById('healthcareCheckbox');
healthcareCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(healthcare);   
    } else {
        map.removeLayer(healthcare);   
    }
});

//End healthcare
////////////////////////

//shop

var shop = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-shop',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon5 = L.divIcon({
    className: 'custom-icon5'
});

fetch('/sklepy.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon5 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Sklep';

                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  
                }
            }
        }).eachLayer(function(layer) {
            shop.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania shop:', error));



// Funkcja pomocnicza do kapitalizacji pierwszej litery
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

 

// Dodanie funkcji obsługi checkboxa dla amenity_hospital
var shopCheckbox = document.getElementById('shopCheckbox');
shopCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(shop);   
    } else {
        map.removeLayer(shop);   
    }
});

//End shop
/////////////////////////


//office

var office = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-office',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon6 = L.divIcon({
    className: 'custom-icon6'
});

fetch('/office.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon6 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Biura';

                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  
                }
            }
        }).eachLayer(function(layer) {
            office.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania office:', error));

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Dodanie funkcji obsługi checkboxa dla amenity_hospital
var officeCheckbox = document.getElementById('officeCheckbox');
officeCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(office);   
    } else {
        map.removeLayer(office);   
    }
});

//End office
/////////////////////////


//craft

var craft = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-craft',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon7 = L.divIcon({
    className: 'custom-icon7'
});

fetch('/craft.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon7 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Craft';

                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  
                }
            }
        }).eachLayer(function(layer) {
            craft.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania craft:', error));

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Dodanie funkcji obsługi checkboxa dla craft
var craftCheckbox = document.getElementById('craftCheckbox');
craftCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(craft);   
    } else {
        map.removeLayer(craft);   
    }
});

//End craft
/////////////////////////

//construction tourism

var tourism = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-tourism',
            iconSize: L.point(40, 40)
        });
    }
});

// Define custom icon
var customIcon9 = L.divIcon({
    className: 'custom-icon9'
});

fetch('/tourism.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.marker(latlng, { icon: customIcon9 });
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    let tooltipContent = 'Turystyka';

                    for (let key in feature.properties) {
                        if (feature.properties.hasOwnProperty(key) && key !== 'access') {
                            let value = feature.properties[key];
                            if (value) {
                                tooltipContent += `<br>${capitalizeFirstLetter(key.replace(/([A-Z])/g, ' $1'))}: ${value}`;
                            }
                        }
                    }

                    // Dodajemy odnośnik do Google Maps na podstawie współrzędnych
                    const lat = feature.geometry.coordinates[1];
                    const lon = feature.geometry.coordinates[0];
                    const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;
                    tooltipContent += `<br><a href="${googleMapsUrl}" target="_blank">Google Maps</a>`;

                    // Dodajemy miniaturę Street View z odnośnikiem do pełnego widoku
                    const streetViewUrl = `https://maps.googleapis.com/maps/api/streetview?size=200x100&location=${lat},${lon}&key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`;
                    const streetViewLink = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
                    tooltipContent += `<br><a href="${streetViewLink}" target="_blank"><img src="${streetViewUrl}" alt="Street View" style="margin-top: 10px; max-width: 100%; height: auto;"></a>`;

                    layer.bindPopup(tooltipContent);  
                }
            }
        }).eachLayer(function(layer) {
            tourism.addLayer(layer); // Dodajemy każdą warstwę do grupy cluster
        });
    })
    .catch(error => console.error('Błąd ładowania construction residential:', error));

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Dodanie funkcji obsługi checkboxa dla construction
var tourismCheckbox = document.getElementById('tourismCheckbox');
tourismCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(tourism);   
    } else {
        map.removeLayer(tourism);   
    }
});

//End Tourism
/////////////////////////




// Wczytanie danych GeoJSON z ogłoszeniami firm
//fetch('static/firms.geojson')
//    .then(response => response.json())
//    .then(data => {
//        L.geoJSON(data, {
//            pointToLayer: function(feature, latlng) {
//                return L.marker(latlng, { icon: createFirmIcon() });
//            },
//            onEachFeature: function(feature, layer) {
//                var popupContent = '<b>Nazwa firmy: ' + feature.properties.name + '</b><br>';
//                popupContent += 'Adres: ' + feature.properties.address + '<br>';
//                if (feature.properties.website) {
//                    popupContent += '<a href="' + feature.properties.website + '" target="_blank">Strona internetowa</a><br>';
//                }
//                layer.bindPopup(popupContent);
//                firmsLayer.addLayer(layer);
//            }
//        });
//    })
//    .catch(error => console.error('Error loading firms data:', error));

// Funkcja tworząca niestandardową ikonę znacznika (miniaturka zdjęcia)
function createCustomIcon(photoUrl) {
    return L.icon({
        iconUrl: 'thumbnails/' + photoUrl,  // URL miniaturki zdjęcia
        iconSize: [48, 48],  // Rozmiar miniaturki zdjęcia (można dostosować)
        iconAnchor: [24, 48],  // Punkt przypięcia ikony (środek dołu)
        popupAnchor: [0, -48]  // Punkt, w którym popup będzie przypięty do znacznika
    });
}

// Utworzenie warstwy z punktami ze zdjęciami
var photosLayer = L.markerClusterGroup({
    iconCreateFunction: function(cluster) {
        var childCount = cluster.getChildCount();
        return L.divIcon({ 
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster marker-cluster-photos',
            iconSize: L.point(40, 40)
        });
    }
});

// Funkcja do usuwania rozszerzenia z nazwy pliku
function getFileNameWithoutExtension(fileName) {
    return fileName.split('.').slice(0, -1).join('.');
}

// Załadowanie punktów z pliku JSON
fetch('/points')
    .then(response => response.json())
    .then(data => {
        data.points.forEach(point => {
            // Przetworzenie nazwy pliku i dodanie prefiksu '_'
            const fileNameWithoutExtension = '_' + getFileNameWithoutExtension(point.file);
            
            // Przygotowanie treści popupu
            let htmlContent = `
                <a href="/foto/${encodeURIComponent(point.file)}" target="_blank">
                    <img src="thumbnails/${encodeURIComponent(point.photoUrl)}" width="500px" height="auto" />
                </a><br>
                ${point.date}
            `;

            // Dodanie linku do Google Maps
            if (point.latitude && point.longitude) {
                htmlContent += `
                    <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(point.latitude)},${encodeURIComponent(point.longitude)}" target="_blank"> [Google Maps] </a>
                `;
            }

            // Dodanie linku do Geoportalu
            if (point.geoportal) {
                htmlContent += `
                    <br><a href="${encodeURIComponent(point.geoportal)}" target="_blank"> [Geoportal]</a>
                `;
            }

            htmlContent += `
                <a href="/galeria#${encodeURIComponent(fileNameWithoutExtension)}"> [Galeria] </a>
            `;

            htmlContent += `
                <a href="/oferty_dzialek" target="_self">[Ogłoszenia sprzedaży działek]</a>
            `;

            // Tworzenie markera i dodanie go do warstwy
            if (point.latitude && point.longitude) {
                const marker = L.marker([point.latitude, point.longitude], {
                    icon: createCustomIcon(point.photoUrl)
                })
                .bindPopup(htmlContent, { maxWidth: 600 });  // Dostosowanie maxWidth popupu

                photosLayer.addLayer(marker);
            }
        });
    })
    .catch(error => console.error('Error loading points:', error));

// Dodanie warstwy z grupą znaczników ze zdjęciami do mapy
map.addLayer(photosLayer);

// Dodanie funkcji obsługi checkboxa dla ogłoszeń firm
//var firmsCheckbox = document.getElementById('firmsCheckbox');
//firmsCheckbox.addEventListener('change', function() {
//    if (this.checked) {
//        map.addLayer(firmsLayer);  // Dodaj warstwę z ogłoszeniami firm do mapy
//    } else {
//        map.removeLayer(firmsLayer);  // Usuń warstwę z ogłoszeniami firm z mapy
//    }
//});

// Dodanie funkcji obsługi checkboxa dla ogłoszeń nieruchomości
var geojsonCheckbox = document.getElementById('geojsonCheckbox');
geojsonCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(geojsonMarkers);  // Dodaj warstwę z ogłoszeniami nieruchomości do mapy
    } else {
        map.removeLayer(geojsonMarkers);  // Usuń warstwę z ogłoszeniami nieruchomości z mapy
    }
});

// Nasłuchiwanie zmiany stanu checkboxa dla warstwy zdjęć
var photosCheckbox = document.getElementById('photosCheckbox');
photosCheckbox.addEventListener('change', function() {
    if (this.checked) {
        map.addLayer(photosLayer);  // Dodaj warstwę ze zdjęciami do mapy
    } else {
        map.removeLayer(photosLayer);  // Usuń warstwę ze zdjęciami z mapy
    }
});




// Nasłuchiwanie zmiany przełącznika warstw mapy
var mapLayerRadio1 = document.getElementById('mapLayerRadio1');
var mapLayerRadio2 = document.getElementById('mapLayerRadio2');
mapLayerRadio1.addEventListener('change', function() {
    if (this.checked) {
        map.removeLayer(satLayer);
        map.addLayer(osmLayer);
    }
});
mapLayerRadio2.addEventListener('change', function() {
    if (this.checked) {
        map.removeLayer(osmLayer);
        map.addLayer(satLayer);
    }
});

// Dopasowanie mapy do zmiany rozmiaru okna przeglądarki
map.invalidateSize();
