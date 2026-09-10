#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chou Mashin Eiyuuden Wataru: Another Step (PS1)
Authentic 4bpp 16x16 Font Generator for MSG_CG.BIN with Mark-to-Mark Thai Stacking

Exact PS1 Hardware / Engine Specifications:
- Font Base RAM Address: 0x80115300 (Offset 0x5300 in MSG_CG.BIN)
- Glyphs 0..165 (0x0000..0x5300): 8x16 system font (preserved untouched!)
- Dialogue Glyphs (0x5300+): 16x16 4bpp (128 bytes per glyph)
- Token Math: Token N -> Offset 0x5300 + N * 128
- Row Format: 16 pixels = 8 bytes. byte = (pixel_right << 4) | (pixel_left & 0x0F)
- Color 0: Transparent (0x0)
- Color 1: White Foreground (0x1)
- Color 14: Drop Shadow / Dark Outline (0x0E)
"""

import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)
from prioritize_clusters import get_prioritized_clusters

# Paths: check if running inside Wataru studio or standalone on another machine
BASE_DIR = r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru"
FONT_DIR = os.path.join(BASE_DIR, "03_FONT_ENGINE")
BIN_PATH = "D:/mod-thai/Retro_Trans_Studio/PS1/Wataru/Chou Mashin Eiyuuden Wataru - Another Step (Japan).bin"

if os.path.exists(BASE_DIR):
    MSG_CG_PATH = os.path.join(BASE_DIR, "02_EXTRACTED", "FM16", "MSG_CG.BIN")
    TABLE_PATH = os.path.join(FONT_DIR, "thai_table.json")
    PREVIEW_PATH = os.path.join(FONT_DIR, "wataru_4bpp_font_grid.png")
else:
    # Standalone mode on any machine
    OUTPUT_DIR = os.path.join(REPO_ROOT, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    MSG_CG_PATH = os.path.join(OUTPUT_DIR, "MSG_CG.BIN")
    TABLE_PATH = os.path.join(REPO_ROOT, "templates", "thai_table.json")
    PREVIEW_PATH = os.path.join(OUTPUT_DIR, "thai_4bpp_font_grid.png")

# Auto-detect standard Thai TTF fonts across platforms (Windows, Linux, macOS)
TTF_CANDIDATES = [
    "C:/Windows/Fonts/tahomabd.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/thai/Garuda.ttf",
    "/usr/share/fonts/truetype/tlwg/TlwgTypo.ttf",
    "/System/Library/Fonts/Thonburi.ttc"
]
TTF_PATH = next((p for p in TTF_CANDIDATES if os.path.exists(p)), "C:/Windows/Fonts/tahomabd.ttf")

def read_base_msg_cg():
    """Extract clean original MSG_CG.BIN, read existing file, or create clean 74,880B container"""
    if os.path.exists(MSG_CG_PATH):
        with open(MSG_CG_PATH, 'rb') as f:
            data = bytearray(f.read())
            if len(data) == 74880:
                return data
    if os.path.exists(BIN_PATH):
        with open(BIN_PATH, 'rb') as f:
            f.seek(148515 * 2352)
            sectors = (74880 + 2047) // 2048
            data = bytearray()
            for _ in range(sectors):
                sec = f.read(2352)
                data.extend(sec[24:24+2048])
        return bytearray(data[:74880])
    print("[!] Running in standalone mode: creating clean 74,880-byte font container.")
    return bytearray(74880)

def render_cluster_layer(cluster, font, dx=0, dy=0):
    """Render a single glyph layer with mark-to-mark elevation and reinforced legibility"""
    upper_vowels = 'ิีึืั็'
    tone_marks = '่้๊๋์'
    
    has_upper = any(c in cluster for c in upper_vowels)
    has_tone = any(c in cluster for c in tone_marks)
    
    bbox = font.getbbox(cluster)
    tw = bbox[2] - bbox[0]
    
    if cluster in 'เแโใไ':
        ox = 16 - tw - 2 - bbox[0]
    elif cluster in 'ะาำ':
        ox = 2 - bbox[0]
    elif cluster in '0123456789!?.:,();"/-+=':
        ox = (16 - tw) // 2 - bbox[0]
    else:
        if tw >= 14:
            ox = max(0, 15 - tw) - bbox[0]
        else:
            ox = max(1, (16 - tw) // 2) - bbox[0]
            
    oy = 1
    
    img = Image.new('L', (16, 16), 0)
    draw = ImageDraw.Draw(img)
    
    if has_upper and has_tone:
        base_upper = ''.join(c for c in cluster if c not in tone_marks)
        tones = ''.join(c for c in cluster if c in tone_marks)
        base = cluster[0]
        
        # Base consonant + upper vowel sits at row 2
        draw.text((ox + dx, 2 + dy), base_upper, font=font, fill=255)
        
        # Tone mark elevated to row -1 so it stacks cleanly above upper vowel
        img_tone = Image.new('L', (16, 16), 0)
        draw_tone = ImageDraw.Draw(img_tone)
        draw_tone.text((ox + dx, -1 + dy), base + tones, font=font, fill=255)
        if '่' in tones:
            # Reinforce mai ek by 1 pixel for crisp 2px stroke width
            draw_tone.text((ox + dx + 1, -1 + dy), base + tones, font=font, fill=255)
        
        for y in range(4):
            for x in range(16):
                val = img_tone.getpixel((x, y))
                if val > 50:
                    img.putpixel((x, y), max(img.getpixel((x, y)), val))
    else:
        draw.text((ox + dx, oy + dy), cluster, font=font, fill=255)
        if '่' in cluster:
            draw.text((ox + dx + 1, oy + dy), cluster, font=font, fill=255)
        
    return img

def render_cluster_16x16_4bpp(cluster, font):
    """
    Render Thai cluster to 16x16 with crisp white foreground + shadow
    Output: 128 bytes 4bpp PS1 format
    """
    img_fg = render_cluster_layer(cluster, font, 0, 0)
    
    # Shadow composite: right, down, right-down
    sh1 = render_cluster_layer(cluster, font, 1, 1)
    sh2 = render_cluster_layer(cluster, font, 1, 0)
    sh3 = render_cluster_layer(cluster, font, 0, 1)
    
    img_sh = Image.new("L", (16, 16), 0)
    for y in range(16):
        for x in range(16):
            v = max(sh1.getpixel((x, y)), sh2.getpixel((x, y)), sh3.getpixel((x, y)))
            img_sh.putpixel((x, y), v)
    
    # Convert to 128 bytes 4bpp PS1 format
    out = bytearray(128)
    for y in range(16):
        row_offset = y * 8
        for bx in range(8):
            fg0 = img_fg.getpixel((bx * 2, y))
            fg1 = img_fg.getpixel((bx * 2 + 1, y))
            sh0 = img_sh.getpixel((bx * 2, y))
            sh1 = img_sh.getpixel((bx * 2 + 1, y))
            
            p0 = 1 if fg0 > 100 else (14 if sh0 > 100 else 0)
            p1 = 1 if fg1 > 100 else (14 if sh1 > 100 else 0)
            
            # PS1 LoadImage: low nibble = left pixel, high nibble = right pixel
            out[row_offset + bx] = ((p1 & 0x0F) << 4) | (p0 & 0x0F)
            
    # For preview
    preview_tile = Image.new("L", (16, 16), 0)
    for y in range(16):
        for x in range(16):
            fg = img_fg.getpixel((x, y))
            sh = img_sh.getpixel((x, y))
            val = 255 if fg > 100 else (120 if sh > 100 else 0)
            preview_tile.putpixel((x, y), val)
            
    return bytes(out), preview_tile

def build_4bpp_thai_font():
    print("=" * 60)
    print(" Chou Mashin Eiyuuden Wataru - 4bpp Font Generator")
    print("=" * 60)

    # 1. Read clean original MSG_CG.BIN
    print("[*] Reading clean original MSG_CG.BIN from base ROM...")
    cg_data = read_base_msg_cg()
    print(f"[*] Base MSG_CG.BIN size: {len(cg_data)} bytes")

    # 2. Keep 0x0000..0x5300 (System font) untouched!
    font_start_offset = 0x5300
    available_bytes = len(cg_data) - font_start_offset
    max_glyphs = (available_bytes // 128) - 1 # Exactly 418 glyphs
    print(f"[*] Font starts at offset 0x{font_start_offset:04X} (RAM 0x80115300)")
    print(f"[*] Available dialogue glyph slots: {max_glyphs} glyphs ({max_glyphs * 128} bytes)")

    # 3. Compile prioritized Thai cluster list
    font = ImageFont.truetype(TTF_PATH, 12)
    clusters = get_prioritized_clusters(max_glyphs)
    print(f"[*] Total prioritized Thai clusters to generate: {len(clusters)}")

    # 4. Table mapping
    table = {
        " ": 0,
        "\n": 0x1000,
        "<WAIT>": 0x2000,
        "<END>": 0x3000,
    }

    # Clear Token 0 (space) to all 0s
    cg_data[font_start_offset : font_start_offset + 128] = b"\x00" * 128

    rendered_images = []

    for idx, cluster in enumerate(clusters):
        token_id = idx + 1
        glyph_offset = font_start_offset + token_id * 128
        
        glyph_128b, p_img = render_cluster_16x16_4bpp(cluster, font)
        cg_data[glyph_offset : glyph_offset + 128] = glyph_128b
        
        table[cluster] = token_id
        rendered_images.append((cluster, token_id, p_img))

    print(f"[+] Wrote {len(clusters)} Thai glyphs (128B each) into MSG_CG.BIN (0x{font_start_offset:05X} .. 0x{font_start_offset + (len(clusters)+1)*128:05X})")
    print(f"[+] Token 207 (0x00CF) is: {repr(clusters[206])} (offset 0x{font_start_offset + 207 * 128:04X})")
    assert table[":"] == 207, f"Token 207 mismatch: expected 207 for ':', got {table.get(':')}"

    # Verify exact size: MUST NOT EXCEED 74,880 BYTES!
    assert len(cg_data) == 74880, f"MSG_CG.BIN size mismatch: expected 74880, got {len(cg_data)}"

    # 5. Save modified MSG_CG.BIN
    with open(MSG_CG_PATH, "wb") as f:
        f.write(cg_data)
    print(f"[+] Saved modified MSG_CG.BIN: {MSG_CG_PATH} (Exact {len(cg_data)} bytes)")

    # 6. Save thai_table.json
    with open(TABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved Thai table: {TABLE_PATH} ({len(table)} mappings)")

    # 7. Generate preview grid
    cols = 20
    rows = (len(rendered_images) + cols - 1) // cols
    preview = Image.new("L", (cols * 16, rows * 16), 0)
    for idx, (cl, tok, p_img) in enumerate(rendered_images):
        gx = (idx % cols) * 16
        gy = (idx // cols) * 16
        preview.paste(p_img, (gx, gy))

    preview_3x = preview.resize((preview.width * 2, preview.height * 2), Image.NEAREST)
    preview_3x.save(PREVIEW_PATH)
    print(f"[+] Saved font preview grid: {PREVIEW_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    build_4bpp_thai_font()
