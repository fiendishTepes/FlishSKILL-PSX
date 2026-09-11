import os
import sys
import json
from PIL import Image, ImageDraw

BASE_DIR = r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru"
FONT_DIR = os.path.join(BASE_DIR, "03_FONT_ENGINE")
UNIVERSAL_DIR = r"D:\mod-thai\Retro_Trans_Studio\Universal_Font_Engine"
MSG_CG_PATH = os.path.join(BASE_DIR, "02_EXTRACTED", "FM16", "MSG_CG.BIN")
CNF_MSG_PATH = os.path.join(BASE_DIR, "02_EXTRACTED", "OUT", "CNF_MSG.BIN")
TABLE_PATH = os.path.join(FONT_DIR, "thai_table.json")
PREVIEW_PATH = os.path.join(FONT_DIR, "wataru_retro_font_preview.png")
DIALOGUE_PREVIEW_PATH = os.path.join(FONT_DIR, "wataru_aligned_dialogue_preview.png")
BIN_PATH = os.path.join(BASE_DIR, "Chou Mashin Eiyuuden Wataru - Another Step (Japan).bin")

RETRO_PNG = os.path.join(UNIVERSAL_DIR, "retro_thai_16x16.png")
UNIVERSAL_TBL_PATH = os.path.join(UNIVERSAL_DIR, "universal_thai_table.json")

sys.path.append(FONT_DIR)
from prioritize_clusters import get_prioritized_clusters, COMPOUND_TILES

def read_base_msg_cg():
    """Extract clean original MSG_CG.BIN from base BIN"""
    with open(BIN_PATH, 'rb') as f:
        f.seek(148515 * 2352)
        sectors = (74880 + 2047) // 2048
        data = bytearray()
        for _ in range(sectors):
            sec = f.read(2352)
            data.extend(sec[24:24+2048])
    return bytearray(data[:74880])

def read_base_cnf_msg():
    """Extract clean original CNF_MSG.BIN from base BIN (LBA 34834, 49 sectors = 98688 bytes)"""
    with open(BIN_PATH, 'rb') as f:
        f.seek(34834 * 2352)
        sectors = (98688 + 2047) // 2048
        data = bytearray()
        for _ in range(sectors):
            sec = f.read(2352)
            data.extend(sec[24:24+2048])
    return bytearray(data[:98688])

