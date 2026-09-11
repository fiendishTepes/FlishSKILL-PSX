# 🛡️ FlishSKILL-PSX: PlayStation 1 & Multi-Console Thai Translation Skill

> **Universal Knowledge Base, Hard Constraints, and Automation Toolkit for PlayStation 1 (PSX/PS1) & Multi-Platform Retro Console Thai ROM Translation**  
> *Developed for Retro Translation Studio by Fiendish Tepes*

[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-blue.svg)](https://github.com/fiendishTepes/FlishSKILL-PSX)
[![Platforms](https://img.shields.io/badge/Platforms-PS1%20%7C%20PSP%20%7C%20SFC%20%7C%20GBA%20%7C%20NDS-orange.svg)]()
[![Catalog: 112 Games](https://img.shields.io/badge/Catalog-112%20Thai%20Games-brightgreen.svg)]()
[![Language: Python 3](https://img.shields.io/badge/Language-Python%203.10%2B-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## 🌟 Overview

**FlishSKILL-PSX** is a production-grade Antigravity AI skill and modding suite engineered for:
1. **PlayStation 1 Deep Modding**:
   * Custom 4bpp 16x16 Thai font rendering with 1px drop shadow, 2-tier mark-to-mark elevation, and tall-stem restoration.
   * **Dual-Syllable Compound Tiles**: Pairs narrow vowels with consonants (`มา`, `จะ`, `นำ`, `ไป`, `ใน`, `ได้`, `ไม่`, `เมื่`, `เยื`, `เรื่`) in single 16x16 tiles, eliminating 10-12px voids and "jagged teeth" spacing.
   * **Universal Mark-Guard Tokenizer**: Boundary protection preventing consonant stealing and eliminating detached floating marks (0 detached marks game-wide).
   * **Graceful Fallback Decomposition**: 91 guaranteed base characters with safe runtime fallback for unmapped clusters.
   * VRAM buffer protection (preventing 74,880B font overflow into adjacent tilemaps).
   * Sequential bytecode event parsing (preventing cascading 3D triangle GPU crash cascades).
   * CD-ROM XA Mode 2 Form 1 sector injection and automated CHD compression.
   * MIPS R3000 assembly trainer & starting fund injection (e.g. 983,040 Gold in `SLPS_013.68`).
2. **Universal Multi-Console Retro Patching**:
   * Pure Python patch engines for **PPF3** (PS1, PSP), **BPS** (SFC, GBA, NDS), and **IPS** (SFC, GB, GBA).
   * Proprietary MemoryCardTH keystream unlocker (`mc_rom_key` + `mc_xor_keystream`) for encrypted `.locked.gz` patch files.
   * Comprehensive database of **112 Thai translation projects across 9 consoles** with SHA1 verification.

---

## 📁 Repository Structure

```text
FlishSKILL-PSX/
├── SKILL.md                                # Antigravity Skill Definition
├── README.md                               # Master Documentation & Setup Guide
├── references/                             # Architectural Runbooks & Manuals
│   ├── RULES_AND_CONSTRAINTS.md            # Anti-crash laws & hardware constraints
│   ├── MULTI_CONSOLE_PATCHING_GUIDE.md     # PPF, BPS, IPS, and MCTH keystream guide
│   ├── PS1_TRAINER_ASSEMBLY_HACKING.md     # MIPS assembly New Game trainer guide
│   ├── RETRO_CONSOLE_CATALOG.md            # 112-game Thai patch catalog & SHA1 table
│   ├── FONT_ENGINE_ARCHITECTURE.md         # 4bpp 16x16 font & Compound Tile architecture
│   ├── REVERSE_ENGINEERING_GUIDE.md        # Script bytecode & pointer relocation
│   └── ISO_REPACKING_PLAYBOOK.md           # CD-ROM sector injection & CHD guide
├── scripts/                                # Production Automation Toolkit
│   ├── patch_cli.py                        # Universal CLI patcher (PPF/BPS/IPS/MCTH)
│   ├── patch_slps_gold_trainer.py          # MIPS assembly starting gold injector
│   ├── build_retro_pixel_font_4bpp.py      # Authentic 16x16 pixel font & compound tile builder
│   ├── generate_thai_font_4bpp.py          # 4bpp 16x16 TTF font generator with drop shadow
│   ├── prioritize_clusters.py              # Intelligent cluster prioritizer with Mark-Guard
│   ├── repack_iso.py                       # Sector-accurate CD-ROM injector & CHD builder
│   └── verify_build_safety.py              # Automated pre-flight validator
└── templates/                              # Schemas, Catalogs & Tables
    ├── catalog.json                        # 112-game database with SHA1 checksums
    ├── thai_table.json                     # 422-token mapping table
    └── universal_thai_table.tbl            # Standard ROM hacking TBL file
```

---

## 🛡️ The 8 Master Rules (Anti-Crash Guarantee)

1. **Font Size Lock**: Font container size must NEVER exceed native allocation (e.g. 74,880 bytes). Any overflow bleeds into scene VRAM buffers causing rainbow static.
2. **Bytecode Preservation**: Cutscene dialogues contain internal opcodes (`0x1912`, `0x1802`). Overwriting with unescaped text or zeros (`0x0000`) causes the GPU to render cascading 3D triangles.
3. **Sector Boundary Rule**: Mode 2 Form 1 CD sectors require files to be exact multiples of 2,048 bytes (e.g. 37 sectors = 75,776 bytes).
4. **Pointer Relocation**: When expanded Thai text exceeds native limits, relocate to trailing free space and update 32-bit RAM pointers (`RAM_BASE + File_Offset`).
5. **Surgical Assembly Patching**: When injecting cheats/trainers, replace existing redundant opcodes without displacing surrounding function pointers.
6. **Dual-Syllable Compound Tiles**: Precompose high-frequency syllables into single 16x16 tiles to eliminate 10-12px monospace kerning voids ("สระห่างเป็นฟันปลา").
7. **Universal Mark-Guard**: Never match a 2-character compound if followed by a vowel or tone mark (`MARKS = set('่้๊๋์ิีึืั็ุู')`), ensuring 0 detached marks.
8. **Guaranteed Fallback Set**: Always guarantee all 46 consonants and 23 standalone marks; unmapped clusters decompose safely without crash.

---

## 💻 Installation as an Antigravity Skill

To load this skill in your Antigravity environment:

```bash
# Clone directly into your global Antigravity skills directory
git clone https://github.com/fiendishTepes/FlishSKILL-PSX.git ~/.gemini/config/skills/FlishSKILL-PSX
```

---

## 📜 License
MIT License. Created by Fiendish Tepes for Retro Translation Studio.
