# Minimalist IAS — Instagram pipeline (runbook for scheduled runs)

This repo holds everything a scheduled run needs to make and publish @minimalistias posts:
- `engine/` — renderers
- `poses/` — Aarav & Priya cut-outs and prop masks
- `brand/` — fonts and X-Ray images
- `posts/` — published JPEGs and reel MP4s (public; Instagram and YouTube pull them via Wix Media)

The full plan is in the claude.ai project doc "Instagram content system — final plan" (`claude/instagram-pyq-of-the-day-pipeline.md`). The character rules are in `claude/aarav-priya-character-guide.md`.

## Hard rules
- **Facts first.** Every claim on a slide is verified against official or standard sources. Then a FRESH independent reviewer agent (one that has not seen the drafting) checks facts, concepts and meaning drift. If anything is flagged and can't be fixed with a cited source, hold the post and tell Shivam.
- **Characters are fictional.**
  - No invented scores, selections or testimonials.
  - They may *use* products (X-Ray, website); they never credit them for a result.
  - Priya is right about 60–70% of the time.
  - Hinglish only on emotional beats.
- **Nudge ladder:**
  1. Free (`/pyq-today`, Brief, readiness check, free answer evaluation)
  2. X-Ray (only where the topic fits)
  3. Mentorship (emotional beats, about once a month)

  A product appears on about 2 of every 10 feed posts, never on the PYQ cover.
- **Phone gate:** `cards.py` must report, for every slide:
  - minFs ≥ 26
  - no offEdge
  - no overlaps
  - content ≤ 45 words (the verbatim question is exempt)
- **Approval (PYQ of the Day, set by Shivam on 20 Oct 2026):**
  - Send the draft (the reel, its cover and both captions) first.
  - If he hasn't replied with changes or "hold" by 7:00 PM IST, silence = approval: publish at 7 PM.
  - If no Telegram PYQ is set for today, choose an unused one yourself (Prelims GS, 2019 or later) and set it as today's `pyqOfTheDay` pointer.
- **Slide count is flexible (Shivam, 20 Oct; carousels only, the PYQ is now a reel):** 5 slides by default. Add up to 3 "extra" slides (`spec.extra`, inserted after the answer) when the PYQ genuinely needs them, e.g.:
  - statement-by-statement analysis
  - a map or chart explanation
  - a "who else / related facts" slide
  - a current-affairs link

  Never pad: each extra slide must teach something the others don't, and it obeys the same fact-check and phone gate.
- **Limits:** never more than 6 Instagram posts a day (YouTube: at most 3 uploads a day). Media only from static.wixstatic.com / video.wixstatic.com.
- **Stories are 9:16 (Shivam, 20 Oct: a 4:5 slide posted as a story spilled off the phone screen).** Never pass a feed slide straight to `instagram_publish_story`. Frame it first: `python3 engine/story.py <slide.jpg> posts/<date>/<kind>-story/story.jpg "<kicker>" "<line>"` → 1080×1920 with the top 250 px and bottom 260 px clear. Commit it, upload it through Wix like the slides, and post that wixstatic URL. Look at the JPEG first.

## PYQ of the Day (daily, 4 PM draft → 7 PM publish): a REEL on Instagram + the same video as a YouTube Short
Shivam, 20 Oct 2026: "daily PYQs as a reel instead of a post", "same reel to be posted on YouTube as well", goal = reach
millions on both. The reel is built for what both platforms rank on (researched 20 Oct 2026): completion rate and
replays (watch time), sends per reach (strongest signal for non-followers on Instagram), saves, and a strong first
second. So: frame 0 already shows the whole hook on two faces; ~32–40 s; every beat ≤ 4.5 s except the question; a
3-2-1 countdown; "save this" and "send this to the friend who'd pick (x)" asks; the last 0.6 s fades back to the hook
so the loop is seamless; original music, captions only, no watermark, no reposted clips.
1. **Get today's PYQ id:** `pyqOfTheDay` collection on the Wix site 9f199c19-1835-4ffe-b42d-d61dedf7766c (Wix connector, CallWixSiteAPI, wix-data query, sorted by day desc, day ≤ today IST). No row for today → choose an unused Prelims GS PYQ (2019+) and save it as today's pointer. Prefer questions ≤ 90 words (they read well in a reel); longer ones split into two cards automatically.
2. **Get the question and explanation:** `src/data/pyq/prelims.json` in the private repo `academysakshamias-byte/minimalist-ias` (add_repo with read access, shallow clone).
3. **Re-check the website explanation** for this one PYQ only. If something is wrong, tell Shivam with the source; don't edit the site.
4. **Write `spec.json`** (same fields as `engine/pyq_post.py`, see `engine/pyq_reel.py` docstring):
   - hook: a curiosity question ≤ 9 words with one `<em>` phrase; it is frame 0, the cover and the YouTube title, so put the searchable topic word in it ("cobalt", "Article 360", "Ramsar site").
   - Aarav and Priya picks and lines (≤ 9 words each); Priya right about 60–70% of the time; the wrong pick is the most tempting wrong option.
   - answer_head, 2–3 verdicts, source, remember / trap (`trap_who`) / method.
   - `topic` ("Geography · critical minerals") and ≤ 5 `hashtags` for the caption; optional `yt_tags`.
   - `dm_word`: one easy keyword from the topic, ≤ 8 letters preferred, not a common word and never a, b, c, d or PYQ ("CONGO", "RAMSAR", "ART360"). The reel ends "Comment CONGO → we'll DM you today's 1-page revision sheet" (Shivam, 20 Oct 2026: comment-to-DM for comments, saves and leads).
   - `extra` is not shown in the reel by default (`reel_extra: false`): completion rate beats depth here; the website has the depth.
