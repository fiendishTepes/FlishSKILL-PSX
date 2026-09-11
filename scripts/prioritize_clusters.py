import os
import re
import json
from collections import Counter

BASE_DIR = r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru"
THAI_DIR = os.path.join(BASE_DIR, "04_SCRIPT_TOOLS", "thai_dialogs")

# High-frequency dual-character compound tiles for tight kerning and zero jagged spacing
# High-frequency dual-character compound tiles for tight kerning and zero jagged spacing
COMPOUND_TILES = [
    # 3-char specials with upper vowel + tone
    "เมื่", "เยื", "เรื่", "เพื่",
    # 3-char leading vowel + cons + tone
    "ได้", "ไม่", "แต่", "ให้", "แล้", "เจ้",
    # Consonant + า
    "มา", "ขา", "พา", "วา", "ตา", "รา", "กา", "นา", "หา", "อา", "สา", "ยา",
    # Consonant + ะ
    "นะ", "จะ", "คะ", "ระ", "ละ", "อะ", "ตะ",
    # Consonant + ำ
    "นำ", "ทำ", "คำ",
    # Leading Vowel + Consonant (plain)
    "ไป", "ใน", "ไม", "แต", "ได", "ให", "เป", "แล", "เห", "เม", "เพ", "เร", "เล", "เอ", "เด", "โต", "โก", "ไร", "เน", "เก", "เจ", "เข",
    # Speaker / common pairs
    "โอ", "บา", "บะ", "ซา", "ยะ", "รุ", "คุ"
]
COMPOUND_TILES = sorted(list(set(COMPOUND_TILES)), key=lambda x: len(x), reverse=True)

# Pure Thai vertical cluster regex:
# Consonant + [upper vowel + tone? | lower vowel + tone? | tone]
cluster_pattern = re.compile(
    r'^[ก-ฮ](?:[ิีึืั็][่้๊๋์]?|[ุู][่้๊๋]?|[่้๊๋์])'
)
MARKS = set('่้๊๋์ิีึืั็ุู')

def tokenize_thai_units(text):
    """
    Standard Thai tokenizer with compound tile support:
    - Precomposed 2-character syllables are tokenized as single units.
    - Vertically-stacked marks are clustered with consonants.
    - Fallback single characters for everything else.
    """
    units = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("<WAIT>", i):
            units.append("<WAIT>")
            i += 6
            continue
        if text.startswith("<END>", i):
            units.append("<END>")
            i += 5
            continue
        if text.startswith("\n", i):
            units.append("\n")
            i += 1
            continue
        if text[i] == ' ':
            units.append(' ')
            i += 1
            continue

        matched_c = False
        for c in COMPOUND_TILES:
            if text.startswith(c, i):
                next_pos = i + len(c)
                if next_pos < n and text[next_pos] in MARKS:
                    # Do not steal consonant or vowel if followed by tone mark / upper/lower mark!
                    continue
                units.append(c)
                i += len(c)
                matched_c = True
                break
        if matched_c:
            continue

        m = cluster_pattern.match(text[i:])
        if m:
            units.append(m.group(0))
            i += len(m.group(0))
            continue
        units.append(text[i])
        i += 1
    return units

def tokenize_speaker(spk):
    """
    Speaker name tokenizer:
    - Uses precomposed 3-tile speaker tags for Obaba, Wataru, and Sakuya
    - All other speaker names use standard individual characters
    """
    if spk == "โอบาบะ":
        return ["โอ", "บา", "บะ"]
    elif spk == "วาตารุ":
        return ["วา", "ตา", "รุ"]
    elif spk == "ซาคุยะ":
        return ["ซา", "คุ", "ยะ"]
    return tokenize_thai_units(spk)

def get_prioritized_clusters(max_count=418):
    clusters = [None] * max_count
    # Pin slot 206 (token 207 = 0x00CF) to ':'
    # In PS1 Wataru engine, speaker lines terminate with 0x00CF (colon) + 0x1000 (\n)
    clusters[206] = ':'
    assigned_set = set([':'])

    def add(c):
        if c in assigned_set or c in ('\n', ' ', '<WAIT>', '<END>'):
            return True
        for idx in range(len(clusters)):
            if clusters[idx] is None:
                clusters[idx] = c
                assigned_set.add(c)
                return True
        return False # Full

    # 1. Standard Punctuation & Digits (guaranteed)
    puncts = ['!', '?', '.', ',', '-', '(', ')', '"', '…', '%', '+', '=']
    for p in puncts: add(p)
    for d in range(10): add(str(d))

    # 2. Standalone vowels & tone marks (guaranteed for fallback decomposition)
    standalone = ['ะ', 'า', 'ำ', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ๆ', 'ฯ', 'ั', '็', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', '่', '้', '๊', '๋', '์']
    for s in standalone: add(s)

    # 3. All Consonants (guaranteed for fallback decomposition)
    consonants_common = [
        'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด',
        'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ฤ', 'ล', 'ฦ', 'ว', 'ศ',
        'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ'
    ]
    for c in consonants_common: add(c)

    # 4. Add all compound tiles
    for ct in COMPOUND_TILES:
        add(ct)

    # 5. Extract frequency of all units across ALL 14 room translation files
    counts = Counter()
    for fname in sorted(os.listdir(THAI_DIR)):
        if not fname.endswith(".json"): continue
        p = os.path.join(THAI_DIR, fname)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data:
            spk = e.get("speaker_th", "")
            for s in tokenize_speaker(spk):
                counts[s] += 1
            txt = e.get("thai", "")
            for u in tokenize_thai_units(txt):
                if u not in ('\n', ' ', '<WAIT>', '<END>'):
                    counts[u] += 1

    # 6. Add remaining vertical clusters by frequency order until 418 slots full
    for c, freq in counts.most_common():
        add(c)

    # Fill any remaining None with space
    for idx in range(len(clusters)):
        if clusters[idx] is None:
            clusters[idx] = ' '

    print(f"[*] Total prioritized clusters compiled: {len(clusters)} (cap: {max_count})")
    assert clusters[206] == ':', "CRITICAL ERROR: Token 207 (slot 206) must be ':'"
    return clusters

if __name__ == "__main__":
    cl = get_prioritized_clusters()
    print("Slot 207 (index 206):", repr(cl[206]))
    print(f"Total non-empty clusters: {sum(1 for c in cl if c != ' ')}")
