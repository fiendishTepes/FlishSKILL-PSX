---
name: psx-thai-translation
description: >-
  Comprehensive skill and master knowledge base for PlayStation 1 (PSX / PS1) Thai translation modding.
  Covers custom 4bpp 16x16 Thai font rendering, mark-to-mark vertical tone elevation, baseline locking,
  VRAM buffer safety (preventing GPU cascade crashes), CD-ROM sector alignment (2048/2352 bytes),
  script event bytecode vs text stream decoding, 32-bit RAM pointer relocation, and automated CHD building.
  Activate this skill when translating, hacking, reverse engineering, or creating Thai mods for PS1 games.
---

# 🎮 PSX Thai Translation & ROM Hacking Skill (FlushSKILL-PSX)

This skill provides end-to-end workflows, reverse-engineering runbooks, technical invariants, and automated tools for creating professional, stable Thai translation mods for Sony PlayStation 1 (PS1/PSX) games.

---

## ⚡ Quick Reference: Hard Technical Invariants

When working on PS1 Thai translation mods, NEVER violate these four cardinal rules:

1. **VRAM Buffer Boundary (No Overflow)**:
   * Dialogue font files (e.g. `MSG_CG.BIN`) load directly into PS1 RAM (e.g. `0x80110000`).
   * Overwriting beyond the allocated font size corrupts the adjacent VRAM tilemap buffer (e.g. `0x80122500`), turning background graphics into rainbow static or triggering GPU packet corruption.
   * **Rule**: Keep font files at their exact native byte size (e.g. 74,880 bytes).

2. **Bytecode Event vs Text Stream (No Blind Overwrite)**:
   * Cutscene dialogue blocks are interleaved with engine opcodes: camera control (`0x1912`), entity sprites (`0x1802`), and animation triggers (`0x1D12`).
   * Padded zeros (`0x0000`) or unescaped text in opcode zones are interpreted by the PS1 GPU as polygon drawing packets, causing cascading 3D triangle screen corruption.
   * **Rule**: Preserve all header opcodes and ensure each section's total length matches its native boundary exactly.

3. **CD-ROM Sector Alignment (Exact Multiples of 2,048B / 2,352B)**:
   * PS1 CD-ROMs use Mode 2 Form 1 (2,048 bytes user data per 2,352-byte raw sector).
   * Any file injected into a base ISO must fit within its allocated sector span. If a file is 37 sectors, it must be padded with `0x00` to exactly `37 * 2,048 = 75,776 bytes`.

4. **32-Bit RAM Pointer Relocation for Expanded Thai Text**:
   * If a translated text is longer than the original slot (e.g. shop tutorials, NPC talk tables), relocate the entire text block to free trailing space in RAM and update the 32-bit pointer table (RAM Address = `RAM_BASE + File_Offset`).

---

## 🛠️ Reusable Tools & Scripts in this Skill

| Script | Purpose | Path |
| :--- | :--- | :--- |
| `generate_thai_font_4bpp.py` | Generates authentic 16x16 4bpp font tiles with 1px drop shadow and 2-tier mark-to-mark elevation | [`scripts/generate_thai_font_4bpp.py`](./scripts/generate_thai_font_4bpp.py) |
| `prioritize_clusters.py` | Smart Thai cluster compiler; extracts vocabulary and fits into 418 glyph slots | [`scripts/prioritize_clusters.py`](./scripts/prioritize_clusters.py) |
| `repack_iso.py` | Injects modified binaries directly at exact CD LBA sectors and converts to CHD | [`scripts/repack_iso.py`](./scripts/repack_iso.py) |
| `verify_build_safety.py` | Automated pre-flight checker for VRAM limits, sector sizes, and missing tokens | [`scripts/verify_build_safety.py`](./scripts/verify_build_safety.py) |

---

## 📖 Deep Technical References

For detailed architecture diagrams and step-by-step case studies, read:
* [Master Rules & Crash Prevention Guide](./references/RULES_AND_CONSTRAINTS.md)
* [Thai Font Engine Architecture & Vertical Stacking](./references/FONT_ENGINE_ARCHITECTURE.md)
* [PS1 Script Reverse Engineering & Bytecode Playbook](./references/REVERSE_ENGINEERING_GUIDE.md)
* [CD-ROM Sector Patching & CHD Compression](./references/ISO_REPACKING_PLAYBOOK.md)

---

## 🚀 Standard Workflow for a New PS1 Game

1. **Extract Base ROM**: Extract target files (overlays, executables, font graphics) using Mode 2 Form 1 extractors.
2. **Reverse Engineer Font Format**: Identify whether the game uses 4bpp 16x16, 8x16 1bpp, or TIM format.
3. **Compile Thai Glyph Table**: Run `prioritize_clusters.py` to create `thai_table.json` with tone marks and precomposed clusters.
4. **Generate Font Binary**: Run `generate_thai_font_4bpp.py` to bake glyphs into the game's font container.
5. **Translate & Inject**:
   - For sequential cutscenes: Match section byte boundaries and preserve opcodes.
   - For pointer-based dialogue: Use trailing space relocation and update pointer tables.
6. **Repack & Test**: Inject modified files into the disc image with `repack_iso.py` and test in DuckStation.
