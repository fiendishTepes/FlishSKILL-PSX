import os
import re
import json

BASE_DIR = r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru"
R00_THAI_PATH = os.path.join(BASE_DIR, "04_SCRIPT_TOOLS", "thai_dialogs", "R00.json")

# Precomposed speaker tiles for exact-byte cutscene alignment
SPEAKER_TILES = ['โอ', 'บา', 'บะ', 'วา', 'ตา']

# Pure Thai vertical cluster regex:
# Consonant + [upper vowel + tone? | lower vowel + tone? | tone]
cluster_pattern = re.compile(
    r'^[ก-ฮ](?:[ิีึืั็][่้๊๋์]?|[ุู][่้๊๋]?|[่้๊๋์])'
)

def tokenize_thai_units(text):
    """
    Standard Thai tokenizer:
    - Pure individual letters for consonants, leading vowels, and trailing vowels.
    - Only true vertically-stacked marks are clustered with consonants.
    - No multi-letter horizontal syllables (no squishing!).
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
    - Uses precomposed 3-tile speaker tags for Obaba and Wataru in opening cutscenes
    - All other speaker names use standard individual characters
    """
    if spk == "โอบาบะ":
        return ["โอ", "บา", "บะ"]
    elif spk == "วาตารุ":
        return ["วา", "ตา", "รุ"]
    return tokenize_thai_units(spk)

