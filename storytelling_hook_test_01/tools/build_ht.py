#!/usr/bin/env python3
"""Hook test shorts: Kokoro voice per line, Whisper-aligned phrase captions, SRT, 1080x1920.
Usage: build_ht.py [ID ...]   (default: all in scripts.json)"""
import json, os, re, sys, subprocess
import numpy as np, soundfile as sf, librosa
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel

W = "/home/claude/work"
HT = os.path.join(W, "hooktest")
OUT = os.path.join(HT, "out"); os.makedirs(OUT, exist_ok=True)
VOICE, SPEED = "am_puck", 1.12
PAUSE, HOOK_PAUSE, TAIL = 0.24, 0.40, 0.8
FONT = "Poppins"
SR = 24000
STOP = {"a", "an", "the", "my", "to", "of", "and", "in", "for", "at", "on", "i", "his", "her", "with",
        "from", "that", "it", "was", "be", "so", "but", "or", "me", "he", "she", "they", "their", "your"}

K = Kokoro(f"{W}/voices/kokoro/kokoro-v1.0.onnx", f"{W}/voices/kokoro/voices-v1.0.bin")
WM = WhisperModel("base.en", device="cpu", compute_type="int8")

def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())

def trim(a, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx): return a
    return a[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.06 * SR)]

def chunks(words):
    """Phrase-aware caption chunks. Split into clauses at punctuation first, then cut each clause
    into the fewest balanced pieces (<=4 words, <=24 chars) so no piece is a lone leftover word,
    and avoid a piece ending on a weak word like 'the' or 'my'."""
    clauses, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.,!?:;]$|\"$", w): clauses.append(cur); cur = []
    if cur: clauses.append(cur)
    out = []
    for cl in clauses:
        n = len(cl)
        for k in range(1, n + 1):
            size = n / k
            cuts = [round(size * m) for m in range(1, k)]
            # nudge cuts so a piece doesn't end on a weak word
            cuts = [c + 1 if (norm(words[cl[c - 1]]) in STOP and c + 1 < n and (c + 1) not in cuts) else c for c in cuts]
            bounds = [0] + cuts + [n]
            parts = [cl[bounds[j]:bounds[j + 1]] for j in range(k)]
            if all(p and len(p) <= 4 and len(" ".join(words[x] for x in p)) <= 24 for p in parts):
                out.extend(parts); break
        else:
            out.extend([[x] for x in cl])
    # glue a one-word clause tail (e.g. "it.") onto the previous piece of the same sentence if it fits
    merged = []
    for p in out:
        if merged and len(p) == 1 and not re.search(r"[.,!?:;]$", words[merged[-1][-1]]) and \
                len(" ".join(words[x] for x in merged[-1] + p)) <= 26 and len(merged[-1]) < 5:
            merged[-1] = merged[-1] + p
        else:
            merged.append(p)
    return merged

def two_lines(t):
    if len(t) <= 13: return t
    ws = t.split(); best, bd = t, 99
    for k in range(1, len(ws)):
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        d = abs(len(a) - len(b))
        if d < bd: best, bd = a + "\\N" + b, d
    return best

def ts_ass(s):
    return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
def ts_srt(s):
    ms = int(round(s * 1000)); return f"{ms//3600000:02d}:{ms%3600000//60000:02d}:{ms%60000//1000:02d},{ms%1000:03d}"