class RetroFontBuilder:
    def __init__(self):
        self.img = Image.open(RETRO_PNG).convert("L")
        with open(UNIVERSAL_TBL_PATH, "r", encoding="utf-8") as f:
            self.tbl = json.load(f)
        self.items = list(self.tbl.items())
        self.char_to_idx = {k: i for i, (k, v) in enumerate(self.items)}

    def get_raw_tile(self, ch):
        if ch not in self.char_to_idx:
            raise KeyError(f"Character {repr(ch)} not in universal table")
        idx = self.char_to_idx[ch]
        gx = (idx % 16) * 16
        gy = (idx // 16) * 16 + 1
        t = self.img.crop((gx, gy, gx + 16, gy + 16))
        # Extend truncated stems on leading vowels เ and แ
        if ch == 'เ':
            t = t.copy()
            for y in range(3, 8):
                t.putpixel((6, y), 255); t.putpixel((7, y), 255)
        elif ch == 'แ':
            t = t.copy()
            for y in range(3, 8):
                t.putpixel((5, y), 255); t.putpixel((6, y), 255); t.putpixel((9, y), 255)
        return t

    def create_compound_tile(self, cluster):
        if cluster in ("เมื่", "เรื่", "เพื่"):
            cons = cluster[1]
            raw1 = self.get_raw_tile('เ')
            raw2 = self.get_perfect_tile(cons + 'ื่')
            res = Image.new('L', (16, 16), 0)
            res.paste(raw1.crop((4, 2, 9, 16)), (1, 0))
            res.paste(raw2.crop((2, 0, 14, 16)), (6, 0))
            res.putpixel((12, 0), 255); res.putpixel((12, 1), 255)
            return res
        if cluster == "เยื":
            raw1 = self.get_raw_tile('เ')
            raw2 = self.get_perfect_tile('ยื')
            res = Image.new('L', (16, 16), 0)
            res.paste(raw1.crop((4, 2, 9, 16)), (1, 0))
            res.paste(raw2.crop((2, 0, 14, 16)), (6, 0))
            return res
        if len(cluster) == 3 and cluster[0] in 'เแโใไ' and cluster[2] in '่้๊๋์':
            leading_v, cons, tone = cluster[0], cluster[1], cluster[2]
            raw_v = self.get_raw_tile(leading_v)
            raw_ct = self.get_perfect_tile(cons + tone)
            res = Image.new('L', (16, 16), 0)
            res.paste(raw_v.crop((3, 1, 10, 16)), (1, 0))
            res.paste(raw_ct.crop((2, 0, 14, 16)), (6, 0))
            return res
        if cluster == "โอ":
            t1 = self.get_raw_tile('โ'); t2 = self.get_raw_tile('อ')
            res = Image.new('L', (16, 16), 0)
            res.paste(t1.crop((4, 3, 11, 15)), (1, 1))
            res.paste(t2.crop((5, 8, 11, 16)), (8, 6))
            return res

        c1, c2 = cluster[0], cluster[1]
        raw1 = self.get_raw_tile(c1)
        res = Image.new('L', (16, 16), 0)

        if c1 in 'เแโใไ':
            raw2 = self.get_raw_tile(c2)
            res.paste(raw1.crop((3, 1, 10, 16)), (1, 0))
            res.paste(raw2.crop((3, 7, 11, 16)), (8, 6))
        elif c2 == 'ะ':
            raw2 = self.get_raw_tile(c2)
            res.paste(raw1.crop((3, 7, 11, 16)), (1, 6))
            res.paste(raw2.crop((4, 7, 12, 16)), (9, 6))
        elif c2 == 'า':
            raw2 = self.get_raw_tile(c2)
            res.paste(raw1.crop((3, 7, 11, 16)), (1, 6))
            res.paste(raw2.crop((4, 7, 11, 16)), (9, 6))
        elif c2 == 'ำ':
            raw_aa = self.get_raw_tile('า')
            res.paste(raw1.crop((3, 7, 11, 16)), (1, 5))
            res.paste(raw_aa.crop((4, 8, 11, 16)), (9, 6))
            for x in (7, 8):
                res.putpixel((x, 2), 255); res.putpixel((x, 4), 255)
            res.putpixel((6, 3), 255); res.putpixel((9, 3), 255)
        else:
            raw2 = self.get_raw_tile(c2)
            res.paste(raw1.crop((3, 7, 10, 16)), (1, 6))
            res.paste(raw2.crop((4, 7, 11, 16)), (8, 6))
        return res

    def get_perfect_tile(self, cluster, bold=False):
        upper_vowels = 'ิีึืั็'
        tone_marks = '่้๊๋์'
        has_upper = any(c in cluster for c in upper_vowels)
        has_tone = any(c in cluster for c in tone_marks)

        # 1. Compound tiles (dual-syllable & special combinations)
        if cluster in COMPOUND_TILES and cluster not in ("รุ", "คุ"):
            t = self.create_compound_tile(cluster)

        # 2. Punctuation
        elif cluster == ':':
            t = Image.new('L', (16, 16), 0)
            for y in (5, 6, 10, 11):
                for x in (6, 7): t.putpixel((x, y), 255)
        elif cluster == ';':
            t = Image.new('L', (16, 16), 0)
            for y in (5, 6, 10, 11):
                for x in (6, 7): t.putpixel((x, y), 255)
            t.putpixel((6, 12), 255); t.putpixel((5, 13), 255)
        elif cluster == '"':
            t = Image.new('L', (16, 16), 0)
            for y in (3, 4):
                for x in (5, 6, 9, 10): t.putpixel((x, y), 255)
            t.putpixel((5, 5), 255); t.putpixel((9, 5), 255)
        elif cluster == '。':
            t = Image.new('L', (16, 16), 0)
            for y in (11, 12, 13):
                for x in (11, 12, 13): t.putpixel((x, y), 255)
            t.putpixel((12, 12), 0)
        elif cluster in ('？', '?'):
            t = self.get_raw_tile('?')
        elif cluster in ('！', '!'):
            t = self.get_raw_tile('!')
        elif cluster in ('ー', '-'):
            t = self.get_raw_tile('-')
        elif cluster in ('、', ','):
            t = self.get_raw_tile(',')

        # 3. Special clean ำ
        elif cluster == 'ำ':
            t = Image.new('L', (16, 16), 0)
            t.putpixel((2, 4), 255); t.putpixel((3, 4), 255)
            t.putpixel((1, 5), 255); t.putpixel((4, 5), 255)
            t.putpixel((2, 6), 255); t.putpixel((3, 6), 255)
            t_aa = self.get_raw_tile('า')
            crop_aa = t_aa.crop((4, 8, 11, 16))
            t.paste(crop_aa, (6, 6))

        # 4. Compound cluster (Upper Vowel + Tone Mark): Pure separation & Locked Baseline!
        elif has_upper and has_tone and len(cluster) >= 3:
            cons = cluster[0]
            u_vowel = [v for v in upper_vowels if v in cluster][0]
            tone = [tm for tm in tone_marks if tm in cluster][0]
            
            t_cons = self.get_raw_tile(cons)
            t = Image.new('L', (16, 16), 0)
            
            # Consonant body at rows 7..13 (locked bot=13!)
            for y in range(8, 16):
                for x in range(16):
                    val = t_cons.getpixel((x, y))
                    if val > 85:
                        t.putpixel((x - 1, y - 2), val)
                        
            if cons in 'ปฝฟฬ':
                for y in range(4, 8):
                    for x in range(9, 13):
                        v = t_cons.getpixel((x, y))
                        if v > 85: t.putpixel((x - 1, y - 2), v)

            # Upper vowel from 'ก' + vowel (rows 2..4)
            ref_v = 'ก' + u_vowel
            if ref_v in self.char_to_idx:
                t_v = self.get_raw_tile(ref_v)
                for src_y, dst_y in [(1, 2), (2, 3), (3, 4)]:
                    for x in range(16):
                        val = t_v.getpixel((x, src_y))
                        if val > 50:
                            nx = x - 1
                            if cons in 'ปฝฟฬ': nx -= 2
                            if 0 <= nx < 16: t.putpixel((nx, dst_y), val)

            # Tone mark at rows 0..1
            tx = 8
            if cons in 'ปฝฟฬ': tx = 6
            elif cons in 'ขชซ': tx = 9
            if tone == '่':
                t.putpixel((tx, 0), 255); t.putpixel((tx, 1), 255)
            elif tone == '้':
                t.putpixel((tx - 1, 0), 255); t.putpixel((tx + 1, 0), 255)
                t.putpixel((tx - 1, 1), 255); t.putpixel((tx, 1), 255); t.putpixel((tx + 1, 1), 255)
            elif tone == '๊':
                t.putpixel((tx - 1, 0), 255); t.putpixel((tx + 1, 0), 255)
                t.putpixel((tx - 1, 1), 255); t.putpixel((tx, 1), 255); t.putpixel((tx + 1, 1), 255)
            elif tone == '๋':
                t.putpixel((tx, 0), 255)
                t.putpixel((tx - 1, 1), 255); t.putpixel((tx, 1), 255); t.putpixel((tx + 1, 1), 255)
            elif tone == '์':
                t.putpixel((tx, 0), 255); t.putpixel((tx + 1, 0), 255)
                t.putpixel((tx - 1, 1), 255); t.putpixel((tx, 1), 255)

        # 5. Standalone marks
        elif cluster in ('ั', '็', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', '่', '้', '๊', '๋', '์'):
            standalone_map = {
                'ั': ('กั', 2, 6), '็': ('ก็', 0, 5), 'ิ': ('กิ', 1, 5),
                'ี': ('กี', 0, 4), 'ึ': ('กึ', 0, 4), 'ื': ('กื', 0, 4),
                'ุ': ('กุ', 14, 16), 'ู': ('กู', 14, 16), '่': ('ก่', 2, 5),
                '้': ('ก้', 1, 5), '๊': ('ก๊', 2, 5), '๋': ('ก๋', 1, 5), '์': ('ก์', 2, 5),
            }
            ref_char, y_start, y_end = standalone_map[cluster]
            ref_tile = self.get_raw_tile(ref_char)
            t = Image.new('L', (16, 16), 0)
            for y in range(y_start, y_end):
                for x in range(16): t.putpixel((x, y), ref_tile.getpixel((x, y)))

        # 6. Standard single characters & single-mark clusters
        else:
            raw = self.get_raw_tile(cluster) if cluster in self.char_to_idx else Image.new('L', (16, 16), 0)

            # Clean raw bleeding
            if not has_upper and not has_tone and cluster not in ('โ', 'ใ', 'ไ', 'ฟ', 'ฝ', 'ป', 'ฬ'):
                for y in range(3):
                    for x in range(16): raw.putpixel((x, y), 0)

            pts = [(x, y) for y in range(16) for x in range(16) if raw.getpixel((x, y)) > 85]
            if not pts:
                return Image.new('L', (16, 16), 0)

            bot_y = max(y for x, y in pts)
            left_x = min(x for x, y in pts)
            right_x = max(x for x, y in pts)

            # Strict baseline locking at row 13
            if any(c in cluster for c in 'ุูฎฏ'):
                target_bot = 15
            elif cluster in ('า', 'ะ', 'ๆ', 'ฯ'):
                target_bot = 13
            else:
                target_bot = 13
            dy = target_bot - bot_y

            # Edge-flush kerning:
            if cluster in ('เ',):
                dx = 12 - right_x
            elif cluster in ('แ',):
                dx = 13 - right_x
            elif cluster in ('โ', 'ใ', 'ไ'):
                dx = 12 - right_x
            elif cluster in ('า', 'ะ', 'ๆ', 'ฯ'):
                dx = 1 - left_x
            else:
                dx = 3 - left_x

            t = Image.new('L', (16, 16), 0)
            for y in range(16):
                for x in range(16):
                    val = raw.getpixel((x, y))
                    if val > 85:
                        nx = x + dx
                        ny = y + dy
                        if 0 <= nx < 16 and 0 <= ny < 16:
                            t.putpixel((nx, ny), 255)

        if bold:
            # 1px horizontal bolding only if requested
            b_tile = Image.new('L', (16, 16), 0)
            for y in range(16):
                for x in range(16):
                    if t.getpixel((x, y)) > 85:
                        b_tile.putpixel((x, y), 255)
                        if x + 1 < 16:
                            b_tile.putpixel((x + 1, y), 255)
            t = b_tile

        return t

    def convert_tile_to_4bpp(self, tile):
        fg_mask = Image.new('1', (16, 16), 0)
        for y in range(16):
            for x in range(16):
                if tile.getpixel((x, y)) > 85:
                    fg_mask.putpixel((x, y), 1)

        sh_mask = Image.new('1', (16, 16), 0)
        for y in range(16):
            for x in range(16):
                if fg_mask.getpixel((x, y)) == 0:
                    p_left = fg_mask.getpixel((x - 1, y)) if x > 0 else 0
                    p_up = fg_mask.getpixel((x, y - 1)) if y > 0 else 0
                    p_diag = fg_mask.getpixel((x - 1, y - 1)) if (x > 0 and y > 0) else 0
                    if p_left or p_up or p_diag:
                        sh_mask.putpixel((x, y), 1)

        out = bytearray(128)
        preview = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

        for y in range(16):
            row_offset = y * 8
            for bx in range(8):
                x0 = bx * 2; x1 = bx * 2 + 1
                p0 = 1 if fg_mask.getpixel((x0, y)) else (14 if sh_mask.getpixel((x0, y)) else 0)
                p1 = 1 if fg_mask.getpixel((x1, y)) else (14 if sh_mask.getpixel((x1, y)) else 0)

                out[row_offset + bx] = ((p1 & 0x0F) << 4) | (p0 & 0x0F)

                for x_p, p in [(x0, p0), (x1, p1)]:
                    if p == 1:
                        preview.putpixel((x_p, y), (255, 255, 255, 255))
                    elif p == 14:
                        preview.putpixel((x_p, y), (20, 20, 30, 240))

        return bytes(out), preview

def build_wataru_retro_font():
    print("=" * 68)
    print(" Chou Mashin Eiyuuden Wataru - Master RetroTH 4bpp Font Compiler")
    print(" Compiles: MSG_CG.BIN (Dialogue) & CNF_MSG.BIN (Menu/Config)")
    print("=" * 68)

    builder = RetroFontBuilder()
    cg_data = read_base_msg_cg()
    cnf_data = read_base_cnf_msg()

    font_start_offset = 0x5300
    available_bytes = len(cg_data) - font_start_offset
    max_glyphs = (available_bytes // 128) - 1 # 418 glyphs

    clusters = get_prioritized_clusters(max_glyphs)
    print(f"[*] Clusters to encode: {len(clusters)}")

    table = {
        " ": 0,
        "\n": 0x1000,
        "<WAIT>": 0x2000,
        "<END>": 0x3000,
    }

    # Clear Token 0 (space) in both font containers
    cg_data[font_start_offset : font_start_offset + 128] = b"\x00" * 128
    cnf_data[font_start_offset : font_start_offset + 128] = b"\x00" * 128

    rendered_images = []
    for idx, cluster in enumerate(clusters):
        token_id = idx + 1
        glyph_offset = font_start_offset + token_id * 128

        tile = builder.get_perfect_tile(cluster, bold=False)
        glyph_128b, p_img = builder.convert_tile_to_4bpp(tile)

        cg_data[glyph_offset : glyph_offset + 128] = glyph_128b
        if glyph_offset + 128 <= len(cnf_data):
            cnf_data[glyph_offset : glyph_offset + 128] = glyph_128b

        table[cluster] = token_id
        rendered_images.append((cluster, token_id, p_img))

    print(f"[+] Encoded {len(clusters)} balanced RetroTH glyphs into MSG_CG.BIN & CNF_MSG.BIN")
    print(f"[+] Verified Token 207 (0x00CF) = {repr(clusters[206])}")
    assert table[":"] == 207, f"Token 207 mismatch: {table.get(':')}"
    assert len(cg_data) == 74880, f"MSG_CG size error: {len(cg_data)} != 74880"
    assert len(cnf_data) == 98688, f"CNF_MSG size error: {len(cnf_data)} != 98688"

    # Save MSG_CG.BIN
    with open(MSG_CG_PATH, "wb") as f:
        f.write(cg_data)
    print(f"[+] Saved MSG_CG.BIN: {MSG_CG_PATH} ({len(cg_data)} bytes)")

    # Save CNF_MSG.BIN
    with open(CNF_MSG_PATH, "wb") as f:
        f.write(cnf_data)
    print(f"[+] Saved CNF_MSG.BIN: {CNF_MSG_PATH} ({len(cnf_data)} bytes)")

    # Save thai_table.json
    with open(TABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved thai_table.json: {TABLE_PATH}")

    # Generate full font preview
    cols = 20
    rows = (len(rendered_images) + cols - 1) // cols
    preview = Image.new("RGBA", (cols * 16, rows * 16), (20, 20, 20, 255))
    for idx, (cl, tok, p_img) in enumerate(rendered_images):
        gx = (idx % cols) * 16
        gy = (idx // cols) * 16
        preview.alpha_composite(p_img, (gx, gy))

    preview_2x = preview.resize((preview.width * 2, preview.height * 2), Image.NEAREST)
    preview_2x.save(PREVIEW_PATH)
    print(f"[+] Saved font grid preview: {PREVIEW_PATH}")

    # Generate Dialogue Preview
    render_dialogue_preview(table, rendered_images)

def render_dialogue_preview(table, rendered_images):
    tile_dict = {tok: img for cl, tok, img in rendered_images}
    tile_dict[0] = Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    dialogues = [
        ("คำทำนาย", "เมื่อความมืดมาเยือน\nมังกรขาวจะนำพา"),
        ("โอบาบะ", "เอาล่ะ ที่เจ้าต้องทำ\nคือไปช่วยโลกนี้ด้วยพลังริวจินมารุ"),
        ("วาตารุ", "ผม อิคซาเบะ วาตารุ ฝากตัวด้วยนะ!\nที่นี่คือที่ไหนเหรอครับ?")
    ]

    from prioritize_clusters import tokenize_thai_units, tokenize_speaker

    box_w = 480
    box_h = 76
    total_h = len(dialogues) * (box_h + 14)
    canvas = Image.new("RGBA", (box_w, total_h), (20, 24, 32, 255))

    for d_idx, (spk, text) in enumerate(dialogues):
        base_y = d_idx * (box_h + 14) + 6
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([6, base_y, box_w - 6, base_y + box_h], radius=6, fill=(16, 24, 48, 240), outline=(80, 100, 140, 255), width=2)

        cur_x = 18; cur_y = base_y + 8
        for st in tokenize_speaker(spk):
            tok = table.get(st, 0)
            if tok in tile_dict: canvas.alpha_composite(tile_dict[tok], (cur_x, cur_y))
            cur_x += 16
        tok_colon = table.get(':', 0)
        if tok_colon in tile_dict: canvas.alpha_composite(tile_dict[tok_colon], (cur_x, cur_y))
        cur_x += 24

        cur_x = 18; cur_y += 22
        for t in tokenize_thai_units(text):
            if t == '\n':
                cur_x = 18; cur_y += 22
                continue
            if t == ' ':
                continue
            tok = table.get(t, 0)
            if tok in tile_dict: canvas.alpha_composite(tile_dict[tok], (cur_x, cur_y))
            cur_x += 16

    canvas_2x = canvas.resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
    canvas_2x.save(DIALOGUE_PREVIEW_PATH)
    print(f"[+] Saved dialogue preview: {DIALOGUE_PREVIEW_PATH}")

if __name__ == "__main__":
    build_wataru_retro_font()
