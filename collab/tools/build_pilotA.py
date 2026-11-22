#!/usr/bin/env python3
"""Pilot A ("winning format"): full story ~2-2.5 min, story-card hook, one-word captions,
licensed satisfying footage with hard cuts, Kokoro voice. Output 1080x1920.
Usage: build_pilotA.py story.json outdir [voice]"""
import json, os, re, sys, subprocess, difflib, random
import numpy as np, soundfile as sf, librosa
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel

W = "/home/claude/work"
story = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); os.makedirs(OUT, exist_ok=True)
VOICE = sys.argv[3] if len(sys.argv) > 3 else "af_heart"
SPEED, PAUSE, TITLE_PAUSE, TAIL, SR, LEAD = 1.05, 0.22, 0.45, 0.9, 24000, 0.08
FONTB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONTM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
CLIPS = ["px_8478150", "px_5900012", "px_36504176", "px_11761089", "px_5799463", "px_30324202", "px_8478148",
         "px_7850416", "px_5900008", "px_6872072", "px_9363591", "px_37230000", "px_30288568", "px_5900019",
         "px_8478147", "px_35487051", "px_8242982", "px_35548150"]

K = Kokoro(f"{W}/voices/kokoro/kokoro-v1.0.onnx", f"{W}/voices/kokoro/voices-v1.0.bin")
WM = WhisperModel("small.en", device="cpu", compute_type="int8")
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())

def trim(a, thr=0.01):
    i = np.where(np.abs(a) > thr)[0]
    return a if not len(i) else a[max(0, i[0] - int(.02 * SR)): i[-1] + int(.06 * SR)]

# ---------- voice + word timings ----------
lines, speech = story["lines"], story.get("speech", {})
audio, t, words, LINE_T = [], 0.0, [], []   # words: (start, end, text, line)
title_end = None
for i, disp in enumerate(lines):
    a, _ = K.create(speech.get(str(i), disp), voice=VOICE, speed=SPEED, lang="en-us")
    a = trim(a.astype(np.float32)); dur = len(a) / SR
    segs, _ = WM.transcribe(librosa.resample(a, orig_sr=SR, target_sr=16000), language="en", word_timestamps=True)
    ww = [w for s in segs for w in s.words]
    dw = disp.split(); st, en = [None] * len(dw), [None] * len(dw)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(x) for x in dw], [norm(w.word) for w in ww], autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): st[i1 + k], en[i1 + k] = ww[j1 + k].start, ww[j1 + k].end
        elif op in ("replace", "delete"):
            s0 = ww[j1].start if j2 > j1 else (ww[j1 - 1].end if j1 else 0.0)
            s1 = ww[j2 - 1].end if j2 > j1 else (ww[j1].start if j1 < len(ww) else dur)
            wt = np.array([len(norm(dw[k])) + 1 for k in range(i1, i2)], float); cum = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
            for n, k in enumerate(range(i1, i2)): st[k], en[k] = s0 + cum[n] * (s1 - s0), s0 + cum[n + 1] * (s1 - s0)
    for k, w in enumerate(dw):
        words.append((t + max(0, st[k] - LEAD), t + max(0, en[k] - LEAD), w, i))
    LINE_T.append((i, t, t + dur))
    audio.append(a)
    gap = TITLE_PAUSE if i == 0 else PAUSE
    if i == 0: title_end = t + dur
    if i < len(lines) - 1:
        audio.append(np.zeros(int(gap * SR), np.float32)); t += dur + gap
    else:
        t += dur
voice_end, total = t, t + TAIL
json.dump({"lines": LINE_T, "words": words, "voice_end": voice_end, "total": total, "title_end": title_end},
          open(f"{OUT}/timeline.json", "w"))
wav = f"{OUT}/voice.wav"
sf.write(wav, np.concatenate(audio + [np.zeros(int(TAIL * SR), np.float32)]), SR)

# ---------- captions: one word (tiny words ride with the next) ----------
groups, cur = [], []
for w in words:
    if w[3] == 0:                       # the title line is shown on the card, not as captions
        continue
    cur.append(w)
    txt = " ".join(x[2] for x in cur)
    if len(norm(w[2])) > 3 or len(txt) >= 9 or re.search(r"[.,!?:]$", w[2]):
        groups.append(cur); cur = []
if cur: groups.append(cur)
keys = set(story.get("keywords", []))
def ts(s): return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
def ts_srt(s):
    ms = int(round(s * 1000)); return f"{ms//3600000:02d}:{ms%3600000//60000:02d}:{ms%60000//1000:02d},{ms%1000:03d}"
