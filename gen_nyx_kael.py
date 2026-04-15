#!/usr/bin/env python3
"""Generate char_nyx.png and char_kael.png via Pixelcut pipeline, then remove backgrounds."""
import json, time, urllib.request, urllib.error, os

API_KEY = "sk_de20684a35154dddbef84aec2d9d6c04"
PIPE_ID = "pipe_be110a4178ac4d5c9177b7241c6af3ac"
BASE    = "https://api.developer.pixelcut.ai/v1"
OUT_DIR = r"C:\Users\goodl\sprites"

SPRITES = [
    ("char_nyx.png",
     "Nyx shadow witch character, young adult female, flowing dark violet and black magical robes, "
     "glowing purple arcane eyes, ornate staff with glowing purple crystal orb, gothic dark fantasy "
     "game character sprite, full body standing pose, detailed illustration, dark background"),
    ("char_kael.png",
     "Kael iron warden knight character, male warrior, heavy dark plate armor with glowing blue energy "
     "cracks and runes, cyberpunk-fantasy fusion, imposing stance, one arm has large energy cannon gauntlet, "
     "glowing blue visor, dark background, detailed game character sprite, full body"),
]

def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req  = urllib.request.Request(url, data=data, method=method,
           headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def generate(filename, prompt, model="flux-2-klein-9b"):
    log(f"--- Generating: {filename} ---")
    p = api("GET", f"/pipelines/{PIPE_ID}")
    nodes = p.get("nodes", [])
    edges = p.get("edges", [])
    for n in nodes:
        if n["type"] == "text-input":
            n["settings"]["text"] = prompt
        if n["type"] == "generate-image":
            n.setdefault("settings", {})["imageModelId"] = model
    api("PUT", f"/pipelines/{PIPE_ID}", {"name": "Sprite Generator", "nodes": nodes, "edges": edges})
    run = api("POST", f"/pipelines/{PIPE_ID}/runs", {})
    job_id = run.get("job_id")
    if not job_id:
        log(f"  ERROR starting run: {run}")
        return None
    log(f"  Job ID: {job_id} — polling...")
    for attempt in range(60):
        time.sleep(8)
        job = api("GET", f"/jobs/{job_id}")
        status = job.get("status")
        log(f"  [{attempt+1}/60] status={status}")
        if status == "completed":
            break
        if status == "failed":
            log(f"  FAILED: {job.get('error')}")
            return None
    else:
        log("  ERROR: timed out waiting for job")
        return None
    gens = job.get("generations", [])
    if not gens:
        log("  ERROR: no generations in completed job")
        return None
    asset_id = gens[0].get("asset_id")
    media = api("GET", f"/media/{asset_id}")
    url = media.get("active_revision", {}).get("asset", {}).get("url", "")
    if not url:
        log(f"  ERROR: no download URL in media response: {media}")
        return None
    out_path = os.path.join(OUT_DIR, filename)
    urllib.request.urlretrieve(url, out_path)
    log(f"  Saved: {out_path}")
    return out_path

# ── Generate sprites ──────────────────────────────────────────────────────────
generated = {}
for filename, prompt in SPRITES:
    result = generate(filename, prompt)
    generated[filename] = result

log("=== Generation results ===")
for fname, path in generated.items():
    if path:
        log(f"  OK  {fname} → {path}")
    else:
        log(f"  FAIL  {fname}")

# ── Background removal ────────────────────────────────────────────────────────
log("=== Running rembg on generated sprites ===")
from rembg import remove

rembg_results = {}
for fname, path in generated.items():
    if path is None:
        log(f"  SKIP {fname} (generation failed)")
        rembg_results[fname] = None
        continue
    try:
        t = time.time()
        with open(path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data)
        with open(path, 'wb') as f:
            f.write(output_data)
        elapsed = time.time() - t
        log(f"  OK  {fname} background removed ({elapsed:.1f}s)")
        rembg_results[fname] = path
    except Exception as e:
        log(f"  ERROR removing background from {fname}: {e}")
        rembg_results[fname] = None

log("=== Final summary ===")
for fname in [s[0] for s in SPRITES]:
    gen_ok  = generated.get(fname) is not None
    remb_ok = rembg_results.get(fname) is not None
    status  = "SUCCESS" if (gen_ok and remb_ok) else ("GEN_FAILED" if not gen_ok else "REMBG_FAILED")
    path    = generated.get(fname) or "N/A"
    log(f"  {fname}: {status}  path={path}")
