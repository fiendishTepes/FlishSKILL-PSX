#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chou Mashin Eiyuuden Wataru: Another Step (PS1)
CD-ROM Disc Repacker & CHD Builder Suite

Repacks modified MSG_CG.BIN (Thai Font) and R00.BIN (Opening + Shop Dialogues)
into a test PS1 disc image in 07_EMULATOR_TEST/ ready for DuckStation / emulator testing.
"""

import os
import shutil
import subprocess

BASE_DIR = r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru"
ORIG_BIN = os.path.join(BASE_DIR, "Chou Mashin Eiyuuden Wataru - Another Step (Japan).bin")
ORIG_CUE = os.path.join(BASE_DIR, "Chou Mashin Eiyuuden Wataru - Another Step (Japan).cue")

TEST_DIR = os.path.join(BASE_DIR, "07_EMULATOR_TEST")
TEST_BIN = os.path.join(TEST_DIR, "Wataru_Thai_Test.bin")
TEST_CUE = os.path.join(TEST_DIR, "Wataru_Thai_Test.cue")
TEST_CHD = os.path.join(TEST_DIR, "Wataru_Thai_Test.chd")

CHDMAN_PATH = os.path.join(BASE_DIR, "chdman.exe")

MSG_CG_PATH = os.path.join(BASE_DIR, "02_EXTRACTED", "FM16", "MSG_CG.BIN")
R00_PATH = os.path.join(BASE_DIR, "02_EXTRACTED", "FPRG", "R00.BIN")

# LBA locations on disc
INJECTIONS = [
    ("FM16/MSG_CG.BIN", MSG_CG_PATH, 148515, 37),
    ("FPRG/R00.BIN",    R00_PATH,    148660, 37),
]

def repack():
    print("=" * 65)
    print(" Chou Mashin Eiyuuden Wataru - PS1 Disc Repacker & Builder")
    print("=" * 65)

    os.makedirs(TEST_DIR, exist_ok=True)

    # 1. Copy base BIN to test directory
    print(f"[*] Copying base BIN image to test folder...")
    print(f"    Source: {ORIG_BIN}")
    print(f"    Target: {TEST_BIN}")
    shutil.copy2(ORIG_BIN, TEST_BIN)
    print(f"[+] Copy complete ({os.path.getsize(TEST_BIN) / 1024 / 1024:.2f} MB)")

    # 2. Inject modified sectors
    with open(TEST_BIN, "r+b") as f_bin:
        for name, file_path, lba, max_sectors in INJECTIONS:
            with open(file_path, "rb") as f_src:
                src_data = f_src.read()

            src_sectors = (len(src_data) + 2047) // 2048
            print(f"[*] Injecting {name} at LBA {lba} ({src_sectors} sectors, {len(src_data)} bytes)...")
            
            if src_sectors > max_sectors:
                raise ValueError(f"File {name} exceeds allocated sector count! ({src_sectors} > {max_sectors})")

            # Pad user data to full sectors
            padded_data = src_data.ljust(src_sectors * 2048, b"\x00")

            for s in range(src_sectors):
                sec_offset = (lba + s) * 2352
                f_bin.seek(sec_offset)
                sector = bytearray(f_bin.read(2352))

                # User data in Mode 2 Form 1 is bytes 24 .. 24+2048
                chunk = padded_data[s * 2048 : (s + 1) * 2048]
                sector[24 : 24 + 2048] = chunk

                f_bin.seek(sec_offset)
                f_bin.write(sector)

            print(f"  [+] Injected {name} ({src_sectors} sectors) successfully.")

    # 3. Create CUE file
    print(f"[*] Generating CUE sheet: {TEST_CUE}...")
    cue_content = f"""FILE "{os.path.basename(TEST_BIN)}" BINARY
  TRACK 01 MODE2/2352
    FLAGS DCP
    INDEX 01 00:00:00
"""
    with open(TEST_CUE, "w", encoding="utf-8") as f_cue:
        f_cue.write(cue_content)
    print(f"[+] Created CUE file: {os.path.basename(TEST_CUE)}")

    # 4. Build CHD using chdman.exe
    if os.path.exists(CHDMAN_PATH):
        print(f"[*] Compressing into CHD format with chdman...")
        cmd = [CHDMAN_PATH, "createcd", "-i", TEST_CUE, "-o", TEST_CHD, "-f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(TEST_CHD):
            chd_size_mb = os.path.getsize(TEST_CHD) / 1024 / 1024
            print(f"[+] CHD created successfully: {os.path.basename(TEST_CHD)} ({chd_size_mb:.2f} MB)")
        else:
            print(f"[!] Warning: chdman failed or returned code {res.returncode}")
            if res.stderr:
                print(f"    {res.stderr.strip()}")

    print("=" * 65)
    print(" BUILD SUCCESSFUL! Ready for Emulator Testing:")
    print(f"  🎮 BIN/CUE : {TEST_CUE}")
    if os.path.exists(TEST_CHD):
        print(f"  🎮 CHD     : {TEST_CHD}")
    print("=" * 65)

if __name__ == "__main__":
    repack()
