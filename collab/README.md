# Storytelling Vibe — shared workspace (Claude ⇄ ChatGPT)

Repo: `Rusikrf/shorts`, branch **`storytelling`**, folder **`collab/`**.
Ruslan (owner) decides; Claude and ChatGPT exchange work here.

## Folders
| folder | who writes | what |
|---|---|---|
| `tasks/` | Claude (and Ruslan) | One file per task: `TASK_###_<who>_<topic>.md`. Each says what to do, the exact output files and where to put them. |
| `research/` | both | Channel analyses and notes. One file per author. |
| `inbox/<task>/` | ChatGPT | Raw materials for Claude: generated images (PNG/JPG), prompt logs. |
| `outputs/` | Claude | Finished videos, scripts, SRT, QA reports. |

## Protocol
1. Open `tasks/` and do every task whose `Status:` is `OPEN` and whose `Assignee:` is you.
2. Put results exactly where the task says, with the exact file names.
3. In the task file, change `Status: OPEN` → `Status: DONE` and add a short `## Report` (what was done, what failed, links).
4. Commit message: `<TASK id>: <short summary>`.
5. Never delete or overwrite the other side's files. If something is wrong, write it in the task's report.

### How ChatGPT uploads files
GitHub web UI → `Rusikrf/shorts` → switch branch to `storytelling` → open the target folder → **Add file → Upload files** → commit directly to `storytelling`.
If upload is not possible, put the files in Google Drive `ChatGPT/stories/collab_inbox/<task>/` and say so in the report.

## Rules for all content
- Stories presented as real: no invented events, people, numbers or quotes beyond the source outline. Drama comes from delivery, not new facts.
- Images and footage must be ours (generated) or explicitly licensed for monetized use. No logos, brands, real people, celebrities, or copyrighted characters.
- English for everything that goes on screen.
