#!/usr/bin/env python3
"""Christmas text-story Shorts: Piper voice + word captions + procedural snowy bokeh background.
Usage: build_xmas.py <id>   (X01 | X02)"""
import json, os, random, subprocess, sys, wave, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

STORIES = {
 "X01": dict(voice="en_US-lessac-high", hook="He said giving mugs\naway was WASTEFUL", palette=((70, 18, 22), (14, 40, 30)), lines=[
  "My father-in-law said giving away our old mugs was wasteful. So for Christmas... he got all of them.",
  "We had way too many mugs in our kitchen.",
  "So we decided to give the extras away.",
  "My father-in-law heard about it. And he did not approve.",
  "Giving them away, he said, was just too wasteful.",
  "Fine. If they were too good to give away... someone should have them.",
  "So my husband and I packed them up. Seventeen mugs. All used.",
  "My husband warned his siblings ahead of time.",
  "They all knew exactly how their dad was. And they all agreed it would be funny.",
  "Well... one of them said Christmas was not the time or place.",
  "We did it anyway.",
  "Christmas Day. The whole family in one room. He opens the box...",
  "Seventeen used mugs.",
  "Everyone in that room knew. Only he was surprised.",
  "He started making excuses. My husband answered him. And the conversation just... moved on.",
  "No fight. No drama. Just one man with seventeen more mugs than he can handle."]),
 "X02": dict(voice="en_US-ryan-high", hook="They ORDERED us to buy\nexpensive gifts", palette=((16, 30, 62), (70, 16, 28)), lines=[
  "My siblings ordered us to buy their kids expensive Christmas gifts. So we did. Just... not the kind they expected.",
  "My partner and I are careful with money.",
  "And somehow, that convinced my siblings we were rich.",
  "So this year, they basically ordered us to buy their kids expensive presents.",
  "Being responsible with money had turned us into the family bank.",
  "That felt unfair. So we complied. Our way.",
  "Play dough.", "Kinetic sand.", "Slime.", "Water balloons.", "And Nerf guns.",
  "Every single gift the kids would love... and every parent would dread cleaning up.",
  "They wanted us to spend on their kids. We did.",
  "And honestly? This might be our new family Christmas tradition."]),
}
sid = sys.argv[1]; S = STORIES[sid]
W, H, FPS = 1080, 1920, 30
OUT = f"/home/claude/xmas/{sid}"; os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
if not os.path.exists(FONT):
    FONT = [l.split(":")[0] for l in subprocess.run(["fc-list"], capture_output=True, text=True).stdout.splitlines() if "Montserrat" in l and "Italic" not in l][0]

# 1) voice, line by line, with measured durations
GAP = 0.28; t = 0.0; timeline = []; pcm = b""; rate = None
for i, line in enumerate(S["lines"]):
    f = f"{OUT}/l{i:02d}.wav"
    subprocess.run(["python3", "-m", "piper", "-m", f"/tmp/piper/{S['voice']}.onnx", "--length-scale", "0.92", "-f", f],
                   input=line.replace("...", ","), text=True, check=True, capture_output=True)
    with wave.open(f) as w:
        rate = w.getframerate(); fr = w.readframes(w.getnframes()); sw = w.getsampwidth()
    dur = len(fr) / (rate * sw)
    timeline.append((line, t, t + dur)); pcm += fr; t += dur
    gap = GAP + (0.25 if line.endswith("...") or i == 0 else 0)
    pcm += b"\x00" * int(gap * rate) * sw; t += gap
total = t + 0.6; pcm += b"\x00" * int(0.6 * rate) * sw
with wave.open(f"{OUT}/voice.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(sw); w.setframerate(rate); w.writeframes(pcm)

# 2) word-group captions (ASS), timing proportional to characters
def ass_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
ev = []
for line, s, e in timeline:
    words = line.replace("...", "…").split()
    groups, cur = [], []
    for wd in words:
        cur.append(wd)
        if len(cur) == 3 or wd[-1] in ".,?!…":
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    weights = [sum(len(w) + 1 for w in g) for g in groups]; tw = sum(weights); x = s
    for g, wgt in zip(groups, weights):
        d = (e - s) * wgt / tw
        txt = " ".join(g).upper()
        ev.append(f"Dialogue: 0,{ass_time(x)},{ass_time(x + d)},Cap,,0,0,0,,{{\\fad(40,0)\\t(0,90,\\fscx108\\fscy108)\\t(90,160,\\fscx100\\fscy100)}}{txt}")
        x += d
fam = "Montserrat"
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{fam},112,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,1,0,0,0,100,100,0,0,1,8,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev).replace("Cap,,0,0,0,,{", "Cap,,0,0,0,,{\\pos(540,1080)") + "\n"
open(f"{OUT}/caps.ass", "w").write(ass)

