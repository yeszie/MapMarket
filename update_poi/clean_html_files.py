#usuwa ze wszystkich html entery i spacje zeby zmniejszyc rozmiar pliku
# rekurencyjnie ze wszystkiego oprócz blokow ze skryptami 

import os
import re

def minimize_html_in_folder(folder_path):
    # Przechodzenie przez wszystkie pliki w folderze i podfolderach
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.html'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Znajdowanie wszystkich bloków <script>...</script>
                script_blocks = re.findall(r'(<script.*?>.*?</script>)', content, re.DOTALL)

                # Usuwanie skryptów tymczasowo z zawartości
                for i, script_block in enumerate(script_blocks):
                    content = content.replace(script_block, f"__SCRIPT_BLOCK_{i}__")

                # Usuwanie nadmiarowych spacji i nowych linii
                minimized_content = re.sub(r'\s+', ' ', content)

                # Przywracanie skryptów
                for i, script_block in enumerate(script_blocks):
                    minimized_content = minimized_content.replace(f"__SCRIPT_BLOCK_{i}__", script_block)

                # Usuwanie nadmiarowych spacji pomiędzy tagami HTML
                minimized_content = minimized_content.replace('> <', '><')

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(minimized_content)

                print(f"Plik {file_name} został zminimalizowany.")

# Przykład użycia:
folder_path = 'static'  # Zmień na odpowiednią ścieżkę
minimize_html_in_folder(folder_path)
