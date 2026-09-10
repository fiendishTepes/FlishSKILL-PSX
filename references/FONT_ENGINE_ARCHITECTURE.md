# 🔤 PS1 4bpp 16x16 Thai Font Engine Architecture

## 1. Hardware Specifications
* **PS1 VRAM Architecture**:
  * 1 MB VRAM (1024x512 pixels at 16-bit color).
  * Text rendering typically uses 4bpp (16 colors per palette) or 8bpp (256 colors).
  * In 4bpp mode, each pixel occupies 4 bits (1 nibble).
  * A 16x16 glyph consumes: `16 pixels * 16 rows * 0.5 bytes = 128 bytes`.

## 2. Row Byte Packing Order
* PS1 GPU `LoadImage` expects:
  * Low nibble (bits 0..3) = Left pixel
  * High nibble (bits 4..7) = Right pixel
  * Row byte formula: `byte = (pixel_right << 4) | (pixel_left & 0x0F)`

## 3. Two-Tier Mark-to-Mark Vertical Elevation
* **Problem**: In Thai typography, vowels (ิ, ี, ึ, ื, ั) and tone marks (่, ้, ๊, ๋, ์) share the upper vertical space. On a 16x16 grid, placing a tone mark directly over an upper vowel without offset causes strokes to collide and disappear.
* **Solution**:
  1. Base consonant + upper vowel rendered at row `oy = 2`.
  2. Tone mark elevated to row `oy = -1` (Rows 0..3).
  3. Merge tone pixels into the glyph composite using pixel maximum blending.

## 4. Locked Baseline Offset (`oy = 1`)
* Every glyph is rendered with a fixed baseline reference at `oy = 1` to prevent Thai text from floating or bouncing irregularly along the line.
