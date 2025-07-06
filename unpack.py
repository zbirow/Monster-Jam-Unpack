import os
import zlib
import struct


# --- Configuration ---
INPUT_FILE = 'Packfile.dat'
OUTPUT_DIR = 'unpacked_FINAL'

# --- Constants ---
DIRECTORY_TABLE_START = 12
POINTER_TABLE_START = 0x14CC0
POINTER_TABLE_ENTRIES = 10560
POINTER_SIZE = 4

CMP_MARKER = b'\x21\x43\x4D\x50'
PNG_HEADER = b'\x89\x50\x4E\x47'
ZLIB_START_OFFSET_IN_BLOCK = 8

def parse_pointer_table(data):
    """Phase 1: Loads the entire Pointer Table into memory."""
    print("--- Phase 1: Parsing Main Pointer Table ---")
    start = POINTER_TABLE_START
    end = start + (POINTER_TABLE_ENTRIES * POINTER_SIZE)
    pointer_table_data = data[start:end]
    pointers = [struct.unpack('<I', pointer_table_data[i*POINTER_SIZE:(i+1)*POINTER_SIZE])[0] for i in range(POINTER_TABLE_ENTRIES)]
    print(f"Read {len(pointers)} physical data pointers.")
    return pointers

def unpack_files_with_final_logic(data, pointer_table):
    """Main function that unpacks unique files into the correct folder structure."""
    print("\n--- Phase 2: Parsing hierarchy and unpacking unique files ---")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    output_dir_path = os.path.join(script_dir, OUTPUT_DIR)
    
    # Step A: Parse Directory Table
    directories = []
    current_pos = DIRECTORY_TABLE_START
    while True:
        try:
            name_start = current_pos + 8
            name_end = data.find(b'\x00', name_start)
            dir_name = data[name_start:name_end].decode('latin-1')
            if not dir_name or ('/' not in dir_name and '\\' not in dir_name):
                break
            _dir_id, first_file_ptr = struct.unpack('<II', data[current_pos : current_pos + 8])
            directories.append({'name': dir_name, 'first_file_ptr': first_file_ptr})
            current_pos = (name_end + 1 + 3) & ~3
        except (struct.error, IndexError): break
    print(f"Identified {len(directories)} directory entries.")

    # Step B: Process each directory and its file list
    saved_files = set()
    
    for directory in directories:
        next_file_ptr = directory['first_file_ptr']
        
        while next_file_ptr != 0:
            try:
                metadata_chunk = data[next_file_ptr : next_file_ptr + 16]
                _next_ptr_val, _total_size, block_count = struct.unpack('<III', metadata_chunk[:12])
                pointer_table_addr_bytes = metadata_chunk[12:16]
                start_pointer_address = int.from_bytes(pointer_table_addr_bytes, 'little')

                name_start = next_file_ptr + 16
                name_end = data.find(b'\x00', name_start)
                # Build the full file path by joining the directory name and file name
                filename_only = data[name_start:name_end].decode('latin-1')
                full_path = os.path.join(directory['name'], filename_only).replace('\\', '/')
            except (struct.error, IndexError): break

            # De-duplication
            if not full_path or full_path.lower() in saved_files:
                next_file_ptr = _next_ptr_val
                continue

            print(f"\n+ Processing unique file: '{full_path}'")
            saved_files.add(full_path.lower())
            
            start_index = (start_pointer_address - POINTER_TABLE_START) // POINTER_SIZE
            
            if start_index >= len(pointer_table):
                print(f"    ERROR: Calculated start index ({start_index}) is out of range. Skipping.")
                next_file_ptr = _next_ptr_val
                continue
            
            # Take only the FIRST block from the list of duplicates
            target_offset = pointer_table[start_index]
            
            next_pointer_index = start_index + 1
            is_last = (next_pointer_index) >= len(pointer_table)
            next_offset = len(data) if is_last else pointer_table[next_pointer_index]
            compr_size = next_offset - target_offset
            
            output_data = b''
            if compr_size > 0:
                raw_chunk = data[target_offset : target_offset + compr_size]
                if raw_chunk.startswith(CMP_MARKER):
                    try:
                        output_data = zlib.decompress(raw_chunk[ZLIB_START_OFFSET_IN_BLOCK:])
                    except zlib.error as e: print(f"    Decompression error: {e}")
                elif raw_chunk.startswith(PNG_HEADER):
                    output_data = raw_chunk
            
            # Save file with full path
            if output_data:
                try:
                    # --- IMPROVED SAVE LOGIC ---
                    output_filepath = os.path.join(output_dir_path, full_path)
                    # Automatically create all needed subfolders
                    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                    
                    with open(output_filepath, 'wb') as out_f:
                        out_f.write(output_data)
                    print(f"  Success! Saved to: '{output_filepath}'")
                    # ---------------------------------
                except (OSError, ValueError) as e:
                    print(f"    Save error: {e}")
            
            next_file_ptr = _next_ptr_val
            
def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    input_file_path = os.path.join(script_dir, INPUT_FILE)

    if not os.path.exists(input_file_path):
        print(f"ERROR: File '{input_file_path}' not found!")
        return

    with open(input_file_path, 'rb') as f:
        full_data = f.read()
    
    pointer_table = parse_pointer_table(full_data)
    
    if pointer_table:
        unpack_files_with_final_logic(full_data, pointer_table)
        

if __name__ == "__main__":
    main()
