# Monster-Jam-Unpack


## Structures

| Start Aderss | End Adress | Type |
| ------------ | ---------- | ----- |
| 0x0 | 0x0 | Header |
| 0x00 | 0x100 | Folders |
| 0x110 | 14CB0 | Files Name |
| 0x14CC0 | 0x1F1C0 | Index |
| 1F200 | END | Files Data |

### Header
Hex `50 41 4B 00 C8 F1 01 00 0C 00 00 00` - First 12 bytes

### Folders
Hex `28 00 00 00 0C 01 00 00 70 63 2F 67 6C 6F 62 61 6C 73 2F 70 68 79 73 69 63 73`

| Meta | Folder Name |
| ---- | --------- |
| 28 00 00 00 0C 01 00 00 | pc/globals/physics |

### Files Name
Hex `00 00 00 00 00 E6 03 00 00 17 00 00 00 C0 4C 01 00 6D 61 74 61 74 74 72 2E 74 78 74`

| Meta | File Name |
| ---- | --------- |
| 00 00 00 00 00 E6 03 00 00 17 00 00 00 C0 4C 01 00 | matattr.txt |

### Index
- The Main Index Table is a contiguous, un-interrupted array consisting of 2,640 entries. Each entry has a fixed size of 16 bytes.
- Each 16-byte entry in the table is a C-style struct composed of four 4-byte, 32-bit unsigned integers, stored in little-endian byte order.

| Offset (in entry) |	Field Name |	Data Type	| Description |
| ----------------- | ---------- | --------- | ------------ |
| 0x00 - 0x03 |	offset | uint32_t |	Absolute file offset. This value points to the exact starting byte of the data chunk within the Packfile.dat file. |
| 0x04 - 0x07 |	compressed_size |	uint32_t |	Compressed Size. This is the number of bytes to read from the file, starting at the offset. It represents the physical on-disk size of the data chunk. |
| 0x08 - 0x0B |	original_size |	uint32_t |	Original Size. This is the expected size of the data after it has been processed (e.g., decompressed). |
| 0x0C - 0x0F |	flags_or_crc |	uint32_t |	Flags or CRC. The exact purpose of this field is currently unknown. It may contain a checksum (like CRC32) for data integrity or a bitfield of flags for processing. |


### Files Data
 
Hex `21 43 4D 50 B3 00 00 00 78 9C 0B 49 AD 28 29 2D`

| ident. | meta | zlib header | zlib Data |
| ------ | ---- | ----------- | ----- |
| 21 43 4D 50 | np. B3 00 00 00 | 78 9C | np. 0B 49 AD 28 29 2D... |
