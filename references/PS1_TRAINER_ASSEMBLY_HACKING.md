# ⚔️ PS1 MIPS R3000 Assembly Trainer & Cheat Injection Guide

This guide documents the reverse-engineering methodology for baking cheat codes, starting funds, and trainer routines directly into PlayStation 1 executables (`SLPS_01x.xx` / `SLUS_01x.xx`).

---

## 1. Locating New Game Initializers

When a player selects "New Game" on the title screen, the game executes an initialization function that sets up quest flags, character attributes, and inventory/gold.

### Reverse Engineering Workflow:
1. **Find GameShark/Action Replay Address**:
   - Locate the RAM address of the target variable (e.g. Gold at `0x8009C8B4`).
2. **Search for Immediate Offsets in MIPS Code**:
   - For `0x8009C8B4`:
     - Base register: `lui $at, 0x800A` (or `0x8009`)
     - Offset: `0xC8B4` (sign-extended `-0x374C`)
     - Instruction: `sw $zero, 0xC8B4($at)` (`0xAC20C8B4`)
3. **Trace the Caller Hierarchy**:
   - Search for `jal` instructions targeting the initialization routine to ensure it is called only during New Game / Reset, not inside every frame loop.

---

## 2. Surgical Instruction Replacement (Zero Side-Effects)

To inject starting values without altering binary size or displacing branch offsets:

### Example: Setting Starting Gold to 983,040 Gold (`0x000F0000`)
In `SLPS_013.68`:
* **Original Instructions (8 bytes)**:
  ```mips
  0x013118: 3C 01 80 0A   lui $at, 0x800A
  0x01311C: AC 20 C8 B4   sw $zero, 0xC8B4($at)   ; Gold = 0
  ```
* **Patched Instructions (8 bytes)**:
  ```mips
  0x013118: 0F 00 02 3C   lui $v0, 0x000F         ; $v0 = 0x000F0000 (983,040)
  0x01311C: B4 C8 22 AC   sw $v0, 0xC8B4($at)    ; Gold = 983,040
  ```

### Why this is 100% Safe:
* `$at` was already loaded with `0x800A` by the preceding instruction (`0x013110`), making the first `lui $at` redundant.
* `$v0` is overwritten by a subsequent instruction (`0x013128: li $v0, 1`), so reusing `$v0` introduces zero register pollution.
* Total byte length remains identical; all surrounding function pointers and jump tables remain valid.

---

## 3. Automated Injection into CD Disc Image

1. Extract `SLPS_013.68` from the base ISO.
2. Apply the binary patch using `scripts/patch_slps_gold_trainer.py`.
3. Re-inject `SLPS_013.68` at its exact LBA sector (e.g. LBA 24, 266 sectors) using `scripts/repack_iso.py`.
4. Compress to CHD using `chdman createcd`.
