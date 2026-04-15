#!/usr/bin/env python3
"""
Tears of the Eternal — Sprite Generation Script
Runs the Pixelcut pipeline for all game sprites.
Pipeline ID: pipe_be110a4178ac4d5c9177b7241c6af3ac
"""
import json, time, urllib.request, urllib.error, os, sys

API_KEY = "sk_de20684a35154dddbef84aec2d9d6c04"
PIPE_ID = "pipe_be110a4178ac4d5c9177b7241c6af3ac"
BASE    = "https://api.developer.pixelcut.ai/v1"
OUT_DIR = r"C:\Users\goodl\sprites"
LOG     = r"C:\Users\goodl\sprite_gen.log"
os.makedirs(OUT_DIR, exist_ok=True)

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
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def get_node_ids():
    p = api("GET", f"/pipelines/{PIPE_ID}")
    nodes = {n["type"]: n["id"] for n in p.get("nodes", [])}
    return nodes

def set_model(model_id):
    p = api("GET", f"/pipelines/{PIPE_ID}")
    nodes = p.get("nodes", [])
    edges = p.get("edges", [])
    for n in nodes:
        if n["type"] == "generate-image":
            n.setdefault("settings", {})["imageModelId"] = model_id
    api("PUT", f"/pipelines/{PIPE_ID}", {"name": "Sprite Generator", "nodes": nodes, "edges": edges})

def generate(filename, prompt, model="nano-banana-pro"):
    log(f"Generating: {filename}")
    # Update pipeline text-input and model
    p = api("GET", f"/pipelines/{PIPE_ID}")
    nodes = p.get("nodes", [])
    edges = p.get("edges", [])
    input_node_id = None
    for n in nodes:
        if n["type"] == "text-input":
            n["settings"]["text"] = prompt
            input_node_id = n["id"]
        if n["type"] == "generate-image":
            n.setdefault("settings", {})["imageModelId"] = model
    api("PUT", f"/pipelines/{PIPE_ID}", {"name": "Sprite Generator", "nodes": nodes, "edges": edges})

    # Run pipeline
    run = api("POST", f"/pipelines/{PIPE_ID}/runs", {})
    job_id = run.get("job_id")
    if not job_id:
        log(f"  ERROR: no job_id — {run}")
        return None

    # Poll until done
    for _ in range(60):
        time.sleep(8)
        job = api("GET", f"/jobs/{job_id}")
        status = job.get("status")
        if status == "completed":
            break
        if status == "failed":
            log(f"  FAILED: {job.get('error')}")
            return None

    # Get asset URL
    gens = job.get("generations", [])
    if not gens:
        log(f"  ERROR: no generations")
        return None
    asset_id = gens[0].get("asset_id")
    media = api("GET", f"/media/{asset_id}")
    url = media.get("active_revision", {}).get("asset", {}).get("url", "")
    if not url:
        log(f"  ERROR: no URL for {asset_id}")
        return None

    # Download
    out_path = os.path.join(OUT_DIR, filename)
    urllib.request.urlretrieve(url, out_path)
    log(f"  Saved: {out_path}")
    return out_path

# ─── SPRITE LIST ─────────────────────────────────────────────────────────────
STYLE = "The Binding of Isaac game sprite style, dark fantasy roguelike, top-down view, transparent background, highly detailed"

