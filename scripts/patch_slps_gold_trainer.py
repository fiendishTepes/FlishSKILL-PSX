#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PS1 MIPS Assembly Trainer Injector: Starting Gold 983,040 Gold (0x000F0000)
Patches New Game initialization and Game Over reset routines in SLPS_013.68
"""

import os
import sys
import struct

def patch_gold(slps_path, gold_val=0x000F0000):
    if not os.path.exists(slps_path):
        print(f"[FAIL] Executable not found at {slps_path}")
        return False

    with open(slps_path, "rb") as f:
        data = bytearray(f.read())

    high_16 = (gold_val >> 16) & 0xFFFF
    # lui $v0, high_16 (0x3C02xxxx)
    # sw $v0, 0xC8B4($at) (0xAC22C8B4)
    patch_bytes = struct.pack("<II", 0x3C020000 | high_16, 0xAC22C8B4)

    # 1. New Game routine at file offset 0x013118 (RAM 0x8002A918)
    t1 = 0x013118
    orig1 = bytes(data[t1:t1+8])
    if orig1 == bytes([0x0A, 0x80, 0x01, 0x3C, 0xB4, 0xC8, 0x20, 0xAC]):
        data[t1:t1+8] = patch_bytes
        print(f"[+] Patched New Game starting gold at 0x{t1:06X} -> {gold_val:,} Gold")
    else:
        print(f"[*] Offset 0x{t1:06X} already patched or different version.")

    # 2. Reset / Clear routine at file offset 0x0175F4 (RAM 0x8002EDF4)
    t2 = 0x0175F4
    orig2 = bytes(data[t2:t2+8])
    if orig2 == bytes([0x0A, 0x80, 0x01, 0x3C, 0xB4, 0xC8, 0x20, 0xAC]):
        data[t2:t2+8] = patch_bytes
        print(f"[+] Patched Reset/Game Over gold at 0x{t2:06X} -> {gold_val:,} Gold")
    else:
        print(f"[*] Offset 0x{t2:06X} already patched or different version.")

    with open(slps_path, "wb") as f:
        f.write(data)

    print(f"[+] Finished patching {slps_path}")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"D:\mod-thai\Retro_Trans_Studio\PS1\Wataru\02_EXTRACTED\SLPS_013.68"
    patch_gold(path)
