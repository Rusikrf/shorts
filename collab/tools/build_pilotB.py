#!/usr/bin/env python3
"""Pilot B (illustrated): same voice/captions/card as Pilot A, background = ChatGPT illustrations
with slow camera moves, cut on the story beats. Usage: build_pilotB.py"""
import json, os, subprocess
W = "/home/claude/work/pilot01"; A = f"{W}/outA"; OUT = f"{W}/outB"; os.makedirs(OUT, exist_ok=True)
IMG = "/home/claude/shorts/collab/inbox/pilot01_images"
tl = json.load(open(f"{A}/timeline.json")); total = tl["total"]
# line index -> image (story beats)
MAP = {0: 4, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4, 10: 5, 11: 5, 12: 5, 13: 6, 14: 6, 15: 6, 16: 6,
       17: 2, 18: 5, 19: 6, 20: 6, 21: 6, 22: 6, 23: 7, 24: 7, 25: 1, 26: 8, 27: 4}
# merge consecutive lines that use the same image into one shot
shots = []
for i, s, e in tl["lines"]:
    img = MAP[i]
    if shots and shots[-1][0] == img: shots[-1][2] = e
    else: shots.append([img, s, e])
for k in range(len(shots)):                      # each shot runs until the next one starts
    shots[k][1] = 0.0 if k == 0 else shots[k][1]
    shots[k][2] = shots[k + 1][1] if k + 1 < len(shots) else total
MOVES = [  # (zoom expression, x expression, y expression) — slow, alternating
    ("1.0+0.10*on/{d}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("1.12-0.10*on/{d}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("1.10", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*0.65-(ih-ih/zoom)*0.3*on/{d}"),
    ("1.10", "(iw-iw/zoom)*(0.2+0.6*on/{d})", "ih/2-(ih/zoom/2)"),
]
segs = []
for n, (img, s, e) in enumerate(shots):
    dur = e - s; frames = max(2, round(dur * 30))
    z, x, y = [m.format(d=frames) for m in MOVES[n % len(MOVES)]]
    o = f"{OUT}/shot_{n:02d}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f"{IMG}/{img:02d}.png", "-t", f"{dur:.3f}",
                    "-vf", f"scale=2160:3840,zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s=1080x1920:fps=30,setsar=1",
                    "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", o], check=True)
    segs.append(o)
open(f"{OUT}/bg.txt", "w").write("".join(f"file '{p}'\n" for p in segs))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/bg.txt", "-c", "copy", f"{OUT}/bg.mp4"], check=True)
# captions lower (illustrations keep faces in the middle third)
ass = open(f"{A}/caps.ass").read().replace("\\pos(540,1010)", "\\pos(540,1365)")
open(f"{OUT}/caps.ass", "w").write(ass)
te = tl["title_end"]; out = f"{OUT}/P01_flight_B.mp4"
fc = (f"[2:v]format=rgba,fade=t=out:st={te + 0.15:.2f}:d=0.35:alpha=1[c];"
      f"[0:v][c]overlay=0:0:enable='lte(t,{te + 0.6:.2f})',ass={OUT}/caps.ass,fade=t=out:st={total - 0.35:.2f}:d=0.35[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/bg.mp4", "-i", f"{A}/voice.wav", "-loop", "1", "-t", f"{total:.2f}",
                "-i", f"{A}/card.png", "-filter_complex", fc, "-map", "[v]", "-map", "1:a", "-t", f"{total:.2f}",
                "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total - 0.35:.2f}:d=0.35",
                "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
for p in segs: os.remove(p)
print(json.dumps({"out": out, "shots": [(s[0], round(s[1], 1), round(s[2], 1)) for s in shots]}))
