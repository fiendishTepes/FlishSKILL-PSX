import os
import sys
import argparse
import gzip
import hashlib
import struct
import json

def sha1_hex(data):
    return hashlib.sha1(data).hexdigest()

def sha256_digest(data):
    return hashlib.sha256(data).digest()

def mc_rom_key(rom_bytes):
    n = len(rom_bytes)
    M = 1048576
    if n <= 4 * M:
        data = rom_bytes
    else:
        mid = n // 2
        data = rom_bytes[:M] + rom_bytes[mid:mid+M] + rom_bytes[n-M:]
    tag = f"MCTH-webpatch-v1|{n}|".encode("utf-8")
    return sha256_digest(tag + data)

def mc_xor_keystream(data, key):
    out = bytearray(len(data))
    for off in range(0, len(data), 32):
        ctr = off // 32
        blk = key + struct.pack(">I", ctr)
        ks = sha256_digest(blk)
        n = min(32, len(data) - off)
        for i in range(n):
            out[off + i] = data[off + i] ^ ks[i]
    return bytes(out)

def apply_ips(rom_bytes, ips_bytes):
    if len(ips_bytes) < 8 or ips_bytes[:5] != b"PATCH":
        raise ValueError("Invalid IPS patch format (header mismatch)")
    
    # Calculate output length
    out = bytearray(rom_bytes)
    off = 5
    truncate_len = -1
    
    while off < len(ips_bytes):
        if ips_bytes[off:off+3] == b"EOF":
            off += 3
            if off + 3 == len(ips_bytes):
                truncate_len = (ips_bytes[off] << 16) | (ips_bytes[off+1] << 8) | ips_bytes[off+2]
            break
        
        target_offset = (ips_bytes[off] << 16) | (ips_bytes[off+1] << 8) | ips_bytes[off+2]
        size = (ips_bytes[off+3] << 8) | ips_bytes[off+4]
        off += 5
        
        if size == 0:  # RLE
            rle_count = (ips_bytes[off] << 8) | ips_bytes[off+1]
            val = ips_bytes[off+2]
            off += 3
            if target_offset + rle_count > len(out):
                out.extend(b"\x00" * (target_offset + rle_count - len(out)))
            for j in range(rle_count):
                out[target_offset + j] = val
        else:
            chunk = ips_bytes[off:off+size]
            off += size
            if target_offset + size > len(out):
                out.extend(b"\x00" * (target_offset + size - len(out)))
            out[target_offset:target_offset+size] = chunk
            
    if truncate_len >= 0:
        out = out[:truncate_len]
    return bytes(out)

def apply_bps(src_bytes, patch_bytes):
    # Standard BPS patch applier
    if len(patch_bytes) < 19 or patch_bytes[:4] != b"BPS1":
        raise ValueError("Invalid BPS patch format")
    
    off = 4
    def read_varint():
        nonlocal off
        res = 0
        shift = 1
        while True:
            b = patch_bytes[off]
            off += 1
            res += (b & 0x7f) * shift
            if b & 0x80:
                break
            shift <<= 7
            res += shift
        return res

    src_size = read_varint()
    dst_size = read_varint()
    meta_size = read_varint()
    off += meta_size  # skip metadata

    dst = bytearray(dst_size)
    out_off = 0
    src_rel_off = 0
    dst_rel_off = 0

    while off < len(patch_bytes) - 12:
        data = read_varint()
        action = data & 3
        length = (data >> 2) + 1

        if action == 0:  # SourceRead
            dst[out_off:out_off+length] = src_bytes[out_off:out_off+length]
            out_off += length
        elif action == 1:  # TargetRead
            dst[out_off:out_off+length] = patch_bytes[off:off+length]
            off += length
            out_off += length
        elif action == 2:  # SourceCopy
            d = read_varint()
            src_rel_off += -(d >> 1) if (d & 1) else (d >> 1)
            dst[out_off:out_off+length] = src_bytes[src_rel_off:src_rel_off+length]
            src_rel_off += length
            out_off += length
        elif action == 3:  # TargetCopy
            d = read_varint()
            dst_rel_off += -(d >> 1) if (d & 1) else (d >> 1)
            for _ in range(length):
                dst[out_off] = dst[dst_rel_off]
                out_off += 1
                dst_rel_off += 1

    return bytes(dst)

def apply_ppf(src_bytes, ppf_bytes):
    if len(ppf_bytes) < 56 or ppf_bytes[:5] != b"PPF30":
        raise ValueError("Invalid PPF3 patch format")
    
    # PPF3 spec
    image_type = ppf_bytes[5]  # 0=bin, 1=gi, 2=all
    block_check = ppf_bytes[6] # 0=off, 1=on
    undo_data = ppf_bytes[7]   # 0=no, 1=yes
    
    out = bytearray(src_bytes)
    off = 56 # header size
    
    while off < len(ppf_bytes):
        # 8 bytes offset, 1 byte count
        if off + 9 > len(ppf_bytes):
            break
        target_off = struct.unpack("<Q", ppf_bytes[off:off+8])[0]
        count = ppf_bytes[off+8]
        off += 9
        
        chunk = ppf_bytes[off:off+count]
        off += count
        
        if undo_data == 1:
            off += count # skip undo
            
        if target_off + count > len(out):
            out.extend(b"\x00" * (target_off + count - len(out)))
        out[target_off:target_off+count] = chunk

    return bytes(out)

def patch_game(patch_path, input_rom_path, output_path=None):
    with open(input_rom_path, "rb") as f:
        rom_data = f.read()

    with open(patch_path, "rb") as f:
        patch_raw = f.read()

    print(f"Original ROM size: {len(rom_data):,} bytes (SHA1: {sha1_hex(rom_data)})")

    # If locked
    if ".locked" in patch_path or not patch_raw.startswith(b"\x1f\x8b"):
        key = mc_rom_key(rom_data)
        decrypted_gz = mc_xor_keystream(patch_raw, key)
    else:
        decrypted_gz = patch_raw

    try:
        patch_decompressed = gzip.decompress(decrypted_gz)
    except Exception as e:
        raise ValueError(f"Failed to decompress patch. Please ensure your base ROM is the exact correct version! ({e})")

    if patch_decompressed.startswith(b"PATCH"):
        print("Detected patch format: IPS")
        out_rom = apply_ips(rom_data, patch_decompressed)
    elif patch_decompressed.startswith(b"BPS1"):
        print("Detected patch format: BPS")
        out_rom = apply_bps(rom_data, patch_decompressed)
    elif patch_decompressed.startswith(b"PPF30"):
        print("Detected patch format: PPF 3.0")
        out_rom = apply_ppf(rom_data, patch_decompressed)
    else:
        raise ValueError("Unknown patch format")

    if not output_path:
        stem, ext = os.path.splitext(input_rom_path)
        output_path = f"{stem}_Thai{ext}"

    with open(output_path, "wb") as f:
        f.write(out_rom)

    print(f"✅ Successfully patched! Output saved to: {output_path} ({len(out_rom):,} bytes)")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python patch_cli.py <patch_file> <input_rom_file> [output_file]")
        sys.exit(1)
    
    p_path = sys.argv[1]
    r_path = sys.argv[2]
    o_path = sys.argv[3] if len(sys.argv) > 3 else None
    patch_game(p_path, r_path, o_path)