def get_prioritized_clusters(max_count=418):
    clusters = [None] * max_count
    # Pin slot 206 (token 207 = 0x00CF) to ':'
    # In PS1 Wataru engine, speaker lines terminate with 0x00CF (colon) + 0x1000 (\n)
    clusters[206] = ':'
    assigned_set = set([':'])

    def add(c):
        if c in assigned_set or c in ('\n', ' ', '<WAIT>', '<END>'):
            return
        for idx in range(len(clusters)):
            if clusters[idx] is None:
                clusters[idx] = c
                assigned_set.add(c)
                return
        # If full, ignored

    # 1. Essential speaker tiles
    for st in SPEAKER_TILES:
        add(st)

    # 2. Extract from translated texts across opening cutscene, sections 1..3, and shops
    cutscene_texts = [
        "ฟื้นแล้วรึเนี่ย!?", "หา?", "เฮ้อ……", "อืม ดูท่า\nไม่มีแผลนะ", "โล่งอกไปที",
        "ค... ครับ\nขอบคุณครับ", "……แล้ว\nเจ้าชื่ออะไร?", "ที่นี่ที่ไหนครับ?",
        "เอ๊ะ?\nหมู่บ้านมอนจาไง", "แล้วชื่อเจ้าล่ะ?", "หมู่บ้านมอนจาเหรอ\nไม่เคยได้ยินเลย……",
        "อยู่ที่ไหนครับ?", "ชื่อเจ้าไงเล่า!", "ตอนเดินใกล้ๆ\nริวจินมารุน่ะ", "จู่ๆ แสงก็สว่างจ้า……",
        "ข้าถามชื่อเจ้าอยู่นะ!", "ตกใจหมดเลยครับ", "แล้วจากนั้นก็……", "โธ่เว้ยย!!", "เหวออ!!",
        "ถามว่า\nชื่ออะไรฟะ!", "ฮ... โฮมุระเบะ วาตารุ", "วาตารุสินะ?", "อ... อื้ม",
        "ตรงตามคำทำนายเป๊ะ", "คำทำนายเหรอ?", "ใช่แล้วล่ะ",
        
        # Section 1
        "ตำนานโบราณเล่าไว้ว่า", "เมื่อความมืดมาเยือน\nมังกรขาวจะนำพา", "ผู้กล้าวาตารุจะมา\nเพื่อกอบกู้โลกนี้",
        "ผู้กล้าเหรอ?", "ใช่แล้ว ผู้กล้า", "ใครเหรอ?", "ก็เจ้าไง", "ของอะไรครับ?", "ของโลกนี้ไง",
        "หา... จริงเหรอ!", "จงช่วยโลกใบนี้\nด้วยพลังริวจินมารุ", "………。 ", "นึกว่าหลุดเข้ามา\nในเกมซะอีกนะ",
        "(มีคนเดินมา)", "ขออนุญาตค่ะ\nท่านยายมีแขกเหรอ?", "ฮึๆ ผู้กล้าที่ร่าเริง\nมาถึงแล้วสินะคะ",
        "เอ๊ะ... เธอคือใครน่ะ?", "ยินดีที่ได้พบ\nท่านผู้กล้าค่ะ", "ฉันชื่อซาคุยะ\nเป็นมิโกะของที่นี่ค่ะ",

        # Section 2 & 3 (Sakuya & Aragoto)
        "ผม อิคซาเบะ\nวาตารุ ฝากตัวด้วยนะ!", "ทีตอนคุยกับข้า\nไม่เห็นตั้งใจฟังเลย",
        "ฮึๆ ท่านผู้กล้า\nร่าเริงดีจังนะคะ", "ก็ท่านยายน่ะ...", "หน้าตาน่ากลัวงั้นเรอะ!\nหน้าตาเนี่ยนะ!",
        "เอาล่ะท่านผู้กล้า\nเรื่องหน้าตาช่างมันเถอะค่ะ", "โซไคซังกับ\nโลกคามิเบะไคสินะครับ?",
        "ค่ะ ก่อนจะไปถึงคามิเบะไค...", "วารุมอนโด?", "วารุมอนโดก็คือ\nจอมปีศาจแห่งความมืดค่ะ",
        "ลองสวมชุดนี้ดูสิ", "ว้าว พอดีเป๊ะเลย!\nแถมเบาสบาย ขยับง่ายด้วย", "เหมาะมากเลยค่ะ",
        "งั้นด้วยชุดนี้\nพวกเราจะไปจัดการพวกมัน!", "ค่ะ อย่างที่เล่าให้ฟัง\nระหว่างมาที่นี่",
        "โอ้วๆ ดูเหมือนจะ\nใส่ได้พอดีสินะ", "ท่านยาย...", "อ๊ะ จริงด้วย...", "อ๊ะ จริงด้วยสิคะ",
        "อ๊ะ ใช่แล้วๆ\nเฮ้ เข้ามาได้แล้ว!", "หึ เรื่องดีต้องรีบทำ\nคิดได้เมื่อไหร่ก็เป็นฤกษ์ดี",
        "เจ้าไม่ใช่หัวหน้านะ\nเป็นแค่ว่าที่หัวหน้า", "วาตารุ จะปล่อยให้เจ้า\nไปโลกปีศาจคนเดียวไม่ได้",
        "ก็ตามนั้นแหละ\nฝากตัวด้วยนะ เจ้าหนู", "อื้ม ทางนี้ก็ขอฝากตัวนะ\nคุณลุงอาราโกโตะ!",
        "ล... ลุง... เรอะ", "ฝากตัวด้วยนะคะ\nคุณ... ลุง...", "อุ... อึก แม้แต่เธอด้วยเรอะ!",
        "ท่านวาตารุคะ...", "อื้ม!", "ฝากดูแลด้วยล่ะ\nอาราโกโตะ", "รับทราบแล้วครับ\nท่านโอบาบะ",
        "ท่านยาย พวกเราไปก่อนนะคะ"
    ]
    for ct in cutscene_texts:
        for u in tokenize_thai_units(ct):
            add(u)

    shop_texts = [
        "พนักงานร้าน", "ซาคุยะ", "โอบาบะ", "วาตารุ", "อาราโกโตะ",
        "ยินดีต้อนรับครับ!\n<WAIT>\nอ้าว ท่านผู้กล้าตามข่าวลือนี่นา\nเลือกดูสินค้าบนชั้นวางได้ตามสบายเลยครับ\n<WAIT>\nถ้านำมาที่เคาน์เตอร์\nเดี๋ยวผมจะคิดเงินให้นะครับ<END>",
        "เมื่อกดปุ่มวงกลมที่หน้าชั้นวาง\nคำอธิบายไอเทมจะปรากฏขึ้นค่ะ\n<WAIT>\nเลื่อนเคอร์เซอร์ขึ้นลง\nไปยังไอเทมที่ต้องการ\nแล้วกดปุ่มวงกลมนะคะ\n<WAIT>\nจากนั้นเลือกจำนวนที่ต้องการซื้อ\nแล้วกดปุ่มวงกลมเพื่อยืนยันค่ะ\n<WAIT>\nเมื่อเลือกเสร็จแล้ว\nให้เดินไปที่เคาน์เตอร์เพื่อชำระเงินนะคะ<END>",
        "ครับ เดี๋ยวผมจะอธิบายวิธีซื้อของให้นะ\n<WAIT>\nเมื่อเลือกไอเทมจากชั้นวางแล้ว\nให้นำมาที่เคาน์เตอร์แล้วคุยกับผมนะครับ\n<WAIT>\nกดปุ่มวงกลมเพื่อคุยได้เลย\n<WAIT>\nแล้วผมจะบอกยอดรวมทั้งหมด\nให้ท่านตัดสินใจว่าจะซื้อหรือไม่\n<WAIT>\nถ้าเปลี่ยนใจไม่ซื้อ หรือเงินไม่พอ\nให้นำไอเทมกลับไปวางที่เดิมนะครับ\n<WAIT>\nวิธีคืนไอเทม แค่ปรับจำนวนที่ชั้นวาง\nให้กลายเป็นศูนย์ก็เรียบร้อยครับ\n<WAIT>\nเข้าใจแล้วใช่ไหมครับ?<END>",
        "เดี๋ยวก่อนสิ ท่านผู้กล้าาา!\n<WAIT>\nถือไอเทมออกไปโดยไม่จ่ายเงิน\nไม่ได้นะคร้าบบบ!\n<WAIT>\nแต่ผมเชื่อว่าท่านผู้กล้า\nคงไม่ทำเรื่องแบบนั้นหรอกเนอะ...\n<WAIT>\nอ้อ ใช่แล้ว ร้านของเรา\nจะเปิดบริการตั้งแต่เมืองถัดไปนะครับ\n<WAIT>\nขอฝากเนื้อฝากตัวด้วยนะครับ!<END>"
    ]
    for st in shop_texts:
        for u in tokenize_thai_units(st):
            add(u)

    if os.path.exists(R00_THAI_PATH):
        with open(R00_THAI_PATH, 'r', encoding='utf-8') as f:
            r00 = json.load(f)
        for item in r00:
            th = item.get('thai', '')
            if th.strip():
                for u in tokenize_thai_units(th):
                    add(u)
                
    # 3. Punctuation & English
    puncts = ['!', '?', '.', ',', '-', ';', '(', ')', '"', '…', '/', '%', '+', '=', '？', '！', '…', 'ー', '、', '。']
    for p in puncts:
        add(p)

    # 4. Digits
    for d in range(10):
        add(str(d))

    # 5. Standalone vowels & marks
    standalone = ['ะ', 'า', 'ำ', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ๆ', 'ฯ', 'ั', '็', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', '่', '้', '๊', '๋', '์']
    for s in standalone:
        add(s)

    # 6. Common consonants
    consonants_common = [
        'ก', 'ข', 'ค', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ญ', 'ด', 'ต', 'ถ', 'ท', 'ธ',
        'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ'
    ]
    rare = ['ฃ', 'ฅ', 'ฆ', 'ฌ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ฤ', 'ฦ']
    for c in consonants_common + rare:
        add(c)

    # 7. Fill remaining slots with common upper, tone, lower combinations
    upper = ['ิ', 'ี', 'ึ', 'ื', 'ั', '็']
    tones = ['่', '้', '๊', '๋']
    lower = ['ุ', 'ู']

    for c in consonants_common:
        for u in upper: add(c + u)
        for t in tones: add(c + t)
        for l in lower: add(c + l)

    for c in consonants_common:
        for u in ['ิ', 'ี', 'ื', 'ั']:
            for t in ['่', '้']:
                add(c + u + t)
        for l in lower:
            for t in ['่', '้']:
                add(c + l + t)

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
    print("Sample first 25 clusters:", cl[:25])
