#!/usr/bin/env python3
"""Illustrated Christmas Shorts: reuse voice/timeline/captions from build_xmas.py, background = ChatGPT images
with slow camera moves cut on the story beats. Usage: build_xmas_illustrated.py X01|X02"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sid = sys.argv[1]
SRC = f"/home/claude/xmas/{sid}"                       # voice.wav, timeline.json, caps.ass from build_xmas.py
IMG = f"/home/claude/shorts/collab/inbox/xmas_{sid}_images"
OUT = f"/home/claude/xmas/{sid}_ill"; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
MAPS = {  # voice line index -> image number (story beats)
 "X01": [7, 1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 7, 7, 8, 8],
 "X02": [6, 1, 2, 2, 2, 3, 4, 4, 4, 5, 5, 6, 7, 8],
}
HOOK = {"X01": "He said giving mugs\naway was WASTEFUL", "X02": "They ORDERED us to buy\nexpensive gifts"}[sid]
tl = json.load(open(f"{SRC}/timeline.json")); total = tl["total"]; MAP = MAPS[sid]
assert len(MAP) == len(tl["lines"]), (len(MAP), len(tl["lines"]))

shots = []
for i, (_, s, e) in enumerate(tl["lines"]):
    if shots and shots[-1][0] == MAP[i]: shots[-1][2] = e
    else: shots.append([MAP[i], s, e])
for k in range(len(shots)):
    shots[k][1] = 0.0 if k == 0 else shots[k][1]
    shots[k][2] = shots[k + 1][1] if k + 1 < len(shots) else total
MOVES = [("1.04+0.08*on/{d}", "iw/2-(iw/zoom/2)", "ih*0.42-(ih/zoom*0.42)"),
         ("1.12-0.08*on/{d}", "iw/2-(iw/zoom/2)", "ih*0.42-(ih/zoom*0.42)"),
         ("1.10", "(iw-iw/zoom)*(0.25+0.5*on/{d})", "ih*0.42-(ih/zoom*0.42)"),
         ("1.10", "(iw-iw/zoom)*(0.75-0.5*on/{d})", "ih*0.42-(ih/zoom*0.42)")]
segs = []
for n, (img, s, e) in enumerate(shots):
    dur = e - s; frames = max(2, round(dur * FPS))
    z, x, y = [m.format(d=frames) for m in MOVES[n % len(MOVES)]]
    o = f"{OUT}/shot_{n:02d}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f"{IMG}/{img:02d}.png", "-t", f"{dur:.3f}",
                    "-vf", f"scale=2160:3840,zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},setsar=1",
                    "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", o], check=True)
    segs.append(o)
open(f"{OUT}/bg.txt", "w").write("".join(f"file '{p}'\n" for p in segs))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/bg.txt", "-c", "copy", f"{OUT}/bg.mp4"], check=True)

# captions in the calm lower band, hook card in the top band
ass = open(f"{SRC}/caps.ass").read().replace("\\pos(540,1080)", "\\pos(540,1560)")
open(f"{OUT}/caps.ass", "w").write(ass)
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"
card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
fnt = ImageFont.truetype(FONT, 76)
try: fnt.set_variation_by_axes([850])
except Exception: pass
lines = HOOK.split("\n"); lh = 100; y0 = 150
boxw = max(cd.textlength(l, font=fnt) for l in lines) + 80
cd.rounded_rectangle([(W - boxw) / 2, y0 - 40, (W + boxw) / 2, y0 + lh * len(lines) + 20], radius=34, fill=(255, 255, 255, 242))
for i, l in enumerate(lines):
    cd.text((W / 2, y0 + i * lh + 38), l, font=fnt, fill=(150, 20, 30, 255), anchor="mm")
card.save(f"{OUT}/card.png")

out = f"/home/claude/xmas/{sid}_xmas_illustrated.mp4"
fc = (f"[2:v]format=rgba,fade=t=out:st=2.6:d=0.4:alpha=1[c];"
      f"[0:v][c]overlay=0:0:enable='lte(t,3.1)',ass={OUT}/caps.ass,fade=t=in:st=0:d=0.2,fade=t=out:st={total-0.4:.2f}:d=0.4[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/bg.mp4", "-i", f"{SRC}/voice.wav", "-loop", "1", "-t", f"{total:.2f}",
                "-i", f"{OUT}/card.png", "-filter_complex", fc, "-map", "[v]", "-map", "1:a", "-t", f"{total:.2f}",
                "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total-0.4:.2f}:d=0.4",
                "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
for p in segs: os.remove(p)
print(out, round(total, 1), [(s[0], round(s[1], 1)) for s in shots])
