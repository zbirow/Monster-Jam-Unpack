# Monster-Jam-Unpack
* Documentation is in development. Not all information may be correct!!

* I know how this file works, I already know how to handle file names during export, and to export only one file without duplicates.

* I also know how to pack the data correctly.

* When I have time, I will write the correct tools, but it may take some time.

* Currently, I do not know how to assign directories


## Structures

| Start Aderss | End Adress | Type |
| ------------ | ---------- | ----- |
| 0x0 | 0x0 | Header |
| 0x00 | 0x100 | Folders |
| 0x110 | 14CB0 | Files Name |
| 0x14CC0 | 0x1F1C0 | Index |
| 0x1F200 | 0x47973AD0 | Files Data |

### Header
Hex `50 41 4B 00 C8 F1 01 00 0C 00 00 00` - First 12 bytes

### Folders
Hex `28 00 00 00 0C 01 00 00` `70 63 2F 67 6C 6F 62 61 6C 73 2F 70 68 79 73 69 63 73`

| Meta | Folder Name |
| ---- | --------- |
| 28 00 00 00 0C 01 00 00 | pc/globals/physics |

### Files Name
Hex `00 00 00 00 00 E6 03 00 00 ` `17 00 00 00 ` `C0 4C 01 00 ` `6D 61 74 61 74 74 72 2E 74 78 74`

| Meta | Amount | Index Adress | File Name |
| ---- | ------ | --------- | ------------ |
| 00 00 00 00 00 E6 03 00 00 | 23 | 014CC0 | matattr.txt |

### index
- Each 4-byte entry is a uint32_t (little-endian) representing an file offset.
`C0 F2 77 1C` `40 25 3C 1D` `40 25 44 1E` `80 A7 5C 1F`

| Hex | Addres (h) |
| --- | ------ |
| C0 F2 77 1C | 1C77F2C0 |
| 40 25 3C 1D | 1D3C2540 |
| 40 25 44 1E | 1E442540 |
| 80 A7 5C 1F | 1F5CA780 |


### Files Data
 
Hex `21 43 4D 50` `B3 00 00 00` `78 9C` `0B 49 AD 28 29 2D` - !CMP

Hex2 `89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52` - PNG

| ident. | Size | zlib header | zlib Data |
| ------ | ---- | ----------- | ----- |
| 21 43 4D 50 | np. B3 00 00 00 | 78 9C | np. 0B 49 AD 28 29 2D... |



# Info!!!

#### The file contains many of the same files. This is because the game loads a given amount of blocks from one location to load them as quickly as possible. Instead of looking for each file separately, it takes the location of the starting block and takes a given amount of them.



