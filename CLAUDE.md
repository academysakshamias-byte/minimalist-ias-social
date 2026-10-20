# Minimalist IAS — Instagram pipeline (runbook for scheduled runs)

This repo holds everything a scheduled run needs to make and publish @minimalistias posts:
- `engine/` — renderers
- `poses/` — Aarav & Priya cut-outs and prop masks
- `brand/` — fonts and X-Ray images
- `posts/` — published JPEGs (public; Instagram pulls them via Wix Media)

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
  - Send the draft (slides plus caption) first.
  - If he hasn't replied with changes or "hold" by 7:00 PM IST, silence = approval: publish at 7 PM.
  - If no Telegram PYQ is set for today, choose an unused one yourself (Prelims GS, 2019 or later) and set it as today's `pyqOfTheDay` pointer.
- **Slide count is flexible (Shivam, 20 Oct):** 5 slides by default. Add up to 3 "extra" slides (`spec.extra`, inserted after the answer) when the PYQ genuinely needs them, e.g.:
  - statement-by-statement analysis
  - a map or chart explanation
  - a "who else / related facts" slide
  - a current-affairs link

  Never pad: each extra slide must teach something the others don't, and it obeys the same fact-check and phone gate.
- **Limits:** never more than 6 Instagram posts a day. Media only from static.wixstatic.com.

## PYQ of the Day (daily, 4 PM draft → 7 PM publish)
1. **Get today's PYQ id:** `pyqOfTheDay` collection on the Wix site 9f199c19-1835-4ffe-b42d-d61dedf7766c (Wix connector, CallWixSiteAPI, wix-data query, sorted by day desc, day ≤ today IST). Fall back to `https://www.minimalistias.com/pyq-today?format=json` if reachable.
2. **Get the question and explanation:** `src/data/pyq/prelims.json` in the private repo `academysakshamias-byte/minimalist-ias` (add_repo with read access, shallow clone).
3. **Re-check the website explanation** for this one PYQ only (the bank was audited once already). If something is wrong, tell Shivam with the source; don't edit the site.
4. **Write `spec.json`** for `engine/pyq_post.py` (see its docstring):
   - hook
   - Aarav and Priya picks and lines (poses from `poses/cut`)
   - answer head
   - verdicts
   - source
   - remember / trap (`trap_who`) / method
5. **Render:** `python3 engine/pyq_post.py spec.json /tmp/run` and check the gate output.
6. **Review:** run the fresh reviewer agent; fix; re-render.
7. **Export and push:** `python3 engine/export.py /tmp/run posts/YYYY-MM-DD/pyq`, then commit and push to main. The raw URLs are printed.
8. **Upload to Wix:** `UploadImageToWixSite` (siteId above) with `imageUrls` = the raw URLs → static.wixstatic.com URLs.
9. **Caption:**
   - Hook with exam keywords.
   - The question in text.
   - "Comment a/b/c/d · Comment PYQ for the full explanation".
   - Website link with `?utm_source=instagram&utm_medium=social&utm_campaign=pyq-of-the-day`.
   - At most 5 hashtags.
   - Alt text per slide.
10. **Draft or publish:**
    - DRAFT mode: send the slides and caption to Shivam and wait.
    - On "publish": `instagram_publish_carousel` (Minimalist IAS Instagram connector) with the wixstatic URLs, then the "PYQ is live" story.

## Core 60 (weekly: Wednesday 7:45 PM draft → Thursday 9 AM publish)
One of the Syllabus X-Ray's 60 Prelims Core sub-topics per week, in rank order (#1 first). Ask: share. Product: the X-Ray Core poster on the last slide (the series' only product mention).
1. **Which number:** query the Wix collection `instagramPosts` for tags starting `core-`; next N = highest + 1 (start at 1). Never repeat a number.
2. **Data:** `python3 engine/core_data.py <site_repo> N /tmp/coreN.json` gives the name, year counts, every question with answer key and the site's audited explanation, the NCERT chapters, and the Core stats. Use these numbers as they are; never estimate.
3. **Write the spec** for `engine/core_post.py` (see its docstring):
   - name: short form of the sub-topic (≤ 2 lines at 84 px)
   - Aarav asks / Priya explains (≤ 40 characters each, 2 lines max; Priya can be wrong only if the content shows it)
   - pattern: sort ALL the questions into 2–4 kinds (counts must add up to `asked`) + a one-line takeaway
   - 3 traps taken from real questions (cite the year)
   - the latest 3 PYQs (short faithful paraphrase + answer key)
   - read only this: the NCERT chapters from the data, plus one method line; skip line
4. **Render:** `python3 engine/core_post.py spec.json /tmp/core`. Gate: minFs ≥ 26, no offEdge, no overlaps, `cwords` ≤ 45 on every slide. Look at every PNG.
5. **Reviewer:** a fresh agent gets the spec, the PNGs and the full question file; it re-sorts the questions and checks every line (OK / FIX / RISKY with sources). Apply fixes, re-render.
6. **Export:** `python3 engine/export.py /tmp/core posts/<thursday>/core`, push, upload via commit-SHA raw URLs, publish with tag `core-NN` (two digits).
7. **Caption:** "Core #N of 60 · <name>", one line on the pattern, what's inside, "Send this to your study partner", the free link to all N questions (minimalistias.com/upsc-syllabus/prelims, link in bio), ≤ 5 hashtags, alt text per slide.

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
