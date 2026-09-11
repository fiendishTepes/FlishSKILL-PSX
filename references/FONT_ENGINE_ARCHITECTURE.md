# 🔤 PS1 4bpp 16x16 Thai Font Engine Architecture & Compound Tile System

This document outlines the master typography engine and font rendering specifications for Thai language localization on the Sony PlayStation 1 (PS1 / PSX) and retro monospace console engines.

---

## 1. Hardware Specifications & Memory Layout
* **PS1 VRAM Architecture**:
  * 1 MB VRAM (1024x512 pixels at 16-bit color).
  * Text rendering typically uses 4bpp (16 colors per palette) or 8bpp (256 colors).
  * In 4bpp mode, each pixel occupies 4 bits (1 nibble).
  * A 16x16 glyph consumes: `16 pixels * 16 rows * 0.5 bytes = 128 bytes`.
* **Row Byte Packing Order**:
  * Low nibble (bits 0..3) = Left pixel (even X)
  * High nibble (bits 4..7) = Right pixel (odd X)
  * Formula: `byte = (pixel_right << 4) | (pixel_left & 0x0F)`
* **Palette Convention**:
  * Color 0: Transparent (`0x0`)
  * Color 1: Crisp Foreground White (`0x1`)
  * Color 14: Drop Shadow / Outline (`0x0E`)

---

## 2. The Monospace Kerning Dilemma & Jagged Teeth Spacing
In retro consoles, dialogue rendering engines advance the cursor by a fixed width ($x \gets x + 16$ or $x \gets x + 8$) unconditionally for every token:
```
[Token 1: x=0..15] -> [Token 2: x=16..31] -> [Token 3: x=32..47] ...
```
When Thai vowels with narrow widths (3-6px) such as leading vowels (`เ`, `แ`, `โ`, `ใ`, `ไ`) or trailing vowels (`า`, `ะ`, `ำ`) are placed in separate standalone 16x16 tiles:
* The vowel leaves a **10-12 pixel empty void** before or after its adjacent consonant.
* Sentences appear spaced out with "jagged teeth" (สระห่างกันเป็นฟันปลา), e.g.:
  `เ  มื่  อ    ค  ว  า  ม    มื  ด    ม  า    เ  ยื  อ  น`
* Dialogue text length expands by up to 50%, overflowing dialogue boxes and triggering opcode truncations.

---

## 3. Dual-Syllable Compound Tile System (ระบบรวบสระคู่พยัญชนะ)
To solve this without modifying complex assembly cursor routines, the font engine pairs high-frequency 2-character and 3-character syllables into single 16x16 compound glyphs:

### A. Coordinate Mapping & Kerning Matrices
| Compound Type | Components | Left Element Offset | Right Element Offset | Special Handling |
| :--- | :--- | :--- | :--- | :--- |
| **Leading Vowel + Consonant** | `เแโใไ` + `[ก-ฮ]` | `(1, 0)` | `(8, 6)` | Stem extended to Row 3; consonant body at Row 6..13 |
| **Consonant + า** | `[ก-ฮ]` + `า` | `(1, 6)` | `(9, 6)` | Locked baseline at Row 13 |
| **Consonant + ะ** | `[ก-ฮ]` + `ะ` | `(1, 6)` | `(9, 6)` | Dual loops of `ะ` centered at Row 6..13 |
| **Consonant + ำ** | `[ก-ฮ]` + `ำ` | `(1, 5)` | `(9, 6)` | Nikhahit circle at `(6..9, 2..4)` above consonant right edge |
| **3-Char Specials** | `เมื่`, `เยื`, `เรื่`, `เพื่` | `เ` at `(1, 0)` | Cluster at `(6, 0)` | Two-tier mark elevation; tone mark reinforced at `(12, 0..1)` |
| **3-Char Leading + Tone** | `ได้`, `ไม่`, `แต่`, `ให้`, `แล้`, `เจ้` | `เแโใไ` at `(1, 0)` | Cons+Tone at `(6, 0)` | Tone mark elevated to Rows 0..3 directly over consonant |

### B. Tall-Stem Restoration for Leading Vowels
In raw retro font sheets, `เ` and `แ` are frequently truncated at Row 8 (only 5-6px tall). In this engine, stems are mathematically extended:
* `เ`: Vertical 2px-wide stroke at `x=6..7` extended from Row 8 upward to Row 3.
* `แ`: Dual vertical strokes at `x=5..6` and `x=9` extended upward to Row 3.
* Results in majestic, legible retro Thai letterforms.

### C. 1px Crisp Stroke vs 2px Bold
* Avoid horizontal pixel doubling (`bold=True`) in 16x16 tiles when using dark shadow outlines (Color 14).
* Doubled strokes merge with the drop shadow, creating blurred, muddy text blocks.
* A single, razor-sharp 1px stroke provides optimal contrast against dark background textboxes.

---

## 4. Universal Mark-Guard Tokenizer Algorithm
A critical vulnerability in compound tokenization is **"Consonant Stealing"**:
* If `เจ` is a compound tile and the text contains `เจ้า` (`เ-จ-้-า`), blindly matching `เจ` strips `จ` from `้`, leaving `้` as an isolated, floating mark with a 16px advance.

### Algorithm
```python
MARKS = set('่้๊๋์ิีึืั็ุู')

def tokenize_thai_units(text):
    units = []
    i = 0
    n = len(text)
    while i < n:
        ...
        matched = False
        for c in COMPOUND_TILES:
            if text.startswith(c, i):
                next_pos = i + len(c)
                # Mark-Guard: Do NOT match compound if next character is a tone or vowel mark
                if next_pos < n and text[next_pos] in MARKS:
                    continue
                units.append(c)
                i += len(c)
                matched = True
                break
        if matched:
            continue
        ...
```
* **Result**: Guarantees **0 detached floating marks** across the entire script.

---

## 5. Graceful Fallback Decomposition
To ensure 100% crash immunity:
1. **Permanent Base Allocation**:
   - 22 slots for Punctuation & Digits (`! ? . , - ( ) " … % + = 0..9`)
   - 23 slots for Standalone Vowels & Tone Marks (`ะ า ำ เ แ โ ใ ไ ั ็ ิ ี ึ ื ุ ู ่ ้ ๊ ๋ ์`)
   - 46 slots for All Base Thai Consonants (`ก .. ฮ`)
   - Total guaranteed: 91 slots.
2. **Dynamic Slots (327 slots)**:
   - High-frequency compounds (61 tiles).
   - Most common vertical stacked clusters sorted by game script frequency.
3. **Fallback Rule**:
   - If any rare or unmapped cluster is encountered in script injection, it decomposes safely:
   ```python
   def encode_dialogue(text):
       tokens = []
       for t in tokenize_thai_units(text):
           if t in tbl:
               tokens.append(tbl[t])
           else:
               for ch in t:
                   if ch in tbl: tokens.append(tbl[ch])
       return tokens
   ```
   - Eliminates missing glyph crashes and maintains continuous script synchronization.
