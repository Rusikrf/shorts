#!/usr/bin/env python3
"""QA for finished shorts: transcript vs script, caption sync vs speech, black/frozen frames,
loudness, a 1-fps contact sheet for visual review."""
import json, os, re, subprocess, sys
import numpy as np, librosa
from faster_whisper import WhisperModel

HT = "/home/claude/work/hooktest"; OUT = f"{HT}/out"
S = json.load(open(f"{HT}/scripts.json"))
WM = WhisperModel("base.en", device="cpu", compute_type="int8")
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())

def srt(path):
    items = []
    for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
        l = b.splitlines(); a, c = l[1].split(" --> ")
        f = lambda x: int(x[:2]) * 3600 + int(x[3:5]) * 60 + float(x[6:].replace(",", "."))
        items.append((f(a), f(c), " ".join(l[2:])))
    return items

def wer(ref, hyp):
    d = np.zeros((len(ref) + 1, len(hyp) + 1), int); d[:, 0] = range(len(ref) + 1); d[0, :] = range(len(hyp) + 1)
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + (ref[i-1] != hyp[j-1]))
    return d[-1, -1] / len(ref)

report = {}
for sid, s in S.items():
    mp4 = f"{OUT}/{sid}.mp4"
    wav = f"{OUT}/{sid}_qa.wav"   # decode the FINAL mp4's audio track, not the intermediate voice file
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    y, _ = librosa.load(wav, sr=16000); os.remove(wav)
    segs, _ = WM.transcribe(y, language="en", word_timestamps=True); segs = list(segs)
    words = [w for sg in segs for w in sg.words]
    heard = " ".join(sg.text.strip() for sg in segs)
    spoken_ref = " ".join(s.get("speech", {}).get(str(i), l) for i, l in enumerate(s["lines"]))
    r = [norm(w) for w in spoken_ref.split() if norm(w)]
    h = [norm(w.word) for w in words if norm(w.word)]
    # caption sync: for every caption whose first word Whisper also heard, compare start times
    caps = srt(f"{OUT}/{sid}.srt"); errs = []; wi = 0
    for a0, a1, txt in caps:
        first = norm(txt.split()[0])
        for k in range(wi, min(wi + 12, len(words))):
            if norm(words[k].word) == first:
                errs.append(abs(a0 - words[k].start)); wi = k + 1; break
    probe = lambda args: subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4] + args + ["-f", "null", "-"],
                                        capture_output=True, text=True).stderr
    black = re.findall(r"black_start:\S+ black_end:\S+", probe(["-vf", "blackdetect=d=0.2:pix_th=0.08", "-an"]))
    frozen = re.findall(r"freeze_start: \S+", probe(["-vf", "freezedetect=n=-60dB:d=1.0", "-an"]))
    lufs = re.search(r"Input Integrated:\s+(\S+)", probe(["-af", "loudnorm=print_format=summary", "-vn"]))
    first_voice = words[0].start if words else None
    dims = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_name:format=duration",
                           "-of", "compact=p=0:nk=1", mp4], capture_output=True, text=True).stdout.split()
    report[sid] = {"file": dims, "first_word_at_s": round(first_voice, 2) if first_voice is not None else None,
                   "word_error_rate_vs_script": round(wer(r, h), 3), "heard": heard,
                   "caption_sync_checked": len(errs), "caption_sync_median_ms": int(np.median(errs) * 1000) if errs else None,
                   "caption_sync_max_ms": int(max(errs) * 1000) if errs else None,
                   "black_segments": black, "frozen_segments": frozen,
                   "integrated_loudness_LUFS": lufs.group(1) if lufs else None}
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                    "fps=1,scale=216:-1,tile=8x5:padding=4", "-frames:v", "1", f"{OUT}/{sid}_sheet.jpg"])
json.dump(report, open(f"{OUT}/qa.json", "w"), indent=1)
print(json.dumps({k: {x: y for x, y in v.items() if x != "heard"} for k, v in report.items()}, indent=1))
