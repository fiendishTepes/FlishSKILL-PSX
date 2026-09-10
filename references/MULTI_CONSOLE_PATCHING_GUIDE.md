# 🕹️ Multi-Console Retro ROM Thai Patching Guide

This guide details the specifications, patch formats, and automation workflows for applying Thai translation mods across 9 retro gaming platforms (PlayStation 1, PSP, Super Famicom/SNES, Game Boy Advance, Nintendo DS, 3DS, Game Boy Color, Game Boy, PC).

---

## 1. Supported Patch Formats & Target Consoles

| Format | Target Consoles | Characteristics | Engine Implementation |
| :--- | :--- | :--- | :--- |
| **PPF3 (PlayStation Patch Format)** | PS1, PSP | Block-based byte replacement designed for large CD/DVD disc images (.bin / .iso) | `patch_cli.py:apply_ppf()` |
| **BPS (Beat Patch Format)** | SFC, GBA, NDS | Modern linear delta patching with built-in CRC32 verification and metadata support | `patch_cli.py:apply_bps()` |
| **IPS (International Patch System)** | SFC, GBA, GBC, GB | Classic 24-bit offset record patching with RLE compression (max file limit 16MB) | `patch_cli.py:apply_ips()` |

---

## 2. MemoryCardTH Keystream Unlocker (`.locked.gz`)

Patches distributed via `http://memorycardth.com/` utilize an anti-tamper keystream layer:

### Algorithm Specification:
1. **ROM Fingerprint Calculation (`mc_rom_key`)**:
   - Extract sample chunks from the base ROM:
     - If `size <= 4MB`: Use entire ROM.
     - If `size > 4MB`: `data = rom[:1MB] + rom[mid:mid+1MB] + rom[-1MB:]`.
   - Compute SHA256 with header: `tag = f"MCTH-webpatch-v1|{size}|".encode("utf-8")`.
   - `key = sha256(tag + data)`.

2. **Keystream Decryption (`mc_xor_keystream`)**:
   - For every 32-byte chunk at offset `off`:
     - Counter block: `blk = key + struct.pack(">I", off // 32)`.
     - Generate 32-byte keystream: `ks = sha256(blk)`.
     - XOR patch payload bytes: `plain[i] = cipher[i] ^ ks[i]`.

3. **Decompression**:
   - Decompress decrypted stream using `gzip.decompress()` to yield the raw `.ppf`, `.bps`, or `.ips` patch payload.

---

## 3. Command-Line Universal Patcher Usage

The `scripts/patch_cli.py` tool automates verification, keystream decryption, and patch application:

```bash
# Automatic detection from catalog.json
python scripts/patch_cli.py --rom "Harvest Moon - Back to Nature (USA).bin" --output "HM_BTN_Thai.bin"

# Explicit patch path
python scripts/patch_cli.py --rom "base.bin" --patch "patch.ppf.locked.gz" --output "patched.bin"
```

---

## 4. Platform-Specific Safety Rules

1. **PlayStation 1 (PS1)**:
   - Base images MUST be raw Mode 2 Form 1 (2,352 bytes per sector).
   - Verify that the game's product ID (e.g. `SLUS-01115`, `SLPS-01368`) matches the patch catalog.
2. **Super Famicom (SFC)**:
   - Check whether the base ROM includes a 512-byte copier header (SMC/SWC). Most BPS patches require **headerless** ROMs (`(size % 1024) == 0`).
3. **Game Boy Advance (GBA)**:
   - Base ROM must match the clean No-Intro SHA1 hash.
