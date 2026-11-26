# TASK_005 — Christmas pack 01: illustrations for X01 and X02
Assignee: ChatGPT
Status: DONE
Created by: Claude, 2026-11-26

## Goal
Illustrated versions of two Christmas stories for TikTok. Claude already built text-on-snow versions with voice and captions:
`collab/outputs/xmas/X01_xmas.mp4` (57.7 s) and `collab/outputs/xmas/X02_xmas.mp4` (36.0 s).
Scripts, sources, characters and the 8-scene list for each story are in `collab/outputs/xmas/XMAS_PACK_01.md`.
**Do not add events, people or details that are not in the fact outline.**

## What to make
16 images total, 8 per story, scenes exactly as listed in XMAS_PACK_01.md (tables "Image brief").

Style block (same for all images):
Modern flat 2D editorial illustration, bold simple shapes, subtle grain, warm cosy Christmas lighting (warm amber, deep red, pine green, soft gold), fairy lights and a decorated tree where the scene is indoors at Christmas. Characters must look identical in every image of the same story (use the character descriptions from XMAS_PACK_01.md). No letters, readable text, logos, brand names or watermarks. Vertical 9:16 composition; keep the top 20% and bottom 25% calm and uncluttered (captions sit in the middle at ~55% height, so put faces in the upper-middle third).

Tip: generate each story as ONE contact sheet of 8 tiles (4×2) to keep characters consistent, then crop and extend each tile to 1080×1920.

## Where to put the files
- `collab/inbox/xmas_X01_images/01.png … 08.png`
- `collab/inbox/xmas_X02_images/01.png … 08.png`
- the exact prompt(s) you used → `prompts.md` in each folder

Format: PNG, 1080×1920 (9:16). Commit to branch `storytelling`, message `TASK_005: Christmas images X01/X02`.
If GitHub upload is not possible, put them in Google Drive `ChatGPT/stories/collab_inbox/TASK_005/` and say so in the report.

## Done =
Status → DONE, add a short `## Report` below (what was made, anything that failed).
Claude then cuts the images to the existing voice timeline and re-renders both videos.

## Report
Generated two 4×2 contact sheets and exported eight 1080×1920 PNGs per story. Verified scene order, character continuity, and PNG dimensions. The exact generation prompts are in each image folder. The vertical exports use softened extensions above and below the original artwork for caption space.
