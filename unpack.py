import os
import zlib

# --- Konfiguracja ---
INPUT_FILE = 'Packfile.dat'
OUTPUT_DIR = 'export'

# --- Znaczniki, których będziemy szukać ---
CMP_MARKER = b'\x21\x43\x4D\x50'
PNG_HEADER = b'\x89\x50\x4E\x47'
ZLIB_START_OFFSET_IN_BLOCK = 8 # zlib stream zaczyna się 8 bajtów po '!CMP'

# ======================= EDYTOWALNA TABELA NAGŁÓWKÓW =======================
# Tutaj mapujesz nagłówek (w formacie binarnym) na rozszerzenie pliku.
# Możesz dodawać własne wpisy. Klucz to bajty, wartość to rozszerzenie.
HEADER_TO_EXTENSION_MAP = {
    b'DDS ': '.dds',           # Standardowy nagłówek DDS (ze spacją na końcu)
    b'\x50\x02\x00': '.hnk',            # Nagłówek dla HNK
    b'Texture': '.files',  
    b'\x06\x00\x00': '.dxm',          # Nagłówek dla DMX
    b'\xED\x09\x00': '.wcol',
    b'TSEC': '.lsb',                  # Nagłówek dla LSB
}
# ===========================================================================

def find_all_markers(data, marker):
    """Pomocnicza funkcja do znajdowania wszystkich wystąpień znacznika."""
    positions = []
    pos = data.find(marker, 0)
    while pos != -1:
        positions.append(pos)
        pos = data.find(marker, pos + 1)
    return positions

def get_extension_from_data(decompressed_data):
    """
    Sprawdza pierwsze bajty rozpakowanych danych i zwraca odpowiednie rozszerzenie
    na podstawie tabeli HEADER_TO_EXTENSION_MAP.
    """
    for header, extension in HEADER_TO_EXTENSION_MAP.items():
        if decompressed_data.startswith(header):
            return extension
            
    # Jeśli żaden nagłówek nie pasuje, sprawdź czy to plik tekstowy
    try:
        sample = decompressed_data[:128].decode('ascii')
        if all(c.isprintable() or c.isspace() for c in sample if c != '\x00'):
            return '.txt'
    except (UnicodeDecodeError, AttributeError):
        pass

    # Domyślne rozszerzenie, jeśli nic nie pasuje
    return '.path'

def bruteforce_export_by_markers_skip_first():
    """
    Skanuje plik, znajduje bloki !CMP i PNG, pomija pierwszy,
    a resztę rozpakowuje i identyfikuje na podstawie tabeli nagłówków.
    """
    print(f"--- Siłowy eksport do folderu '{OUTPUT_DIR}' (z tabelą nagłówków) ---")
    
    # Niezawodne ścieżki
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_dir_path = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_dir_path, exist_ok=True)
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"BŁĄD: Nie można otworzyć pliku wejściowego! {e}")
        return
        
    # Krok 1: Znajdź i posortuj wszystkie bloki
    print("Skanowanie pliku w poszukiwaniu znaczników !CMP i PNG...")
    cmp_positions = find_all_markers(data, CMP_MARKER)
    png_positions = find_all_markers(data, PNG_HEADER)
    
    all_chunks = []
    for pos in cmp_positions:
        all_chunks.append({'offset': pos, 'type': 'CMP'})
    for pos in png_positions:
        all_chunks.append({'offset': pos, 'type': 'PNG'})
    all_chunks.sort(key=lambda x: x['offset'])
    
    if not all_chunks:
        print("Nie znaleziono żadnych bloków danych.")
        return
        
    print(f"Znaleziono łącznie {len(all_chunks)} bloków danych.")
    print(f"Celowo pomijam pierwszy blok znaleziony na pozycji {hex(all_chunks[0]['offset'])}.")

    # Krok 2: Przetwarzanie bloków, pomijając pierwszy
    for i in range(1, len(all_chunks)):
        chunk = all_chunks[i]
        offset = chunk['offset']
        chunk_type = chunk['type']
        
        is_last_chunk = (i + 1) == len(all_chunks)
        end_offset = len(data) if is_last_chunk else all_chunks[i+1]['offset']
        
        raw_chunk = data[offset:end_offset]
        
        output_data = None
        extension = ".dat"
        
        print(f"\nPrzetwarzanie chunk_{i} (Typ: {chunk_type}, Offset: {hex(offset)})...")
        
        if chunk_type == 'CMP':
            zlib_stream = raw_chunk[ZLIB_START_OFFSET_IN_BLOCK:]
            try:
                output_data = zlib.decompress(zlib_stream)
                # Identyfikacja na podstawie tabeli
                extension = get_extension_from_data(output_data)
            except zlib.error as e:
                print(f"  Ostrzeżenie: Błąd dekompresji. Zapisuję surowy blok. Błąd: {e}")
                output_data = raw_chunk
                extension = ".cmp.error"
        
        elif chunk_type == 'PNG':
            output_data = raw_chunk
            extension = ".png"
            
        if output_data:
            output_filename = f"chunk_{i}{extension}"
            output_filepath = os.path.join(output_dir_path, output_filename)
            try:
                with open(output_filepath, 'wb') as out_f:
                    out_f.write(output_data)
                print(f"  Sukces! Zapisano do '{output_filepath}' (Rozmiar: {len(output_data)} bajtów)")
            except OSError as e:
                print(f"  Błąd zapisu pliku '{output_filepath}': {e}")
                
    print(f"\nSukces! Zakończono eksport.")

if __name__ == "__main__":
    bruteforce_export_by_markers_skip_first()