def build(sid, s):
    lines, speech = s["lines"], s.get("speech", {})
    keys = set(norm(k) for k in s.get("keywords", []))
    audio, t, caps, align_err = [], 0.0, [], []
    for i, disp in enumerate(lines):
        say = speech.get(str(i), disp)
        a, sr = K.create(say, voice=VOICE, speed=SPEED, lang="en-us")
        a = trim(a.astype(np.float32)); dur = len(a) / SR
        # word timings from Whisper on this line
        y16 = librosa.resample(a, orig_sr=SR, target_sr=16000)
        segs, _ = WM.transcribe(y16, language="en", word_timestamps=True)
        ww = [w for sg in segs for w in sg.words]
        dw = disp.split()
        # align caption words to the words Whisper heard; unmatched runs (e.g. "$3,000" spoken as
        # "three thousand dollars") take the time span of the matching unmatched speech run
        import difflib
        a_, b_ = [norm(w) for w in dw], [norm(w.word) for w in ww]
        starts, ends = [None] * len(dw), [None] * len(dw); mode = "whisper"
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a_, b_, autojunk=False).get_opcodes():
            if op == "equal":
                for k in range(i2 - i1):
                    starts[i1 + k], ends[i1 + k] = ww[j1 + k].start, ww[j1 + k].end
            elif op in ("replace", "delete"):
                mode = "mapped"
                s0 = ww[j1].start if j2 > j1 else (ww[j1 - 1].end if j1 > 0 else 0.0)
                s1 = ww[j2 - 1].end if j2 > j1 else (ww[j1].start if j1 < len(ww) else dur)
                wt = np.array([len(a_[k]) + 1 for k in range(i1, i2)], float)
                cum = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
                for n, k in enumerate(range(i1, i2)):
                    starts[k], ends[k] = s0 + cum[n] * (s1 - s0), s0 + cum[n + 1] * (s1 - s0)
        LEAD = 0.10  # show each phrase a hair before it is spoken
        starts = [max(0.0, x - LEAD) for x in starts]; ends = [max(0.0, x - LEAD) for x in ends]
        for c in chunks(dw):
            txt = " ".join(dw[j] for j in c)
            caps.append((t + starts[c[0]], t + ends[c[-1]], txt, [dw[j] for j in c]))
        align_err.append((i, mode))
        audio.append(a)
        gap = HOOK_PAUSE if i == 0 else PAUSE
        if i < len(lines) - 1:
            audio.append(np.zeros(int(gap * SR), np.float32)); t += dur + gap
        else:
            t += dur
    voice_end = t
    total = voice_end + TAIL
    wav = os.path.join(OUT, f"{sid}_voice.wav")
    sf.write(wav, np.concatenate(audio + [np.zeros(int(TAIL * SR), np.float32)]), SR)

    # make captions continuous (no flicker): each caption lasts until the next starts
    fixed = []
    for k, (a0, a1, txt, ws) in enumerate(caps):
        start = max(a0, fixed[-1][1]) if fixed else max(0.0, a0)
        nxt = caps[k + 1][0] if k + 1 < len(caps) else voice_end + 0.4
        end = nxt if nxt - a1 < 0.6 else a1 + 0.2   # hold until the next phrase, never overlap
        fixed.append((start, max(end, start + 0.25), txt, ws))

    # SRT
    with open(os.path.join(OUT, f"{sid}.srt"), "w", encoding="utf-8") as f:
        for n, (a0, a1, txt, _) in enumerate(fixed, 1):
            f.write(f"{n}\n{ts_srt(a0)} --> {ts_srt(a1)}\n{txt}\n\n")

    def styled(ws):
        out = []
        for w in ws:
            u = w.upper().replace("{", "(").replace("}", ")")
            out.append("{\\c&H00D7FF&}" + u + "{\\c&HFFFFFF&}" if (re.search(r"\d|\$", w) or norm(w) in keys) else u)
        return two_lines(" ".join(out))

    ass = os.path.join(OUT, f"{sid}.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},108,&H00FFFFFF,&H00FFFFFF,&H00000000,&H70000000,1,0,0,0,100,100,0,0,1,10,0,5,0,0,0,1
Style: Box,{FONT},108,&H00FFFFFF,&H00FFFFFF,&H80000000,&H80000000,1,0,0,0,100,100,0,0,3,22,0,5,0,0,0,1
Style: Hook,{FONT},100,&H00FFFFFF,&H00FFFFFF,&H001A1AD8,&H001A1AD8,1,0,0,0,100,100,1,0,3,22,0,8,70,70,290,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        f.write(f"Dialogue: 1,{ts_ass(0)},{ts_ass(2.8)},Hook,,0,0,0,,{{\\fad(0,200)}}{s['screen_text']}\n")
        for a0, a1, _, ws in fixed:
            plain = two_lines(" ".join(w.upper() for w in ws))
            # translucent box underneath (layer 0, text hidden) keeps captions readable over the moving character
            f.write(f"Dialogue: 0,{ts_ass(a0)},{ts_ass(a1)},Box,,0,0,0,,{{\\pos(525,880)\\1a&HFF&}}{plain}\n")
            f.write(f"Dialogue: 2,{ts_ass(a0)},{ts_ass(a1)},Cap,,0,0,0,,{{\\pos(525,880)}}{styled(ws)}\n")

    bg, start = s["bg"]
    vf = (f"scale=1166:2074,crop=1080:1920,eq=brightness=-0.04:saturation=1.05,ass={ass},"
          f"fade=t=out:st={total-0.3:.2f}:d=0.3")
    out = os.path.join(OUT, f"{sid}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-i", os.path.join(W, bg), "-i", wav,
                    "-t", f"{total:.2f}", "-map", "0:v", "-map", "1:a", "-vf", vf,
                    "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total-0.3:.2f}:d=0.3",
                    "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
    return {"id": sid, "duration": round(total, 2), "captions": len(fixed),
            "proportional_lines": [i for i, m in align_err if m != "whisper"]}

S = json.load(open(os.path.join(HT, "scripts.json")))
ids = sys.argv[1:] or list(S)
print(json.dumps([build(i, S[i]) for i in ids], indent=1))
