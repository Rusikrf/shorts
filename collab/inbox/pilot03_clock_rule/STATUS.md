# Pilot 03 — 4:00:01 Rule — production status (2026-11-23)
Source: https://www.reddit.com/r/MaliciousCompliance/comments/1ubd7he/just_complying_with_your_written_expectations_and/

## Done
- Source checked against the post.
- 16-line English retell and 9-scene character-consistent storyboard in `story.json` and `PRODUCTION.md` in this directory.
- Nine vertical 1080x1920 image scenes prepared in user's chat download bundle.
- A precise 66-second HeyGen Rosa narration was generated on the user's Free plan. Audio is linked in the Nov 23 chat; asset is not in this public repo.
- 1080x1920, 30fps, ~66-second video with animated pan/zoom, title card, and word-by-word English subtitles was rendered as an intermediate, and sent to the user in chat.
- Prepared Windows script that downloads the narration and merges without video re-encode. Files in same chat bundle.

## Blocker
- Narration URL downloads in a browser but tool runtime could not fetch its bytes to mux them directly. Silent MP4 **must not be published**. Next run can accept WAV uploaded by Ruslan and mux with the rendered MP4 in the same chat (or use merge_voice.bat on user's Windows laptop). Actual word timestamps were returned by HeyGen but are not fully captured to a local file; subtitle timing is line-anchored and approximate, so perform a visual QA on the final result.

## Metadata
Title: My boss gave us a rule down to the SECOND. I followed it. #shorts

Description:
A hospital IT worker's manager wrote an unusually precise shift rule. One last-minute call put that rule to the test.

Retold in our own words from a first-person Reddit account:
https://www.reddit.com/r/MaliciousCompliance/comments/1ubd7he/just_complying_with_your_written_expectations_and/

The account is not independently verified; characters and scenes are AI illustrations.
#redditstories #maliciouscompliance #storytime #shorts

TikTok:
My boss gave us a rule down to the second. I followed it. #redditstories #maliciouscompliance #storytime
