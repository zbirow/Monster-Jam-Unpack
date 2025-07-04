
# File Format Documentation
This document describes the structure of the .dat archive files used in the game. The format is a custom container, referred to internally as "PAK", designed for efficient asset loading.

## Overall Structure
The archive is composed of a single, continuous header section followed by a "heap" of data chunks. The header contains all the necessary metadata to locate and interpret the data chunks.
Section	Start Address	End Address	Description
### Main Header	
0x0	- 0x1F1FF
- A large metadata block containing all file and folder definitions and indices.
### Data Heap
0x1F200	- End of File
- A contiguous block containing all physical data chunks (!CMP and raw).



## Main Header
The Main Header is a complex structure composed of several sequential tables.


### Global Header (12 bytes)
The file begins with a 12-byte global header.
Hex: 50 41 4B 00 C8 F1 01 00 0C 00 00 00


| Offset	| Size |	Data Type	| Description	| Value |
| ------ | ---- | --------- | ----------- | ------------- |
| 0x00	| 4	| char[4]	| Magic Identifier. Reads as "PAK" (\0 terminated). |	50 41 4B 00 |
| 0x04	| 4	| uint32_t	| Total size in bytes of the entire header section.	| 0x01F1C8 |
| 0x08	| 4	| uint32_t	| The total number of folder entries in the Directory Table.	| 12 |


### Directory Table
This table immediately follows the Global Header. It lists all the virtual folders within the archive.
Structure: A list of variable-length entries. Each entry consists of 8 bytes of metadata followed by a null-terminated folder name string.
Hex: 28 00 00 00 0C 01 00 00 70 63 2F...


| Offset	| Size	| Data Type	| Description	| Value |
| ------ | ---- | --------- | ----------- | ------------- |
| 0x00	| 4	| int32_t	| A unique ID for the folder. Its specific purpose is unknown.|	0x00000028 (40) |
| 0x04	| 4	| uint32_t	| A pointer (absolute file offset) to the first file entry in the File Table that belongs to this directory.	| 0x0000010C |
| 0x08	| ?	| char[]	| The null-terminated path of the folder.	| pc/globals/physics |


### File Table
This is the main "logical" file manifest, structured as a linked list.
Structure: A list of variable-length entries. Each entry consists of 16 bytes of metadata followed by a null-terminated file name string.
hex:  6D 61 74 61 74 74 72 2E 74 78 74 00

| Offset |	Size |	Data Type	| Description |
| ------ | ---- | --------- | ----------- |
| 0x00	| 4	| uint32_t	| Pointer to Next File. An absolute file offset pointing to the next file entry within the same folder. A value of 0 signifies the end of the list for that directory, implementing a linked list structure. |
| 0x04	| 4	| uint32_t	| Total Original Size. The total, final size in bytes of the asset after all its constituent data chunks have been processed (e.g., decompressed) and concatenated. |
| 0x08	| 4	| uint32_t	| This integer specifies how many consecutive entries in the Pointer Table belong to this file. |
| 0x0C	| 4	| uint32_t	| Start Index in Pointer Table. This is the zero-based index (e.g., 0, 1, 17, 550) that specifies which entry in the Pointer Table is the first one associated with this file. |
| 0x10	| ?	| char[]	| File Name. A null-terminated string containing the full, virtual path of the file. |


### Pointer Table (Index)
This is a low-level, flat array of pointers.
It maps logical file chunks to their physical locations.

- **Location:** 0x14CC0 - 0x1F1BF
- **Structure:** A simple array of 10,560 entries.
- **Entry Size:** 4 bytes.
- **Format:** Each 4-byte entry is a uint32_t (little-endian) representing an absolute file offset to the start of a physical data chunk in the Data Heap.

Example:

C0 F2 77 1C -> 0x1C77F2C0

40 25 3C 1D -> 0x1D3C2540



## Data Heap
This section contains the actual asset data.

### Compressed Chunks (!CMP)
Identifier: Begins with the 4-byte marker !CMP (21 43 4D 50).
Structure:
| Offset (in chunk) | Size | Data Type | Description | Example Value |
| :---------------- | :--- | :--------- | :------------------------------------------------------------------------------------------------------------ | :-------------- |
| 0x00 | 4 | char[4] | The !CMP identifier. | 21 43 4D 50 |
| 0x04 | 4 | uint32_t | Authoritative Original Size. The size of the data after decompression. This value should be trusted. | B3 00 00 00 |
| 0x08 | ? | byte[] | The zlib data stream, which typically begins with 78 9C. The end of this stream must be auto-detected. | 78 9C ... |

### Raw Chunks (e.g., PNG)
- **Identifier:** Begins with the file's native header.
-  **Example (PNG):** 89 50 4E 47 0D 0A 1A 0A ...
- **Processing:** This data should be copied directly from the archive without any decompression. The size of the chunk must be determined by calculating the difference between its offset and the offset of the next chunk in the Pointer Table.



