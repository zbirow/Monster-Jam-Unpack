# Monster-Jam-Unpack


## Structures

| Start Aderss | End Adress | Type |
| ------------ | ---------- | ----- |
| 0x0 | 0x0 | Header |
| 0x00 | 0x100 | Folders |
| 0x110 | 14CB0 | Files Name |
| 0x14CC0 | 0x1F1C0 | Meta |
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

### Meta
------


### Files Data
 
Hex `21 43 4D 50 B3 00 00 00 78 9C 0B 49 AD 28 29 2D`

| ident. | Size | zlib header | zlib Data |
| ------ | ---- | ----------- | ----- |
| 21 43 4D 50 | np. B3 00 00 00 | 78 9C | np. 0B 49 AD 28 29 2D... |


# Info!!!

#### The file contains many of the same files. This is because the game loads a given amount of blocks from one location to load them as quickly as possible. Instead of looking for each file separately, it takes the location of the starting block and takes a given amount of them.



