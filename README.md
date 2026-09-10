# 🛡️ FlushSKILL-PSX: PS1 Thai Translation Modding Skill

> **Universal Knowledge Base, Hard Constraints, and Automation Toolkit for PlayStation 1 (PSX/PS1) Thai ROM Translation**  
> *Developed for Retro Translation Studio by Fiendish Tepes*

[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-blue.svg)](https://github.com/fiendishTepes/FlushSKILL-PSX)
[![Platform: PS1](https://img.shields.io/badge/Platform-Sony%20PlayStation%201-lightgrey.svg)]()
[![Language: Python 3](https://img.shields.io/badge/Language-Python%203.10%2B-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## 🌟 Overview

Translating PlayStation 1 games into Thai presents unique technical challenges due to the hardware limitations of the 1990s:
* **No dynamic font rendering**: PS1 lacks HarfBuzz, FreeType, or native Unicode support.
* **Tight VRAM budgets**: Font tiles are stored in raw 4bpp/8bpp formats sharing RAM with scene tilemaps.
* **Complex Thai vertical stacking**: Consonants, upper vowels, and tone marks stack up to 3 levels high.
* **Opcodes interleaved in text**: Script event interpreters mix dialogue text directly with GPU rendering opcodes.

**FlushSKILL-PSX** encapsulates the complete reverse-engineering methodology, anti-crash laws, and automation pipeline developed during the full translation of *Chou Mashin Eiyuuden Wataru: Another Step (PS1)*.

---

## 📁 Repository Structure

```text
FlushSKILL-PSX/
├── SKILL.md                          # Antigravity Skill Definition
├── README.md                         # Project Documentation
├── references/                       # Deep Architectural Runbooks
│   ├── RULES_AND_CONSTRAINTS.md      # Anti-crash laws & hard constraints
│   ├── FONT_ENGINE_ARCHITECTURE.md   # 4bpp 16x16 Thai font rendering guide
│   ├── REVERSE_ENGINEERING_GUIDE.md  # Script bytecode & pointer relocation
│   └── ISO_REPACKING_PLAYBOOK.md     # CD-ROM sector injection & CHD guide
├── scripts/                          # Production Automation Tools
│   ├── generate_thai_font_4bpp.py    # 4bpp 16x16 font generator with drop shadow
│   ├── prioritize_clusters.py        # Intelligent Thai cluster prioritization
│   ├── repack_iso.py                 # Sector-accurate CD-ROM injector & CHD builder
│   └── verify_build_safety.py        # Automated pre-flight validator
└── templates/                        # Reusable Schemas and Tables
    ├── thai_table.json               # 422-token mapping table
    └── universal_thai_table.tbl      # Standard ROM hacking TBL file
```

---

## 🛡️ The 4 Master Rules (Anti-Crash Guarantee)

1. **Font Size Lock**: Font container size must NEVER exceed native allocation (e.g. 74,880 bytes). Any overflow bleeds into scene VRAM buffers causing rainbow static.
2. **Bytecode Preservation**: Cutscene dialogues contain internal opcodes (`0x1912`, `0x1802`). Overwriting with unescaped text or zeros (`0x0000`) causes the GPU to render cascading 3D triangles.
3. **Sector Boundary Rule**: Mode 2 Form 1 CD sectors require files to be exact multiples of 2,048 bytes (e.g. 37 sectors = 75,776 bytes).
4. **Pointer Relocation**: When expanded Thai text exceeds native limits, relocate to trailing free space and update 32-bit RAM pointers (`RAM_BASE + File_Offset`).

---

## 💻 Installation as an Antigravity Skill

To load this skill in your Antigravity environment:

```bash
# Clone directly into your Antigravity skills directory
git clone https://github.com/fiendishTepes/FlushSKILL-PSX.git ~/.gemini/config/skills/FlushSKILL-PSX
```

Or reference it in your workspace `.agents/skills/` directory.

---

## 📜 License
MIT License. Created by Fiendish Tepes for Retro Translation Studio.
