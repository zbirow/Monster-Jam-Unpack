import os
import zlib

# --- Konfiguracja ---
# Nazwy plików i katalogów (bez ścieżek)
INPUT_FILE_NAME = 'Packfile.dat'
OUTPUT_DIR_NAME = 'unpacked_files'

# --- Stałe binarne ---
# Znacznik !CMP -> 21 43 4D 50
CMP_MARKER = b'\x21\x43\x4D\x50'
# Standardowy nagłówek kompresji zlib (DEFLATE)
ZLIB_MARKER = b'\x78\x9c'


def unpack_files():
    """
    Główna funkcja do rozpakowywania plików z archiwum .dat.
    Wszystkie operacje plikowe odbywają się w katalogu, w którym znajduje się skrypt.
    """
    try:
        # Krok 1: Ustalenie, gdzie znajduje się ten skrypt
        # __file__ to specjalna zmienna Pythona przechowująca ścieżkę do bieżącego pliku .py
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # Jeśli skrypt jest uruchamiany w środowisku, gdzie __file__ nie jest zdefiniowane
        # (np. interaktywna konsola), używamy bieżącego katalogu roboczego.
        script_dir = os.getcwd()

    # Krok 2: Zbudowanie pełnych ścieżek na podstawie lokalizacji skryptu
    # os.path.join() inteligentnie łączy ścieżki, działając na każdym systemie (Windows/Linux/macOS)
    input_file_path = os.path.join(script_dir, INPUT_FILE_NAME)
    output_dir_path = os.path.join(script_dir, OUTPUT_DIR_NAME)

    # Sprawdzenie, czy plik wejściowy istnieje w tej lokalizacji
    if not os.path.exists(input_file_path):
        print(f"Błąd: Plik '{input_file_path}' nie został znaleziony!")
        print("Upewnij się, że plik 'Packfile.dat' jest w tym samym katalogu co skrypt.")
        return

    # Utworzenie katalogu na wypakowane pliki w tej lokalizacji
    os.makedirs(output_dir_path, exist_ok=True)
    print(f"Skrypt działa w katalogu: '{script_dir}'")
    print(f"Pliki będą zapisywane w: '{output_dir_path}'")

    # Otwarcie pliku .dat w trybie odczytu binarnego ('rb')
    with open(input_file_path, 'rb') as f:
        data = f.read()

    # Inicjalizacja zmiennych do pętli
    start_pos = 0
    file_index = 0
    
    # Pętla do znajdowania wszystkich wystąpień znacznika !CMP
    while True:
        current_cmp_pos = data.find(CMP_MARKER, start_pos)
        if current_cmp_pos == -1:
            break

        next_cmp_pos = data.find(CMP_MARKER, current_cmp_pos + len(CMP_MARKER))

        if next_cmp_pos == -1:
            file_block = data[current_cmp_pos:]
        else:
            file_block = data[current_cmp_pos:next_cmp_pos]
        
        zlib_start_in_block = file_block.find(ZLIB_MARKER)

        if zlib_start_in_block != -1:
            metadata = file_block[len(CMP_MARKER):zlib_start_in_block]
            compressed_data = file_block[zlib_start_in_block:]
            
            print(f"\n--- Przetwarzanie pliku #{file_index} ---")
            print(f"Znaleziono blok na pozycji: {hex(current_cmp_pos)}")
            print(f"Metadane (hex): {metadata.hex(' ')}")
            
            try:
                decompressed_data = zlib.decompress(compressed_data)
                
                # Budowanie pełnej ścieżki do pliku wyjściowego
                output_filename = os.path.join(output_dir_path, f'unpacked_{file_index}.dat')
                with open(output_filename, 'wb') as out_f:
                    out_f.write(decompressed_data)
                
                print(f"Sukces! Zapisano do: '{output_filename}'")
                print(f"Rozmiar skompresowany: {len(compressed_data)} B, Rozmiar po dekompresji: {len(decompressed_data)} B")

            except zlib.error as e:
                print(f"Błąd dekompresji zlib dla pliku #{file_index}: {e}")

        else:
            print(f"\nOstrzeżenie: W bloku na pozycji {hex(current_cmp_pos)} nie znaleziono nagłówka zlib (78 9C).")

        start_pos = next_cmp_pos
        file_index += 1
        
    print(f"\nZakończono przetwarzanie. Znaleziono i przetworzono {file_index} bloków.")


# Uruchomienie głównej funkcji
if __name__ == "__main__":
    unpack_files()