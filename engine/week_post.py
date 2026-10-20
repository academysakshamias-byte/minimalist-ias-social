#!/usr/bin/env python3
"""Week in One Page — Monday carousel ("Priya's notes").
usage: week_post.py spec.json out_dir
spec = {
 "week": 42, "range": "12–18 Oct 2026", "date": "20 Oct 2026",
 "stories": [{"gs": "GS2 · Polity", "t": "headline ≤ 8 words", "k": "Prelims angle, 1–3 words"}],   # 6–12, most important first
 "facts":   ["one-line fact", ...],                                                          # 5
 "mcqs":    [{"s": "statement as UPSC might frame it", "a": "True|False", "why": "one line"}], # 2
 "nudge":   "optional extra line for the CTA slide",
 "page":    true when the week's web page (minimalistias.com/week) is live — the CTA then points there,
 (each story may also carry "pyq": true when UPSC has asked about its theme before — shown as "· PYQ" on the sheet)
 "extra":   [optional 0–2 deeper slides after the facts: {"lab":"Deeper","h":"html heading","points":["..." or {"h":"bold","p":"text"}],"source":"..."}]
}
Slides: 1 cover (Priya + clipboard) · 2 the week on one page (screenshot sheet) · 3 five facts · 4 two MCQ angles + save/brief CTA.
"""
import json, os, sys, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import LOGO_D, LOGO_L, chrome, pose

# subject labels longer than the sheet's label column are shortened on the image (the web page keeps the full word)
SHORT = {"Geography": "Geog.", "Agriculture": "Agri.", "Governance": "Gov.", "Security": "Secur.", "Environment": "Env"}

CSS = """
.cv{position:absolute;left:96px;top:230px;width:560px}
.cv .k{font:600 26px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.cv .h{font-size:92px;margin-top:26px}
.cv .sub{margin-top:30px}
.cv .chips{display:flex;flex-direction:column;gap:16px;margin-top:44px}
.cv .chips span{font:600 32px/1 var(--sans);color:var(--ivory)}.cv .chips b{color:var(--gold);font:600 36px/1 var(--serif);margin-right:12px}
.ask{position:absolute;left:96px;right:96px;top:1110px;height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 34px/1 var(--sans)}
.sheet{position:absolute;left:70px;right:70px;top:160px;bottom:150px;background:#fffaf0;border-radius:24px;box-shadow:0 12px 40px rgba(60,40,0,.12);padding:34px 36px 0}
.sheet .tt{display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #1a1712;padding-bottom:16px;margin-bottom:6px}
.sheet .tt h2{margin:0;font:600 50px/1 var(--serif);color:#16130e}.sheet .tt h2 em{color:var(--p-acc)}
.sheet .tt span{font:600 26px/1 var(--mono);color:var(--p-lab);letter-spacing:.08em}
.row{display:grid;grid-template-columns:132px 1fr;column-gap:20px;padding:15px 0;border-bottom:2px solid rgba(26,23,18,.10)}
.dense .row{padding:6px 0;grid-template-columns:118px 1fr}.dense .row .t{font-size:28px;line-height:1.2}.dense .row .t i{margin-top:2px;line-height:1.15}.dense .row .g{font-size:26px;line-height:1.15;padding-top:2px}
.dense.sheet{top:150px;bottom:140px;padding-top:28px}.dense .tt{padding-bottom:12px}
.row .g{font:600 26px/1.2 var(--mono);color:var(--p-lab);padding-top:4px}
.row .t{font:500 32px/1.25 var(--sans);color:#1a1712}
.row .t i .pq{color:#2f4f7a}
.row .t i{display:block;font:600 26px/1.2 var(--mono);font-style:normal;color:#7a3518;margin-top:6px}
.fx{position:absolute;left:96px;right:96px;top:190px}
.fx .h{font-size:72px;margin-bottom:40px}
.fi{display:grid;grid-template-columns:76px 1fr;gap:18px;margin-bottom:30px;align-items:start}
.fi b{font:500 italic 58px/1 var(--serif);color:var(--gold)}
.fi p{margin:4px 0 0;font:400 32px/1.4 var(--sans);color:var(--ink)}
.mq{position:absolute;left:96px;right:96px;top:190px}
.mq .h{font-size:66px;margin-bottom:34px}
.mc{background:rgba(250,247,240,.06);border:2px solid rgba(242,183,5,.35);border-radius:22px;padding:26px 30px;margin-bottom:26px}
.mc .st{font:500 32px/1.4 var(--sans);color:var(--ivory)}
.mc .a{margin-top:14px;font:600 28px/1.35 var(--sans);color:var(--gold)}
.mc .a span{color:var(--ink);font-weight:400}
.cta{position:absolute;left:96px;right:96px;top:1000px;text-align:center}
.cta .p{font:500 30px/1.35 var(--sans);color:var(--ink);margin-bottom:22px}.cta .p b{color:var(--gold)}
.xw{position:absolute;left:96px;right:96px;top:190px}.xw .h{font-size:64px;margin-bottom:44px}
.xp{font:400 32px/1.42 var(--sans);color:var(--ink);padding:0 0 26px 34px;position:relative}.xp:before{content:"";position:absolute;left:0;top:16px;width:12px;height:12px;border-radius:50%;background:var(--gold)}.xp b{color:var(--ivory);font-weight:600}
.xw .src{margin-top:24px;font:500 26px/1.35 var(--sans);color:var(--muted)}
.cta .pill{height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 34px/1 var(--sans)}
"""

