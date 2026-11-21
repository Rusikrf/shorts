# TASK_003 — Google Flow: animate Pilot 01 key shots (Pilot C)
Assignee: Ruslan (or Claude via Ruslan's browser, if signed in to Flow there)
Status: OPEN
Created by: Claude, 2026-11-21

## Goal
Turn the 6 most important illustrations into short animated clips (image → video), then Claude rebuilds Pilot 01 as version **C** with real motion.
Budget: 6 clips × ~10 credits = **~60 credits** (of ~200). Do not use the high-quality mode unless a clip fails.

## How
Google Flow → new project → for each row: **Frames to Video / Ingredients**, start frame = the image from `collab/inbox/pilot01_images/`, aspect **9:16 (portrait)**, length 8 s, **no audio** (or mute), prompt below.
Download each result as `C01.mp4` … `C06.mp4` and upload to `collab/inbox/pilot01_flow/` (or Drive `ChatGPT/stories/collab_inbox/pilot01_flow/`).

| file | start image | prompt |
|---|---|---|
| C01 | 04.png | Slow push-in over her shoulder toward the phone; the small plane icon glides along the dotted route on the map; soft screen glow flickers on her hair. Keep the flat 2D illustration style, no text. |
| C02 | 01.png | She waves goodbye, he walks toward the terminal waving back, light breeze in her hair, people walking in the background, gentle camera drift right. Flat 2D style, no text. |
| C03 | 02.png | He talks on the phone in the gate queue, glances sideways nervously, people shuffle forward behind him, subtle handheld camera. Flat 2D style, no text. |
| C04 | 05.png | She looks up from the phone with growing suspicion, eyebrows rising; the dog tilts its head and looks at her; slow push-in on her face. Flat 2D style, no text. |
| C05 | 06.png | She leans closer to the laptop, scrolls on her phone, then taps the map; steam rises from the coffee mug; slow camera orbit. Flat 2D style, no text. |
| C06 | 07.png | She speaks calmly and firmly into the phone, then lowers it and exhales; city lights twinkle outside; slow pull-back. Flat 2D style, no text. |

## Check
Faces and clothes must match the illustrations; no text, no logos, no morphing hands. Regenerate a clip only if it is clearly broken.
When done: set `Status: DONE`, add a `## Report` (credits used, which clips were regenerated).
