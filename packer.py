import os
import zlib
import struct
import shutil

# --- Konfiguracja ---
ORIGINAL_FILE = 'Packfile.dat'
MODIFIED_FILE = 'Packfile_modify_appended.dat'
INPUT_DIR = 'pack'

# --- Adresy i stałe ---
INDEX_START_ADDRESS = 0x14CC0
ENTRY_SIZE = 16
CMP_MARKER = b'\x21\x43\x4D\x50'
PNG_HEADER = b'\x89\x50\x4E\x47'
ZLIB_START_OFFSET_IN_BLOCK = 8

def find_all_markers(data, marker):
    positions = []
    pos = data.find(marker, 0)
    while pos != -1:
        positions.append(pos)
        pos = data.find(marker, pos + 1)
    return positions

def repack_files_with_append():
    print(f"--- Repacker (tryb dopisywania) dla '{ORIGINAL_FILE}' ---")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    
    original_path = os.path.join(script_dir, ORIGINAL_FILE)
    modified_path = os.path.join(script_dir, MODIFIED_FILE)
    input_dir_path = os.path.join(script_dir, INPUT_DIR)

    if not os.path.exists(original_path) or not os.path.isdir(input_dir_path):
        print("BŁĄD: Brak pliku Packfile.dat lub folderu 'pack/'!")
        return

    print(f"Tworzenie kopii roboczej: '{modified_path}'...")
    shutil.copyfile(original_path, modified_path)
    
    with open(modified_path, 'r+b') as f:
        data = bytearray(f.read())

        print("Skanowanie struktury bloków...")
        cmp_positions = find_all_markers(data, CMP_MARKER)
        png_positions = find_all_markers(data, PNG_HEADER)
        
        all_chunks = []
        for pos in cmp_positions: all_chunks.append({'offset': pos, 'type': 'CMP'})
        for pos in png_positions: all_chunks.append({'offset': pos, 'type': 'PNG'})
        all_chunks.sort(key=lambda x: x['offset'])
        
        files_to_repack = {}
        for filename in os.listdir(input_dir_path):
            if filename.startswith('chunk_'):
                try:
                    chunk_number = int(filename.split('_')[1].split('.')[0])
                    files_to_repack[chunk_number] = os.path.join(input_dir_path, filename)
                except (ValueError, IndexError): continue
        
        print(f"Znaleziono {len(files_to_repack)} plików do zaimplementowania.")

        for i, chunk in enumerate(all_chunks):
            if i in files_to_repack:
                file_to_inject_path = files_to_repack[i]
                print(f"\nPróba podmiany bloku #{i} plikiem '{os.path.basename(file_to_inject_path)}'...")
                
                with open(file_to_inject_path, 'rb') as new_file:
                    new_data = new_file.read()

                original_offset = chunk['offset']
                is_last_chunk = (i + 1) == len(all_chunks)
                original_end_offset = len(data) if is_last_chunk else all_chunks[i+1]['offset']
                original_block_size = original_end_offset - original_offset
                
                new_block_data = b''
                
                if chunk['type'] == 'CMP':
                    original_size = len(new_data)
                    compressed_stream = zlib.compress(new_data)
                    new_block_data = CMP_MARKER + struct.pack('<I', original_size) + compressed_stream
                elif chunk['type'] == 'PNG':
                    new_block_data = new_data

                # --- NOWA, BEZPIECZNA LOGIKA ---
                if len(new_block_data) <= original_block_size:
                    # Jeśli nowy blok się mieści, podmieniamy go "na miejscu"
                    print(f"  Nowy blok ({len(new_block_data)} B) mieści się w oryginalnym miejscu ({original_block_size} B). Podmieniam.")
                    data[original_offset : original_offset + len(new_block_data)] = new_block_data
                    # Wypełniamy resztę zerami (dopełnienie)
                    if len(new_block_data) < original_block_size:
                        padding_size = original_block_size - len(new_block_data)
                        data[original_offset + len(new_block_data) : original_end_offset] = b'\x00' * padding_size
                else:
                    # Jeśli nowy blok jest za duży, dopisujemy go na końcu pliku
                    print(f"  Nowy blok ({len(new_block_data)} B) jest większy niż oryginalne miejsce ({original_block_size} B).")
                    
                    # 1. Zapamiętaj, gdzie na końcu pliku umieścimy nowe dane
                    new_offset = len(data)
                    print(f"  Dopisuję na końcu pliku pod adresem {hex(new_offset)}.")
                    
                    # 2. Dopiś nowe dane do 'data'
                    data.extend(new_block_data)
                    
                    # 3. ZNAJDŹ i ZAKTUALIZUJ wpis w Głównej Tabeli Indeksu
                    table_entry_to_update_offset = INDEX_START_ADDRESS + (i * ENTRY_SIZE)
                    
                    # Odczytujemy stary wpis, żeby nie nadpisać wszystkiego
                    old_offset, _, _, old_flags = struct.unpack('<IIII', data[table_entry_to_update_offset:table_entry_to_update_offset+ENTRY_SIZE])
                    
                    new_compr_size = len(new_block_data)
                    
                    # Zapisujemy nowy offset i nowy rozmiar skompresowany
                    # Rozmiar oryginalny jest teraz w metadanych !CMP, więc nie musimy go tu aktualizować
                    # Zachowujemy stare flagi/crc
                    updated_entry = struct.pack('<IIII', new_offset, new_compr_size, 0, old_flags)
                    data[table_entry_to_update_offset : table_entry_to_update_offset + ENTRY_SIZE] = updated_entry
                    print(f"  Zaktualizowano wpis #{i} w Tabeli Indeksu.")
                
                print(f"  Sukces! Blok #{i} został przetworzony.")

        print("\nZapisywanie finalnego pliku...")
        f.seek(0)
        f.write(data)
        f.truncate()

    print(f"\nGotowe! Zmodyfikowany plik został zapisany jako '{MODIFIED_FILE}'.")


if __name__ == "__main__":
    repack_files_with_append()