def build(spec, out):
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True); e = html.escape
    X = spec.get('extra') or []; T = 4 + len(X); W = spec['week']; S = []
    n = len(spec['stories'])
    assert 4 <= n <= 12, 'Week in One Page takes 4–12 stories'
    S.append(f'''<div class="s" id="n1">{chrome(1,T,"Priya's notes",f"Week {W}","Swipe for the sheet →")}
 <div class="cv"><div class="k">{e(spec['range'])}</div>
  <h1 class="h">Last week, <em>in one page.</em></h1>
  <div class="chips"><span><b>{n}</b>stories that matter</span><span><b>5</b>facts to remember</span><span><b>2</b>likely MCQ angles</span></div></div>
 <img class="pose" src="{pose('priya_clipboard')}" style="right:-10px;top:300px;height:820px">
 <div class="fade" style="top:1000px;height:350px"></div>
 <div class="ask">Save it — a new sheet every Monday</div></div>''')
    rows = ''.join(f'<div class="row"><div class="g">{"<br>".join(e(SHORT.get(x, x)) for x in s["gs"].split(" · "))}</div><div class="t">{e(s["t"])}<i>{e(s["k"])}{' <span class="pq">· PYQ</span>' if s.get("pyq") else ''}</i></div></div>' for s in spec['stories'])
    S.append(f'''<div class="s paper" id="n2">{chrome(2,T,"The week on one page","Screenshot this",f"Week {W} · {spec['range']}",True)}
 <div class="sheet{' dense' if len(spec['stories']) > 8 else ''}"><div class="tt"><h2>Week <em>{W}</em></h2><span>{e(spec['range']).upper()}</span></div>{rows}</div></div>''')
    fx = ''.join(f'<div class="fi"><b>{i+1}</b><p>{e(f)}</p></div>' for i, f in enumerate(spec['facts']))
    S.append(f'''<div class="s" id="n3">{chrome(3,T,"5 facts to remember",f"Week {W}","Swipe for MCQ angles →")}
 <div class="fx"><h2 class="h">Facts that <em>stick.</em></h2>{fx}</div></div>''')
    for j, x in enumerate(X):
        k = 4 + j
        pts = ''.join(f'<div class="xp"><b>{e(p.get("h",""))}</b> {e(p.get("p",""))}</div>' if isinstance(p, dict) else f'<div class="xp">{e(p)}</div>' for p in x.get('points', []))
        S.append(f'''<div class="s" id="n{k}">{chrome(k,T,e(x.get("lab","Go deeper")),f"Week {W}","Swipe →")}
 <div class="xw"><h2 class="h">{x.get("h","")}</h2><div class="xl">{pts}</div>{f'<div class="src">Source: {e(x["source"])}</div>' if x.get("source") else ''}</div></div>''')
    kM = 4 + len(X)
    mq = ''.join(f'<div class="mc"><div class="st">“{e(m["s"])}”</div><div class="a">{e(m["a"])} — <span>{e(m["why"])}</span></div></div>' for m in spec['mcqs'])
    S.append(f'''<div class="s" id="n{kM}">{chrome(kM,T,"Likely MCQ angles",f"Week {W}","Follow for next Monday's sheet")}
 <div class="mq"><h2 class="h">How UPSC <em>could ask it</em></h2>{mq}</div>
 <div class="cta"><div class="p">{('Every story with its UPSC angle and past questions: <b>minimalistias.com/week</b> — free, link in bio.' if spec.get('page') else 'Read any story in full: <b>the Daily Brief</b> — free, link in bio.')}{(' ' + e(spec['nudge'])) if spec.get('nudge') else ''}</div>
  <div class="pill">Save this · Share with your study group</div></div></div>''')
    page = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>{CSS}</style></head><body>{"".join(S)}</body></html>'
    p = os.path.join(out, 'post.html'); open(p, 'w').write(page)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'cards.py'), p, out, '.s'], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