5. **Render:** `python3 engine/pyq_reel.py spec.json /tmp/reel` (~5 min). It also renders `sheet.jpg`, the DM revision sheet (`engine/sheet.py`, built only from the spec; gate: minFs ≥ 26, no overflow). Gate per scene: minFs ≥ 26, no text outside x 140–920 / y 300–1300 (inside both the Reels and the Shorts UI), no overlaps, ≤ 45 content words. `"fail": {}` or fix the spec. Look at every file in `/tmp/reel/stills/`, plus `cover.jpg` and `story.jpg`.
6. **Review:** the fresh reviewer agent checks the question, key and every on-screen line (OK / FIX / RISKY with sources); fix; re-render.
7. **Export and push:** copy `reel.mp4`, `cover.jpg`, `story.jpg`, `sheet.jpg`, `meta.json`, `spec.json` into `posts/<date>/pyq-reel/`; commit and push to main; note the commit SHA.
8. **Upload to Wix:**
   - cover, story and sheet: `UploadImageToWixSite` (imageUrls = commit-SHA raw URLs) → static.wixstatic.com URLs.
   - save the DM data on today's pointer row: wix-data PATCH `https://www.wixapis.com/wix-data/v2/items/<today>` (collection `pyqOfTheDay`) with SET_FIELD `dmWord` = the keyword and `sheetUrl` = the sheet's wixstatic URL. The comment auto-reply task reads them from there.
   - video: `CallWixSiteAPI` POST `https://www.wixapis.com/site-media/v1/files/import` with `{url: <raw reel.mp4 URL>, mimeType: "video/mp4", displayName: "pyq-<date>.mp4", mediaType: "VIDEO", private: false}`; then GET `https://www.wixapis.com/site-media/v1/files/get-file-by-id?fileId=<id>` about once a minute until `operationStatus` is `READY`; use `media.video.resolutions[]` → the `1080p` mp4 URL (`https://video.wixstatic.com/video/<id>/1080p/mp4/file.mp4`).
9. **Text** (start from `meta.json`; keep its keyword-first first lines):
   - Instagram caption = `ig_caption`: hook + "UPSC Prelims <year> PYQ" first (Instagram search reads captions), the question in text, "Aarav says (x). Priya says (y). Who's right?", "Pause the reel and pick yours. Comment a, b, c or d 👇" (keep "Comment a, b, c or d" exactly: the answer-split story finds the post by it), the "Comment WORD and we'll DM you…" line, the send line, the free link, ≤ 5 hashtags.
   - YouTube: `yt_title` (≤ 100 characters, ends "#Shorts"), `yt_description`, `yt_tags`.
