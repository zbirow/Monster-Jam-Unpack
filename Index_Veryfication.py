import os
import struct


# --- Configuration ---
INPUT_FILE = 'Packfile.dat'
OUTPUT_LOG_FILE = 'Index_Verification.txt'

# Analyzed data block
TABLE_START = 0x14CC0
TABLE_END = 0x1F1C0
POINTER_SIZE = 4

# Markers to search for
CMP_MARKER = b'\x21\x43\x4D\x50'
PNG_HEADER = b'\x89\x50\x4E\x47'

def verify_4byte_pointer_list():
    """
    Verifies the hypothesis that the block 0x14CC0-0x1F1C0 is a simple list
    of 4-byte offsets, checking what is located at each of them.
    """
    print(f"--- Verification Script: Testing the 4-byte pointer list hypothesis ---")

    # Reliable file loading
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_path = os.path.join(script_dir, OUTPUT_LOG_FILE)

    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"ERROR: Unable to open input file! {e}")
        return

    # Extract the table itself
    table_data = data[TABLE_START:TABLE_END]
    num_entries = len(table_data) // POINTER_SIZE

    success_count = 0
    failure_count = 0

    print(f"Analyzing {num_entries} potential 4-byte pointers...")

    try:
        with open(output_path, 'w', encoding='utf-8') as log_file:
            header = f"{'Entry #':<8} | {'Pointer Value (Hex)':<20} | {'Status'}\n"
            log_file.write(header)
            log_file.write("-" * (len(header) - 1) + "\n")

            # Loop through all 4-byte chunks
            for i in range(num_entries):
                offset_in_table = i * POINTER_SIZE
                chunk = table_data[offset_in_table : offset_in_table + POINTER_SIZE]

                # Read the pointer
                target_offset = struct.unpack('<I', chunk)[0]

                # Default status
                status = "[✗ MARKER ERROR]"

                # Check if the address is within file bounds
                if target_offset + 4 <= len(data):
                    # Get the first 4 bytes from the target location
                    header_bytes = data[target_offset : target_offset + 4]

                    if header_bytes == CMP_MARKER:
                        status = "[✓ MATCH - !CMP]"
                        success_count += 1
                    elif header_bytes == PNG_HEADER:
                        status = "[✓ MATCH - PNG]"
                        success_count += 1
                    else:
                        failure_count += 1
                else:
                    status = "[✗ ADDRESS ERROR]"
                    failure_count += 1

                # Format and write the line to the log file
                line = f"{i:<8} | 0x{target_offset:016X} | {status}\n"
                log_file.write(line)

            # Write summary at the end of the log file
            log_file.write("\n" + "="*40 + "\n")
            log_file.write("           VERIFICATION SUMMARY\n")
            log_file.write("="*40 + "\n")
            log_file.write(f" Pointers scanned:         {num_entries}\n")
            log_file.write(f" Correct (matching):      {success_count}\n")
            log_file.write(f" Incorrect (not matching): {failure_count}\n")
            log_file.write("="*40 + "\n")

    except Exception as e:
        print(f"ERROR: An error occurred during processing or writing the log file! {e}")
        return

    print(f"\nSuccess! Full verification log has been saved to file:")
    print(f"-> {output_path}")
    print("\nSummary:")
    print(f"  Correct:   {success_count}")
    print(f"  Incorrect: {failure_count}")

if __name__ == "__main__":
    verify_4byte_pointer_list()
