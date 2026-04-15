#!/usr/bin/env python3
"""Retry failed sprites with content-safe prompts."""
import json, time, urllib.request, urllib.error, os

API_KEY = "sk_de20684a35154dddbef84aec2d9d6c04"
PIPE_ID = "pipe_be110a4178ac4d5c9177b7241c6af3ac"
BASE    = "https://api.developer.pixelcut.ai/v1"
OUT_DIR = r"C:\Users\goodl\sprites"

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
    log(f"Generating: {filename}")
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
        log(f"  ERROR: {run}"); return None
    for _ in range(60):
        time.sleep(8)
        job = api("GET", f"/jobs/{job_id}")
        status = job.get("status")
        if status == "completed": break
        if status == "failed":
            log(f"  FAILED: {job.get('error')}"); return None
    gens = job.get("generations", [])
    if not gens: log("  ERROR: no generations"); return None
    asset_id = gens[0].get("asset_id")
    media = api("GET", f"/media/{asset_id}")
    url = media.get("active_revision", {}).get("asset", {}).get("url", "")
    if not url: log(f"  ERROR: no URL"); return None
    out_path = os.path.join(OUT_DIR, filename)
    urllib.request.urlretrieve(url, out_path)
    log(f"  Saved: {out_path}")
    return out_path

RETRIES = [
    ("item_crickets_head.png",
     "Cricket insect head trophy item icon, stylized bug face with big eyes, orange and brown, dark background, game icon"),
    ("item_my_little_unicorn.png",
     "Small cute cartoon unicorn pony item icon, pink mane, rainbow colors, bright cheerful, dark background, game icon"),
    ("item_moms_knife.png",
     "Large serrated kitchen knife item icon, silver steel blade, worn handle, dark background, fantasy game icon"),
    ("item_whore_of_babylon.png",
     "Dark purple demonic power symbol item icon, mysterious glowing sigil, purple and violet, dark background, game icon"),
    ("item_dr_fetus.png",
     "Small figure wearing top hat and monocle item icon, holding a bomb, grey and white, dark background, game icon"),
    ("item_magic_mushroom.png",
     "Glowing rainbow fantasy mushroom item icon, sparkling aura, vibrant multicolor, dark background, game icon"),
    ("item_blood_of_martyr.png",
     "Sacred red crucifix cross item icon, crimson and gold holy glow, dark background, game icon"),
    ("item_guillotine.png",
     "Orbiting spinning head familiar item icon, circular halo motion, grey and gold, dark background, game icon"),
    ("item_brain_worm.png",
     "Pink brain with spiral worm pattern item icon, pink and red, dark background, game icon"),
]

log(f"Retrying {len(RETRIES)} failed sprites...")
done, failed = [], []
for filename, prompt in RETRIES:
    result = generate(filename, prompt)
    if result: done.append(filename)
    else: failed.append(filename)

log(f"Done: {len(done)} ok, {len(failed)} failed")
if failed: log("Still failed: " + ", ".join(failed))