10. **Draft (4 PM):** send Shivam `reel.mp4`, the cover and both texts: "Publishing at 7:00 PM IST on Instagram and YouTube unless you reply with changes or 'hold'." Silence by 7 PM = approval.
11. **Publish (7 PM):** check `instagram_recent_media` first (never twice).
    - Instagram: `instagram_publish_reel` (video_url = the 1080p wixstatic MP4, caption, cover_url, tag `pyq-<date>`); if it returns a creation_id, call `instagram_publish_container` (creation_id, kind "reel", the same tag and caption) once a minute for up to 5 minutes. Then `instagram_publish_story` with the story.jpg wixstatic URL (tag `pyq-<date>-story`).
    - YouTube: `youtube_upload_short` (same connector) with the same MP4 URL, `yt_title`, `yt_description`, `yt_tags`, privacy "public", tag `pyq-<date>`. If the result says YouTube kept it private (Google's app audit isn't done yet), tell Shivam: "Tap Visibility → Public in YouTube Studio" with the link. If YouTube isn't connected yet, say so once and carry on with Instagram.
    - Record both on today's `pyqOfTheDay` row (wix-data PATCH, SET_FIELD): `ytVideoId`, `ytPublishedAt` (from youtube_recent), `ytTitle`, `ytDuration` (e.g. "PT35S"), `igPermalink`. The question's page on the website then shows "the 35-second version" (the Short + the sheet) with VideoObject/ImageObject structured data for search and answer engines.
    - Report both links.

## Comment-to-DM (runs inside the comment auto-reply task)
For every comment on a PYQ reel that contains that day's `dmWord` (any case, as a word; `pyqOfTheDay` row of the reel's day, found via the reel's `instagramPosts` row → `day`):
1. `instagram_private_reply` (comment_id, message). Meta allows ONE private message per comment, within 7 days. Message:
   "Here's your 1-page revision sheet + the 35-second video for today's PYQ 📘\nhttps://www.minimalistias.com/pyqs/prelims/<year>/q<n>?utm_source=instagram&utm_medium=dm&utm_campaign=revision-sheet#revision-sheet\nA new PYQ every evening at 7. Follow @minimalistias so you don't miss it."
   The link goes to the question's page on the website, not to the image: the page shows the sheet, the Short and every option explained, so each DM is a website visit (Shivam, 20 Oct 2026: reels, Shorts and DMs should all lead to the site).
2. Then a short public reply under the comment: "Sent! Check your DMs 📩 (if you don't follow us yet, look in message requests)". Vary the wording slightly.
3. The tool logs `dm:<commentId>` in `instagramReplies`, so a comment is never messaged twice. Skip our own account. At most 50 DMs a run. If Meta refuses (permission or policy error), stop DMs for the run, reply publicly with the sheet link instead, and tell Shivam the exact error once.

## Core 60 (weekly: Wednesday 7:45 PM draft → Thursday 9 AM publish)
One of the Syllabus X-Ray's 60 Prelims Core sub-topics per week, in rank order (#1 first). Ask: share. Product: slide 6 shows that sub-topic's real X-Ray row (verbatim from `core_data.py`), the one-a-week vs all-today gap and the live price — the series' only product mention. One post a week (Shivam, 20 Oct: keep weekly, judge by student response before changing).
1. **Which number:** query the Wix collection `instagramPosts` for tags starting `core-`; next N = highest + 1 (start at 1). Never repeat a number.
2. **Data:** `python3 engine/core_data.py <site_repo> N /tmp/coreN.json` gives the name, year counts, every question with answer key and the site's audited explanation, the NCERT chapters, and the Core stats. Use these numbers as they are; never estimate.
3. **Write the spec** for `engine/core_post.py` (see its docstring):
   - name: short form of the sub-topic (≤ 2 lines at 84 px)
   - Aarav asks / Priya explains (≤ 40 characters each, 2 lines max; Priya can be wrong only if the content shows it)
   - pattern: sort ALL the questions into 2–4 kinds (counts must add up to `asked`) + a one-line takeaway
   - 3 traps taken from real questions (cite the year)
   - the latest 3 PYQs (short faithful paraphrase + answer key)
   - read this first: the NCERT chapters from the data, plus a skip line
4. **Render:** `python3 engine/core_post.py spec.json /tmp/core`. Gate: minFs ≥ 26, no offEdge, no overlaps, `cwords` ≤ 45 on every slide (the verbatim X-Ray row is exempt). Look at every PNG.
5. **Reviewer:** a fresh agent gets the spec, the PNGs and the full question file; it re-sorts the questions and checks every line (OK / FIX / RISKY with sources). Apply fixes, re-render.
6. **Export:** `python3 engine/export.py /tmp/core posts/<thursday>/core`, push, upload via commit-SHA raw URLs, publish with tag `core-NN` (two digits).
7. **Caption:** "Core #N of 60 · <name>", one line on the pattern, what's inside, "Send this to your study partner", the free link to all N questions (minimalistias.com/upsc-syllabus/prelims, link in bio), ≤ 5 hashtags, alt text per slide.

