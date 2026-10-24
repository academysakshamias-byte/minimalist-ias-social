#!/usr/bin/env python3
"""Test Yourself — Sunday carousel: 5 MCQs from the week's Daily Brief bank, Aarav's score to beat, answer key, score CTA.
usage: test_post.py spec.json out_dir
spec = {
 "week": 43, "date": "25 Oct 2026", "range": "19–24 Oct 2026",
 "qs": [  # exactly 5, verbatim from the MCQ bank (already fact-checked by the Brief), in the order shown
   {"day": "Mon", "gs": "GS2", "q": "<bank q text with \\n lines>", "options": [["a","..."],...], "a": "c",
    "aarav": "b",            # Aarav's pick: the bank's named trap when he gets it wrong
    "why": "≤ 6 words: the trap, e.g. 'Zero Hour isn't in the Rules'"}],
 "monthly": false            # last Sunday of the month: Priya reassures + free strategy call instead of the readiness check
}
Aarav's score = how many of his picks match the key (computed, never typed). Keep it believable: 2–4 of 5.
Slides: 1 cover (aarav_pointing) · 2–6 one question each (verbatim, exempt from the word count) · 7 answer key with Aarav's
picks · 8 comment-your-score CTA (priya_clap; monthly: priya_reassure + free strategy call).
"""
import json, os, sys, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import chrome, pose, TICK, CROSS

CSS = """
.cv{position:absolute;left:96px;right:96px;top:186px}
.cv .k{font:600 26px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.cv .h{font-size:84px;margin-top:28px;max-width:620px}
.cv .chips{display:flex;flex-direction:column;gap:18px;margin-top:44px}
.cv .chips span{font:600 32px/1.2 var(--sans);color:var(--ivory)}.cv .chips b{color:var(--gold);font:600 38px/1 var(--serif);margin-right:12px}
.ask{position:absolute;left:96px;right:96px;top:1118px;height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 32px/1 var(--sans);z-index:3}
.qw{position:absolute;left:96px;right:96px;top:176px}
.qw .src{font:600 26px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--p-lab);margin-bottom:26px}
.qw .stem{font:500 38px/1.3 var(--serif);color:#16130e;margin:0 0 26px}
.qw .it{font:400 31px/1.4 var(--sans);color:#1a1712;margin:0 0 16px;padding-left:26px;border-left:5px solid #d9a441}
.qw .pr{font:600 31px/1.35 var(--sans);color:#1a1712;margin:22px 0 26px}
.op{display:flex;gap:20px;align-items:center;margin-bottom:20px;font:400 32px/1.3 var(--sans);color:#1a1712}
.qw.big .stem{font-size:46px}.qw.big .it{font-size:35px;margin-bottom:22px}.qw.big .pr{font-size:34px}.qw.big .op{font-size:36px;margin-bottom:26px}
.op i{flex:none;width:54px;height:54px;border-radius:50%;border:2px solid #1a1712;font:600 26px/50px var(--mono);text-align:center;font-style:normal}
.key{position:absolute;left:96px;right:96px;top:186px}
.key .h{font-size:68px;margin-bottom:36px}
.kh{display:grid;grid-template-columns:90px 90px 1fr 110px;gap:16px;font:600 26px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-bottom:14px;border-bottom:2px solid rgba(236,230,216,.16)}
.kr{display:grid;grid-template-columns:90px 90px 1fr 110px;gap:16px;align-items:center;padding:24px 0;border-bottom:2px solid rgba(236,230,216,.1)}
.kr .n{font:600 30px/1 var(--mono);color:var(--muted)}
.kr .a{width:62px;height:62px;border-radius:50%;border:3px solid var(--gold);display:flex;align-items:center;justify-content:center;font:500 italic 38px/1 var(--serif);color:var(--gold);padding-bottom:4px;box-sizing:border-box}
.kr .w{font:400 31px/1.32 var(--sans);color:var(--ink)}
.kr .ar{display:flex;align-items:center;gap:10px;justify-content:flex-end}
.kr .ic{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center}.kr .ic svg{width:22px;height:22px}
.kr .ic.yes{background:#7f9a7a}.kr .ic.no{background:#c6714f}
.kr .pk{font:600 26px/1 var(--mono);color:var(--muted)}
.sc{margin-top:30px;font:500 32px/1.35 var(--sans);color:var(--ivory)}.sc b{color:var(--gold)}
.cta{position:absolute;left:96px;right:440px;top:200px}
.cta .h{font-size:72px}
.cta .pt{margin-top:34px;font:400 32px/1.42 var(--sans);color:var(--ink)}.cta .pt b{color:var(--ivory)}
.cta .url{display:block;margin-top:10px;font:600 30px/1.3 var(--sans);color:var(--gold);white-space:nowrap}
.cpose{position:absolute;right:-30px;bottom:0;height:900px}
.share{position:absolute;left:96px;right:96px;top:1118px;height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 32px/1 var(--sans);z-index:3}
#n1 .ft span:first-child,#n8 .ft span:first-child{visibility:hidden}
"""

