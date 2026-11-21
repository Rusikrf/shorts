# QA report — storytelling_hook_test_01

## 1. What was wrong in the old shorts (checked S02 landlord — 110 views, and S01 office)
- **First voice line was backstory, not conflict.** S02 opens with “The paint started falling off my bathroom ceiling…” — the conflict (“go ahead and report me”) arrives at ~5 s. Viewers left before it.
- **Two texts fight for attention in the first seconds.** Small yellow hook bar at the top + a different sentence in the captions; in S01 the game's distance counter (“242m”) sits right next to the hook.
- **Captions cut mid-phrase** every 3 words: “FALLING OFF MY” / “BATHROOM CEILING IN” — hard to read on a phone.
- **Dark, low-contrast backgrounds** (Minecraft night/cave scenes) with jump cuts in the footage.
- **Voice:** old Piper voice at 4.3 words/s — the fastest of all tested and flatter in timbre. Note: I can't listen to audio; this is from measurements, not hearing.
- **Part 1 shorts ended without a resolution** (“full story on my channel”).

## 2. Voice test (same hook, 4 voices)
Files in `voice_samples/` — A is the old voice, C is the chosen one. Please listen to A vs C yourself; numbers below are objective proxies only.

| sample | sec | words/s | pitch range (semitones) | errors when transcribed |
|---|---|---|---|---|
| A_piper_ryan | 6.1 | 4.27 | 13.3 | 0% |
| B_kokoro_michael | 7.79 | 3.34 | 9.38 | 0% |
| C_kokoro_puck | 7.23 | 3.6 | 13.33 | 0% |
| D_kokoro_heart | 7.23 | 3.6 | 7.6 | 0% |

Chosen: **C_kokoro_puck** — widest pitch variation (least monotone), calmer pace than the old voice, 0 transcription errors. Kokoro misread “$3,000 each” as “dollar 3,000”, so those numbers are spelled out for the voice and shown as digits in captions.

## 3. Final files — checks run on the actual MP4s
| file | size | length | first word | transcript vs script | caption sync median / max | black / frozen frames | loudness |
|---|---|---|---|---|---|---|---|
| HT01_wrong_cat.mp4 | 1080×1920 | 38.10 s | 0.0 s | 0.7% diff* | 94 / 478 ms | none / none | -15.7 LUFS |
| HT02_store_215.mp4 | 1080×1920 | 37.50 s | 0.0 s | 5.6% diff* | 92 / 518 ms | none / none | -15.7 LUFS |
| HT03_dentist_review.mp4 | 1080×1920 | 37.80 s | 0.0 s | 13.7% diff* | 96 / 761 ms | none / none | -15.7 LUFS |

*Differences are number formats (“$300” vs “three hundred”) and one misheard word (“Around” → “Round” in HT01). Full transcripts: `qa.json`.
Caption sync measured against speech recognition word timings on the final audio; re-check with a more accurate model gave median 0.14–0.16 s, 90% of captions within 0.25 s.

**Visual check:** 1-frame-per-second contact sheets (`*_sheet.jpg`) reviewed for all three videos: voice and motion start in frame 1; hook text readable at thumbnail size; captions 1–2 lines, centered at 46% height — clear of the bottom title area and the right-hand buttons; translucent box keeps text readable when the game character passes behind; numbers and key words in yellow; no black frames, freezes or jump cuts; Jellevate corner mark cropped out (credit kept in description); video ends 0.8 s after the last sentence.

## 4. What is NOT verified
- I can't hear audio: naturalness of the voice is judged by measurements. Listen to at least the first 5 seconds of each before posting.
- Story facts are limited to the outlines in Drive; original posts could not be opened from here.

## 5. How to read the test
Post the three manually, one per day, on a channel that gets impressions (new channel or TikTok). Compare after 48 h: % ‘stayed to watch’ (old best: 24.8%) and average % viewed (old: 41%). Target: >50% stayed and >70% viewed.
