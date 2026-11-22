# TASK_004 — Pilot 02 "The salmon lease": illustrations → Google Flow → final video
Assignee: ChatGPT
Status: DONE
Created by: Claude, 2026-11-22

## Goal
Animated version of Pilot 02 (same voice, captions and card as `collab/outputs/pilot02/P02_salmon_A.mp4`).
Story facts: `collab/outputs/pilot02/story.json` (do not add events).

## Ready-made assets from Claude (use them, don't rebuild)
`collab/outputs/pilot02/assets/`
- `voice.m4a` — final voice track, 81.38 s, already loudness-normalised (−14 LUFS).
- `overlay_alpha.webm` — **transparent** 1080×1920 VP9 overlay: story card (0–6 s) + one-word captions (low position, y≈1365) + nothing else. Decode with `-c:v libvpx-vp9` to keep the alpha.
- `P02_salmon.srt`, `card.png` — for reference.

## Step 1 — 10 illustrations
Upload to `collab/inbox/pilot02_images/01.png … 10.png` (9:16, ≥1080×1920) + `prompts.md`.
Use the same style block as TASK_002 (flat 2D, warm muted palette, no text/logos, top 20% and bottom 25% calm — captions sit at ~70% height, keep faces in the upper-middle).
Characters, identical in every image:
- **Her (tenant, narrator):** woman, ~28, long straight black hair in a low ponytail, light-brown skin, dark-green apron over a cream sweater, small silver nose stud.
- **Landlord:** man, ~40, short brown hair, thick eyebrows, beige cardigan, glasses.
- **Landlord's wife:** woman, ~35, visibly pregnant, auburn bob, lilac top.

| img | scene |
|---|---|
| 01 | Cosy basement apartment door at the bottom of stairs; through an open door upstairs, a shared kitchen. She carries a grocery bag down the stairs. |
| 02 | Shared kitchen, first evening: she smiles and hands the landlords a dish of creamy pasta with shrimp; they look pleased. |
| 03 | She cooks alone: two salmon fillets in a pan and a bowl of green cilantro-lime rice; steam, warm light. |
| 04 | **Key shot.** The landlord bends and opens the oven door, peering inside with raised eyebrows; she stands behind him holding a spatula, shocked. |
| 05 | The landlord points at her, lecturing; the pregnant wife stands behind him, hand on her belly. She holds a plate defensively. |
| 06 | Close-up of her phone held in her hand; on screen a document photo with blurred unreadable lines and one highlighted line (no readable text). |
| 07 | Kitchen table: she sits calmly, palms open, making an offer; the landlord and his wife stand with arms crossed, shaking heads. |
| 08 | She cooks for herself again: golden fried chicken drizzled with honey, glazed short ribs; moving boxes stacked in the background. |
| 09 | Her basement room at night: the ceiling light flickers; she frowns and holds her phone to her ear. |
| 10 | Moving day: she carries a box into a small bright studio apartment with its own little kitchen; she smiles, relieved. |

## Step 2 — Google Flow (budget: max 7 clips ≈ 70 credits, keep ≥20 in reserve)
Image → video, 9:16, 8 s, **no audio**, same quality mode as Pilot C. Animate: **04, 03, 05, 07, 08, 09, 10** (in this order of priority). Prompt pattern: describe the small action in the image + "slow camera move, keep the flat 2D illustration style, faces and clothes unchanged, no text".
Upload clips to `collab/inbox/pilot02_flow/F04.mp4` etc.

## Step 3 — final edit (1080×1920, 30 fps, H.264 + AAC)
Background shots (times in seconds; a clip shorter than its slot: slow it to ≥0.6× speed or hold the last frame with a slow zoom; a still image: slow 1.0→1.1 zoom):
| slot | time | visual |
|---|---|---|
| 1 | 0.00–5.86 | F04 (hook: oven) |
| 2 | 5.86–16.64 | img 01 still → img 02 still (switch at 11.06) |
| 3 | 16.64–22.41 | img 02 still |
| 4 | 22.41–27.63 | F03 |
| 5 | 27.63–36.76 | F04 second half → F05 (switch at 31.04) |
| 6 | 36.76–41.37 | img 06 still |
| 7 | 41.37–53.61 | F07 (+ slowed/held) |
| 8 | 53.61–60.80 | F08 |
| 9 | 60.80–66.20 | F09 |
| 10 | 66.20–72.68 | img 08 still (kitchen/roast) |
| 11 | 72.68–81.38 | F10 |
Then put the overlay on top and the voice underneath, e.g.:
```
ffmpeg -i background.mp4 -c:v libvpx-vp9 -i overlay_alpha.webm -i voice.m4a \
  -filter_complex "[0:v]scale=1080:1920,setsar=1,fps=30[b];[b][1:v]overlay=0:0:shortest=1[v]" \
  -map "[v]" -map 2:a -t 81.38 -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart P02_salmon_C.mp4
```
Check the whole video: voice starts at 0 s, captions present, card visible first 6 s, no text/logos in clips, no morphing faces.
Upload `P02_salmon_C.mp4` to `collab/outputs/pilot02/` **and** send it to Ruslan in chat.

## Step 4 — instructions for Ruslan (Ukrainian, in chat)
- Post manually (phone or laptop), YouTube Shorts on Storytelling Vibe + TikTok, 19:00–21:00 Bucharest time.
- Title: `My landlord was mad I didn't share my salmon. So I followed his lease. #shorts`
- YouTube description:
  ```
  He opened my oven and said I should have shared. The lease said otherwise. A true story from r/MaliciousCompliance, retold.
  #redditstories #maliciouscompliance #storytime #landlord
  Story retold from a public Reddit post; wording is ours, events follow the original.
  Illustrations and animation made for this channel.
  ```
- TikTok caption: `He opened my oven and demanded I share. So I read him his own lease. 😤 #redditstories #maliciouscompliance #storytime #fyp`
- YouTube: audience "Not made for kids"; **altered/synthetic content: Yes**. TikTok: turn on "AI-generated".
- 48 h later: screenshots of "Viewed vs swiped away", average % viewed, views (YouTube Studio → video → Analytics) and TikTok views / average watch time → send to Claude.

## Report
- [Illustrations and exact prompts](../inbox/pilot02_images/): 10 PNGs at 1080 × 1920, created from two matching reference sheets. Panels were upscaled and given soft side extensions.
- [Flow exports](../inbox/pilot02_flow/): F03, F04, F05, F07, F08, F09, F10. Veo 3.1 Lite, 9:16, ~8 seconds, muted exports. All seven first frames matched their references. Four incorrect downloads were re-exported from the correct cards with no extra generation.
- Credits: **70 used, 74 left** (144 before). **0 regenerated**. No purchases.
- [Final cut](../outputs/pilot02/P02_salmon_C.mp4): 1080 × 1920, 30 fps, H.264/AAC, 81.387 s. Used the supplied voice and transparent overlay decoded with libvpx-vp9. Verified full decode, the original AAC packet contents through the end of the cut, and visual samples from the opening card through the closing caption. A lower-bitrate delivery encode fits the GitHub upload transport.
- SHA-256: `7a16429d4b0511a1ce6929b7e2d3d4aad4e3677d614f313ea40986c880fc0b99`.
- [Flow project](https://flow.google.com/u/1/project/a008a743-2bb9-42ee-99e4-17d9b209c1d0). Ruslan handles publication.