def parse(q):
    lines = [l.strip() for l in q.split('\n') if l.strip()]
    stem, items, prompt = [], [], []
    for l in lines:
        if l[:2].rstrip('.').isdigit() and l[1:3].startswith('.') or (l[:1].isdigit() and l[1:2] == '.'):
            items.append(l.split('.', 1)[1].strip())
        elif items:
            prompt.append(l)
        else:
            stem.append(l)
    return ' '.join(stem), items, ' '.join(prompt)

def build(spec, out):
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True); e = html.escape
    Q = spec['qs']; assert len(Q) == 5, 'Test Yourself takes exactly 5 questions'
    T = 8; W = spec['week']; tag = f'Week {W}'
    score = sum(1 for q in Q if q['aarav'] == q['a']); S = []
    S.append(f'''<div class="s" id="n1">{chrome(1,T,"Test yourself",tag,"")}
 <div class="cv"><div class="k">{e(spec['range'])}</div>
  <h1 class="h">Aarav scored <em>{score}/5</em> this week. Can you beat him?</h1>
  <div class="chips"><span><b>5</b>questions from this week's news</span><span><b>1</b>slide with every answer</span></div></div>
 <img class="pose" src="{pose('aarav_pointing')}" style="right:-40px;top:470px;height:820px">
 <div class="fade" style="top:1010px;height:340px"></div>
 <div class="ask">Note your answers · comment your score</div></div>''')
    for i, q in enumerate(Q):
        stem, items, prompt = parse(q['q'])
        its = ''.join(f'<p class="it">{j + 1}. {e(x)}</p>' for j, x in enumerate(items))
        ops = ''.join(f'<div class="op"><i>{k}</i><span>{e(v)}</span></div>' for k, v in q['options'])
        big = len(q['q']) + sum(len(v) for _, v in q['options']) < 380   # shorter questions get larger type
        S.append(f'''<div class="s paper" id="n{i + 2}">{chrome(i + 2,T,f"Question {i + 1} of 5",tag,"Note your answer, then swipe",True)}
 <div class="qw verbatim{' big' if big else ''}"><div class="src">{e(q['day'])}'s Brief · {e(q['gs'])}</div><p class="stem">{e(stem)}</p>{its}{f'<p class="pr">{e(prompt)}</p>' if prompt else ''}{ops}</div></div>''')
    rows = ''.join(f'''<div class="kr"><span class="n chrome">Q{i + 1}</span><span class="a chrome">{q['a']}</span><span class="w">{e(q['why'])}</span>
  <span class="ar chrome"><span class="pk">{q['aarav']}</span><span class="ic {'yes' if q['aarav'] == q['a'] else 'no'}">{TICK if q['aarav'] == q['a'] else CROSS}</span></span></div>''' for i, q in enumerate(Q))
    S.append(f'''<div class="s" id="n7">{chrome(7,T,"Answer key",tag,"Swipe to post your score")}
 <div class="key"><h2 class="h">The <em>answers</em></h2>
  <div class="kh chrome"><span>Q</span><span>Key</span><span>The trap</span><span style="text-align:right">Aarav</span></div>{rows}
  <div class="sc">Aarav: <b>{score}/5</b>. Your turn.</div></div></div>''')
    if spec.get('monthly'):
        body = ('<p class="pt">One low week is information, not a verdict. <b>Talk it through with a mentor, free.</b>'
                '<span class="url">minimalistias.com/services/free-strategy-call</span></p>')
        cp = 'priya_reassure'
    else:
        body = ('<p class="pt">Below 3? <b>Check your Prelims readiness, free.</b><span class="url">minimalistias.com/readiness-check</span></p>')
        cp = 'priya_clap'
    S.append(f'''<div class="s" id="n8">{chrome(8,T,"Your score",tag,"")}
 <div class="cta"><h2 class="h">Comment your <em>score.</em></h2>{body}
  <p class="pt">25 more questions every Sunday, free:<span class="url">minimalistias.com/resources/weekly-quiz</span></p></div>
 <img class="pose cpose" src="{pose(cp)}">
 <div class="fade" style="top:1010px;height:340px"></div>
 <div class="share">Post your score in the comments</div></div>''')
    page = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>{CSS}</style></head><body>{"".join(S)}</body></html>'
    p = os.path.join(out, 'post.html'); open(p, 'w').write(page)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'cards.py'), p, out, '.s'], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    return p

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