caps = []
for k, g in enumerate(groups):
    s0 = g[0][0] if not caps else max(g[0][0], caps[-1][1])
    nxt = groups[k + 1][0][0] if k + 1 < len(groups) else voice_end + 0.3
    e = nxt if nxt - g[-1][1] < 0.5 else g[-1][1] + 0.15
    caps.append((s0, max(e, s0 + 0.12), g))

ass = f"{OUT}/caps.ass"
with open(ass, "w") as f:
    f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: W,Poppins,132,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,11,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
    for s0, e, g in caps:
        out = []
        for w in g:
            u = w[2].upper().strip('"')
            out.append("{\\c&H00D7FF&}" + u + "{\\c&HFFFFFF&}" if (norm(w[2]) in keys or re.search(r"\d", w[2])) else u)
        f.write(f"Dialogue: 0,{ts(s0)},{ts(e)},W,,0,0,0,,{{\\pos(540,1010)\\fscx70\\fscy70\\t(0,70,\\fscx100\\fscy100)}}{' '.join(out)}\n")
with open(f"{OUT}/{story['id']}_A.srt", "w") as f:
    for n, (s0, e, g) in enumerate([(0, title_end, [(0, 0, story['card_title'])])] + caps, 1):
        f.write(f"{n}\n{ts_srt(s0)} --> {ts_srt(e)}\n{' '.join(x[2] for x in g)}\n\n")

# ---------- story card (our own design, no third-party branding) ----------
card = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
x0, y0, x1 = 70, 300, 1010
ft, fn, fs = ImageFont.truetype(FONTB, 58), ImageFont.truetype(FONTB, 40), ImageFont.truetype(FONTM, 30)
words_t, lines_t, line = story["card_title"].split(), [], ""
for w in words_t:
    test = (line + " " + w).strip()
    if d.textlength(test, font=ft) > (x1 - x0 - 80): lines_t.append(line); line = w
    else: line = test
lines_t.append(line)
h = 180 + len(lines_t) * 74 + 40
shadow = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(shadow).rounded_rectangle((x0 + 6, y0 + 12, x1 + 6, y0 + h + 12), 42, fill=(0, 0, 0, 120))
card = Image.alpha_composite(card, shadow.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(card)
d.rounded_rectangle((x0, y0, x1, y0 + h), 42, fill=(255, 255, 255, 255))
av = Image.open(f"{W}/brand/avatar_800.png").convert("RGBA").resize((96, 96)); m = Image.new("L", (96, 96), 0); ImageDraw.Draw(m).ellipse((0, 0, 95, 95), fill=255)
card.paste(av, (x0 + 40, y0 + 36), m)
d.text((x0 + 156, y0 + 40), "Storytelling Vibe", font=fn, fill=(20, 20, 20))
d.text((x0 + 156, y0 + 92), "true story  ·  retold", font=fs, fill=(120, 120, 120))
for n, l in enumerate(lines_t):
    d.text((x0 + 40, y0 + 160 + n * 74), l, font=ft, fill=(15, 15, 15))
card.save(f"{OUT}/card.png")

# ---------- background: licensed clips, hard cuts every ~6-9 s ----------
rnd = random.Random(story["id"]); CLIPS = rnd.sample(CLIPS, len(CLIPS)); segs, acc, n = [], 0.0, 0
while acc < total + 0.5:
    c = CLIPS[n % len(CLIPS)]; n += 1
    p = f"{W}/src/px/{c}.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    take = min(dur - 0.6, rnd.uniform(6.0, 9.0))
    if take < 3.5: continue
    o = f"{OUT}/seg_{n:02d}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.3", "-t", f"{take:.2f}", "-i", p, "-an",
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", o], check=True)
    segs.append(o); acc += take
open(f"{OUT}/bg.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
bg = f"{OUT}/bg.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{OUT}/bg.txt", "-c", "copy", bg], check=True)

out = f"{OUT}/{story['id']}_A.mp4"
fc = (f"[0:v]eq=brightness=-0.07:saturation=1.08[b];"
      f"[2:v]format=rgba,fade=t=out:st={title_end + 0.15:.2f}:d=0.35:alpha=1[c];"
      f"[b][c]overlay=0:0:enable='lte(t,{title_end + 0.6:.2f})',ass={ass},fade=t=out:st={total - 0.35:.2f}:d=0.35[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", bg, "-i", wav, "-loop", "1", "-t", f"{total:.2f}", "-i", f"{OUT}/card.png",
                "-filter_complex", fc, "-map", "[v]", "-map", "1:a", "-t", f"{total:.2f}",
                "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total - 0.35:.2f}:d=0.35",
                "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
for s in segs: os.remove(s)
print(json.dumps({"out": out, "duration": round(total, 2), "title_end": round(title_end, 2), "captions": len(caps), "clips": len(segs)}))
