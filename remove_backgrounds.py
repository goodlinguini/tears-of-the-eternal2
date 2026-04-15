#!/usr/bin/env python3
"""Remove backgrounds from all sprites using rembg (local, no API needed)."""
from rembg import remove
from PIL import Image
import os, time

SPRITES_DIR = r"C:\Users\goodl\sprites"

files = sorted(f for f in os.listdir(SPRITES_DIR) if f.endswith('.png'))
print(f"Processing {len(files)} sprites...")

done = 0
for fname in files:
    path = os.path.join(SPRITES_DIR, fname)
    t = time.time()
    with open(path, 'rb') as f:
        input_data = f.read()
    output_data = remove(input_data)
    with open(path, 'wb') as f:
        f.write(output_data)
    elapsed = time.time() - t
    done += 1
    print(f"[{done}/{len(files)}] {fname} ({elapsed:.1f}s)", flush=True)

print(f"\nDone — {done} sprites processed.")
