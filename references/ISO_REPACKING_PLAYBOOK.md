# 💿 PS1 CD-ROM Sector Patching & CHD Playbook

## 1. CD-ROM XA Mode 2 Form 1
* Each CD sector is 2,352 bytes:
  * Sync bytes: 12 bytes (`00 FF FF ... FF 00`)
  * Header: 4 bytes (Minute, Second, Sector, Mode)
  * Sub-header: 8 bytes (File, Channel, Sub-mode, Coding)
  * **User Data Payload: 2,048 bytes (Offset 24..2072)**
  * EDC / ECC: 280 bytes error detection & correction

## 2. Direct LBA Injection
* Compute file starting LBA: `LBA = file_sector_number`
* Byte offset in `.bin`: `Offset = LBA * 2352 + 24`
* Write user data in 2,048-byte chunks, advancing 2,352 bytes per sector.

## 3. Compression to CHD
```bash
chdman createcd -i input.cue -o output.chd -f
```