## Test Yourself (weekly: Saturday 7:42 PM draft → Sunday 9 AM publish)
5 MCQs from the week's Daily Brief bank (memory `/areas/upsc-brief-mcq-bank/mon.md` … `sat.md`; use only entries dated in this Mon–Sat week), Aarav's score to beat, the answer key, then "comment your score". Ask: comment your score. Free nudges: the readiness check (score below 3) and the free Weekly Quiz. On the last Sunday of each month set `"monthly": true`: Priya reassures and points to the free strategy call (the monthly mentorship touch). No other product.
1. **Pick 5:** one per day where possible; at least two GS papers; mixed difficulty; prefer shorter questions (they read better on a phone); never pick a question that tests a proposal or a pending case. Copy question text, options and key **verbatim** from the bank.
2. **Aarav:** pick his answers so he scores 2–4 of 5 (vary week to week). When he's wrong, his pick is the option that falls for the trap the bank's explanation names. The score is computed by the template, never typed.
3. **why:** ≤ 6 words per question, naming the trap ("The General Assembly elects them").
4. **Render:** `python3 engine/test_post.py spec.json /tmp/test` (8 slides). Gate as usual; the question slides are verbatim and exempt from the word count. Look at every PNG.
5. **Reviewer:** a fresh agent re-checks each question's key against official sources (bare Acts, judgments, official sites) and checks that every `why` matches the explanation. A question that can't be confirmed is swapped for another from the bank.
6. **Export:** `python3 engine/export.py /tmp/test posts/<sunday>/test`, story frame from slide 1 with `engine/story.py`, push, upload, publish with tag `test-<yyyy>-w<NN>`.
7. **Caption:** "Aarav scored N/5 on this week's UPSC current affairs. Can you beat him? 🧠", "Answers on slide 7 · comment your score 👇", the free Weekly Quiz link (minimalistias.com/resources/weekly-quiz, link in bio), ≤ 5 hashtags, alt text per slide.

## Daily stories (10:13 AM, 1:13 PM, 3:13 PM: each runs whatever is due and not yet posted today)
Native 9:16 stories from `engine/stories.py` (no draft step: every word comes from already-published, fact-checked material or real counts). Tags make each story post once a day: `story-brief-<date>`, `story-split-<date>` (`story-eval-<date>` when the Saturday story is restarted).
1. **Room check first:** count today's rows in `instagramPosts`. Keep 2 slots free for the 7 PM PYQ reel + story (if not yet posted). Post a story only if `posts today + reserved + 1 ≤ 6`. Priority: Brief top 3 > answer split.
2. **Brief top 3** (`stories.py brief`): today's `dailyBriefs` row (briefDate = today IST). The Brief lands between ~8 AM and ~2:30 PM, so if it isn't there yet, do nothing; a later run will post it.
   - Pick 3 articles from different GS papers where possible (no GS4), the most exam-relevant first.
   - title = the Brief's title verbatim; gs like "GS2 · POLITY"; why = the Brief's own why line, trimmed to ≤ 90 characters without adding anything.
3. **Answer split** (`stories.py split`, first run of the day): yesterday's PYQ reel (instagram_recent_media: the post whose caption has "Comment a, b, c or d", published yesterday IST).
   - Count one vote per username: their first comment that is just an option letter ("c", "C", "(c)", "c)", "option c"). Exclude our own account.
   - Post only if there are ≥ 10 votes; real counts only, never rounded up or padded.
   - The answer and tag come from yesterday's `pyqOfTheDay` row → `prelims.json` (key and option text).
4. **Saturday evaluation: PAUSED** (Shivam, 20 Oct 2026: "pause this till I say to start"). Do not post it. The template (`stories.py evaluate`) stays ready for when he restarts it.
5. **Publish:** save the JPEGs under `posts/<date>/stories/`, commit and push, upload them via the commit-SHA raw URLs, then post with `instagram_publish_story` and the tag. Look at each JPEG first; `unsafe` in the output must be empty.

## Assets
- **Poses (`poses/cut`):**
  - aarav_* (15)
  - priya_* (14)
  - duo_* (3)
  - props: aarav_phone, aarav_sheet, aarav_answersheet, priya_phone, priya_sheet, priya_notebook, duo_sheet, duo_laptop
- **Branded props:** `engine/props.py` → `compose(name, content_png, out_png)` warps any image onto the blank screen or sheet.
- **Brand:**
  - colours: dark #13110d, gold #f2b705, cream #f3eee3
  - fonts: Newsreader + IBM Plex (`brand/fonts`)
  - logo: gold/ivory diamond (`brand/favicon.svg`)
