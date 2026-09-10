# 🔍 PS1 Script Reverse Engineering & Bytecode Guide

## 1. Sequential Stream vs Pointer Table Architectures
* **Sequential Stream**: Cutscene interpreters read opcodes and text continuously. Sections are bounded by `<WAIT>` (`0x2000`) and `<END>` (`0x3000`). Total byte length of each section must be preserved exactly using trailing zero padding.
* **Pointer Table**: Menus, shops, and NPC talk tables reference text blocks via 32-bit RAM pointers. These can be relocated to free RAM space.

## 2. The 0x0000 Opcode Hazard (Cascading Triangles Crash)
* In PS1 game engines, zero bytes (`0x0000`) in script event sections are often parsed as GPU polygon draw commands.
* If a cutscene block is truncated or padded with zeros in the middle of a command sequence, the GPU attempts to draw garbage primitives across the frame buffer.
* **Rule**: Always pad with `0x0000` immediately before the final `<END>` (`0x3000`) terminator, never mid-stream.
