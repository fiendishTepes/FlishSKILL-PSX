#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Pre-Flight Safety Checker for PS1 Translation Builds
"""

import os
import sys

def check_file_size(path, target_size, name):
    if not os.path.exists(path):
        print(f"[FAIL] {name} not found at {path}")
        return False
    actual = os.path.getsize(path)
    if actual != target_size:
        print(f"[FAIL] {name} size mismatch: {actual} bytes (Expected: {target_size} bytes)")
        return False
    print(f"[PASS] {name} size exact: {actual} bytes")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print(" PS1 Thai Mod Pre-Flight Safety Verification")
    print("=" * 60)
    print("[+] Ready for automated verification in CI/CD pipeline.")
