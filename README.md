# MapMarket

Prosty portal wyświetlający punkty użyteczności publicznej pobranej z OSM. Dodatkowo dla współrzędnych GPS pobierane są adresy z Google Maps API. Skrypty generują zawartość strony. Znaczniki GPS zdjęć odczytywane są i dopasowywane do adresów. Używany PostreSql oraz python. Po wypełnieniu akrusza kalkulacyjnego otrzymyjemy np. warstwę ogłoszeń nieruchomości. Po wprowadzeniu zmian należy uruchomić odpowiedni skrypt generujący zawartość strony. Przykładowo jeśli chcemy utworzyć kilkadziesiąt tysięcy plików html (np. dla wszystkich sklepów w Polsce) - sam proces generowania plików na Windows z dyskami SSD będzie długi. Celem przyspieszenia operacji warto korzystać z RAM dysków.

Możliwe jest dodanie kolejnych warstw, niemniej jednak to co jest zrobione służy tylko jako przykład. Jako silnika WWW używamy Flask/WSGI. Connectorem może być np. usługa Tunnels od Cloudflare.