# 3) background: warm two-tone gradient + blurred bokeh (static), then animated snow overlay
random.seed(sid)
c1, c2 = S["palette"]
bg = Image.new("RGB", (W, H))
px = bg.load()
for y in range(H):
    k = y / H
    col = tuple(int(c1[j] * (1 - k) + c2[j] * k) for j in range(3))
    for x in range(W): px[x, y] = col
bok = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bok)
for _ in range(38):
    r = random.randint(30, 110); x = random.randint(-50, W + 50); y = random.randint(-50, H + 50)
    col = random.choice([(255, 196, 110), (255, 120, 90), (140, 220, 160), (255, 235, 190)])
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (random.randint(35, 80),))
bok = bok.filter(ImageFilter.GaussianBlur(18))
bg = Image.alpha_composite(bg.convert("RGBA"), bok)
# darken centre band for caption contrast
band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
bd.rectangle([0, 820, W, 1340], fill=(0, 0, 0, 90)); band = band.filter(ImageFilter.GaussianBlur(60))
bg = Image.alpha_composite(bg, band).convert("RGB"); bg.save(f"{OUT}/bg.png")

# hook card (first ~2.6 s)
card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
fnt = ImageFont.truetype(FONT, 84)
try: fnt.set_variation_by_axes([850])
except Exception: pass
lines = S["hook"].split("\n"); lh = 110; y0 = 470 - lh * len(lines) // 2
boxw = max(cd.textlength(l, font=fnt) for l in lines) + 90
cd.rounded_rectangle([(W - boxw) / 2, y0 - 45, (W + boxw) / 2, y0 + lh * len(lines) + 25], radius=36, fill=(255, 255, 255, 240))
for i, l in enumerate(lines):
    cd.text((W / 2, y0 + i * lh + 40), l, font=fnt, fill=(150, 20, 30, 255), anchor="mm")
card.save(f"{OUT}/card.png")

# snow loop: 4 s of falling flakes rendered as alpha frames
SN = f"{OUT}/snow"; os.makedirs(SN, exist_ok=True)
flakes = [(random.uniform(0, W), random.uniform(0, H), random.uniform(2, 7), random.uniform(80, 260), random.uniform(0, 6.28)) for _ in range(140)]
LOOP = 4 * FPS
for f in range(LOOP):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); tt = f / FPS
    for x, y, r, v, ph in flakes:
        yy = (y + v * tt * (H / (v * 4)) * (v / 170)) % H  # each flake wraps within the loop
        yy = (y + (H * round(v / 170 + 0.5)) * tt / 4) % H
        xx = x + 18 * math.sin(ph + tt * 2 * math.pi / 4)
        dd.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 255, 255, 200))
    im.save(f"{SN}/{f:03d}.png")

# 4) render
fc = (f"[0:v]scale={W}:{H},zoompan=z='1.0+0.06*on/{int(total*FPS)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(total*FPS)}:s={W}x{H}:fps={FPS}[b];"
      f"[1:v]format=rgba[s];[b][s]overlay=0:0:shortest=0[bs];"
      f"[2:v]format=rgba,fade=t=out:st=2.3:d=0.4:alpha=1[c];[bs][c]overlay=0:0:enable='lte(t,2.8)',ass={OUT}/caps.ass,"
      f"fade=t=in:st=0:d=0.25,fade=t=out:st={total-0.4:.2f}:d=0.4[v]")
out = f"/home/claude/xmas/{sid}_xmas.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f"{OUT}/bg.png",
                "-stream_loop", "-1", "-framerate", str(FPS), "-i", f"{SN}/%03d.png",
                "-loop", "1", "-i", f"{OUT}/card.png", "-i", f"{OUT}/voice.wav",
                "-filter_complex", fc, "-map", "[v]", "-map", "3:a", "-t", f"{total:.2f}",
                "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total-0.4:.2f}:d=0.4",
                "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
json.dump({"total": total, "lines": [[l, round(s, 2), round(e, 2)] for l, s, e in timeline]}, open(f"{OUT}/timeline.json", "w"), indent=1)
print(out, round(total, 1))