SPRITES = [
    # (filename, prompt, model)

    # ── Boss (most detail, best model) ───────────────────────────────────────
    ("boss_moms_heart.png",
     f"Mom's Heart final boss, giant grotesque pulsating dark red flesh heart organ, angry glowing yellow eyes sunken into the flesh, dark purple veins crawling across it, menacing tentacle-like growths, screaming mouth splitting open, {STYLE}",
     "nano-banana-pro"),

    # ── Enemies (medium detail) ───────────────────────────────────────────────
    ("enemy_gaper.png",
     f"Gaper enemy creature, round oversized pale head, black hollow eyes, wide stitched grin, tiny withered body below, shambling posture, dried blood stains, {STYLE}",
     "nano-banana-pro"),

    ("enemy_fly.png",
     f"Fly enemy creature, small dark demonic fly insect with buzzing veiny wings, single glowing red eye, sharp mandibles, tiny dark body, {STYLE}",
     "nano-banana-pro"),

    ("enemy_spider.png",
     f"Spider enemy creature, purple veiny spider with eight spindly legs, cluster of small red eyes, round fleshy body, drops of venom, {STYLE}",
     "nano-banana-pro"),

    ("enemy_mushroom.png",
     f"Mushroom enemy creature, large green glowing mushroom with sad drooping face, small root feet, emits green spore clouds, {STYLE}",
     "nano-banana-pro"),

    ("enemy_horf.png",
     f"Horf enemy creature, small orange blob creature with a wide gaping mouth, stubby arms, shoots glowing projectiles, {STYLE}",
     "nano-banana-pro"),

    ("enemy_leech.png",
     f"Leech enemy creature, dark crimson slug leech with circular fanged sucker mouth, slimy glistening body, {STYLE}",
     "nano-banana-pro"),

    ("enemy_clotty.png",
     f"Clotty enemy creature, purple blood clot mass with angry asymmetrical eyes, lumpy pulsating body, splits apart when killed, {STYLE}",
     "nano-banana-pro"),

    ("enemy_knight.png",
     f"Knight enemy creature, grey armored undead skeleton knight, cracked helmet with hollow glowing eyes, shield and sword, impervious front, vulnerable rear, {STYLE}",
     "nano-banana-pro"),

    ("enemy_bomb_fly.png",
     f"Bomb Fly enemy creature, red demonic fly carrying a round black bomb with a lit fuse, wings buzzing, menacing, {STYLE}",
     "nano-banana-pro"),

    ("enemy_angel.png",
     f"Angel enemy creature, golden angelic figure with holy white wings and glowing halo, angelic robes, shoots holy golden tears at player, {STYLE}",
     "nano-banana-pro"),

    ("enemy_tumor.png",
     f"Tumor enemy creature, dark red grotesque fleshy tumor mass, angry sunken eyes, veins pulsating, stationary, shoots blood tears in 8 directions, {STYLE}",
     "nano-banana-pro"),

    # ── Items (colorful iconic designs) ───────────────────────────────────────
    ("item_sad_onion.png",
     "Sad Onion item icon, crying grey onion with large sad eyes and flowing tears, simple bold design, colorful game item icon, dark background, glowing",
     "flux-2-klein-9b"),

    ("item_inner_eye.png",
     "Inner Eye item icon, large mystical blue eye with three pupils, magical ethereal glow, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_spoon_bender.png",
     "Spoon Bender item icon, metallic bent silver spoon with purple psychic energy swirling around it, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_crickets_head.png",
     "Cricket's Head item icon, orange cricket insect severed head with big eyes, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_my_little_unicorn.png",
     "My Little Unicorn item icon, cute pink cartoon unicorn with rainbow mane, bright vibrant colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_the_wafer.png",
     "The Wafer item icon, round pale cream communion wafer with cross embossed, holy glow, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_brimstone.png",
     "Brimstone item icon, glowing red demon eye with fiery laser beams erupting, hellfire red and orange colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_moms_knife.png",
     "Mom's Knife item icon, large serrated kitchen knife with dried blood, pink and silver colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_polyphemus.png",
     "Polyphemus item icon, single giant cyclops eye with massive tear drop, dark blue and grey tones, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_sacred_heart.png",
     "Sacred Heart item icon, glowing red heart with golden crown of thorns, holy aura, deep red and gold colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_dead_cat.png",
     "Dead Cat item icon, black cat with X eyes and halo, cute but morbid, black and grey colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_whore_of_babylon.png",
     "Whore of Babylon item icon, dark purple demonic feminine silhouette with glowing evil eyes, purple and black colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_epic_fetus.png",
     "Epic Fetus item icon, floating baby fetus inside crosshair targeting reticle, mint green colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_ipecac.png",
     "Ipecac item icon, green medicine bottle with skull and crossbones, toxic green liquid, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_dr_fetus.png",
     "Dr Fetus item icon, fetus in top hat and monocle holding a bomb, grey and pink colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_holy_mantle.png",
     "Holy Mantle item icon, golden holy shield with cross emblem and divine light, gold and white colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_scapular.png",
     "Scapular item icon, brown religious scapular cord with cross medallion, golden holy glow, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_aries.png",
     "Aries item icon, red ram skull with curved horns, fiery aura, deep red colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_cancer.png",
     "Cancer item icon, orange crab zodiac symbol with glowing claws, warm orange colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_magic_mushroom.png",
     "Magic Mushroom item icon, glowing rainbow-colored mushroom with sparkles, vibrant multicolor, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_crickets_body.png",
     "Cricket's Body item icon, small cricket insect torso without head, green and brown, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_lump_of_coal.png",
     "Lump of Coal item icon, black shiny coal chunk with orange inner glow, dark black and ember orange, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_blood_of_martyr.png",
     "Blood of the Martyr item icon, red crucifix cross dripping with bright red blood, deep crimson colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_the_compass.png",
     "The Compass item icon, golden antique compass with glowing needle pointing, gold and blue colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_rock_bottom.png",
     "Rock Bottom item icon, grey rock with downward arrow and solid base, teal and grey colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_spirit_sword.png",
     "Spirit Sword item icon, glowing ethereal blue spirit sword with ghostly aura, cyan and white colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_trisagion.png",
     "Trisagion item icon, white glowing holy cross light beam, pure white and gold, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_incubus.png",
     "Incubus item icon, small purple demonic winged familiar floating, dark purple and red, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_twisted_pair.png",
     "Twisted Pair item icon, two glowing orange orbital familiar orbs circling each other, bright orange colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_void.png",
     "Void item icon, dark swirling black hole with purple accents absorbing light, dark and purple, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_thunder_thighs.png",
     "Thunder Thighs item icon, pair of large pink chunky legs with lightning bolt, pink and yellow, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_missing_page.png",
     "Missing Page item icon, torn black book page with dark aura and skull, black and dark purple, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_cake.png",
     "Cake item icon, pink birthday cake slice with candle and sprinkles, bright pink colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_tech_x.png",
     "Tech X item icon, glowing cyan laser ring beam ring charging with electricity, cyan and electric blue, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_guillotine.png",
     "Guillotine item icon, rotating severed head with tiny body orbiting it, grey and red, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_bone_tears.png",
     "Bone Tears item icon, white bouncing bone fragment tear projectile, white and cream colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_soul_jar.png",
     "Soul Jar item icon, glowing blue glass jar containing a small soul, cyan and white colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_beelzebuls_wing.png",
     "Beelzebul's Wing item icon, single dark demonic insect wing with veins, dark and iridescent, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_cursed_penny.png",
     "Cursed Penny item icon, dark purple glowing cursed coin with skull face, purple and gold colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_pluto.png",
     "Pluto item icon, tiny distant planet sphere with icy surface, light blue and white, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_glowing_hourglass.png",
     "Glowing Hourglass item icon, golden hourglass with glowing golden sand flowing, gold and amber colors, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_cracked_crown.png",
     "Cracked Crown item icon, golden crown with crack running through it, gold and bronze, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_inner_child.png",
     "Inner Child item icon, tiny crying baby version of the character, pink and pale, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_spirit_shackles.png",
     "Spirit Shackles item icon, glowing blue spectral shackle chains, cyan and ghost white, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_brain_worm.png",
     "Brain Worm item icon, pink brain with a worm crawling through it, pink and gross red, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_tainted_heart.png",
     "Tainted Heart item icon, dark purple corrupted heart with crack and curse mark, purple and dark red, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),

    ("item_redemption.png",
     "Redemption item icon, golden glowing cross with beams of light, radiant gold and white, simple bold design, colorful game item icon, dark background",
     "flux-2-klein-9b"),
]

log(f"Starting sprite generation — {len(SPRITES)} sprites to generate")
log(f"Output: {OUT_DIR}")

done, failed = [], []
for i, (filename, prompt, model) in enumerate(SPRITES):
    log(f"--- [{i+1}/{len(SPRITES)}] {filename} ---")
    result = generate(filename, prompt, model)
    if result:
        done.append(filename)
    else:
        failed.append(filename)

log(f"\n=== DONE === {len(done)} succeeded, {len(failed)} failed")
if failed:
    log("Failed: " + ", ".join(failed))
