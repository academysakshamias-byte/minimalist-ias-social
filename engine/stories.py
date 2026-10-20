#!/usr/bin/env python3
"""Daily stories (native 9:16, 1080×1920). Instagram's UI covers the top ~250 px and the bottom ~260 px: nothing lives there.
usage: stories.py brief spec.json out.jpg   spec = {"date": "20 Oct 2026", "picks": [{"gs": "GS2", "title": "…", "why": "…"}] x3}
       stories.py split spec.json out.jpg   spec = {"date": "19 Oct 2026", "tag": "Prelims 2022 · Q90", "votes": {"a": 12, "b": 30, "c": 5, "d": 3},
                                                     "answer": "a", "answer_text": "Ant"}   # votes = real comment counts, one per person
       stories.py evaluate {} out.jpg       (Saturday: free Mains answer evaluation)
Text comes from fact-checked sources (the published Brief, UPSC's key, real comment counts); nothing is invented.
"""
import json, os, sys, html, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import LOGO_D, pose

BASE = """body{margin:0}#st{width:1080px;height:1920px;position:relative;overflow:hidden;background:#13110d;color:var(--ink);font-family:var(--sans)}
#st .g{position:absolute;inset:0;background:radial-gradient(1200px 900px at 100% 0%,rgba(242,183,5,.16),transparent 60%),radial-gradient(900px 700px at 0% 100%,rgba(242,183,5,.07),transparent 60%)}
.top{position:absolute;left:84px;right:84px;top:262px;display:flex;align-items:center;gap:16px;font:600 30px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.top svg{width:46px;height:46px}.top .d{margin-left:auto;color:var(--muted)}
.h{position:absolute;left:84px;right:84px;top:340px;margin:0;font:500 84px/1.05 var(--serif);color:var(--ivory)}.h em{font-style:italic;color:var(--gold)}
.bar{position:absolute;left:84px;right:84px;top:1560px;height:100px;border-radius:50px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 36px/1 var(--sans);text-align:center;z-index:3}
.clip{position:absolute;left:0;right:0;top:0;height:1600px;overflow:hidden;z-index:1;-webkit-mask-image:linear-gradient(#000 88%,transparent);mask-image:linear-gradient(#000 88%,transparent)}  /* characters end at the bar */
"""

def render(body, css, out):
    page = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>{BASE}{css}</style></head><body><div id="st"><div class="g"></div>{body}</div></body></html>'
    td = tempfile.mkdtemp(prefix='stories-'); hp = os.path.join(td, 's.html'); png = os.path.join(td, 's.png'); open(hp, 'w').write(page)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + hp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        rep = pg.evaluate("""() => { let m = 999, off = []; const R = document.querySelector('#st').getBoundingClientRect();
          const tw = document.createTreeWalker(document.querySelector('#st'), NodeFilter.SHOW_TEXT);
          while (tw.nextNode()) { const n = tw.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement;
            m = Math.min(m, parseFloat(getComputedStyle(el).fontSize)); const rg = document.createRange(); rg.selectNodeContents(n);
            for (const r of rg.getClientRects()) { const y0 = r.top - R.top, y1 = r.bottom - R.top, x0 = r.left - R.left, x1 = r.right - R.left;
              if (y0 < 250 || y1 > 1660 || x0 < 60 || x1 > 1020) off.push(n.textContent.trim().slice(0, 30)); } }
          return {minFs: m, unsafe: [...new Set(off)]}; }""")
        pg.query_selector('#st').screenshot(path=png); b.close()
    from PIL import Image
    Image.open(png).convert('RGB').save(out, 'JPEG', quality=92)
    print(json.dumps({'out': out, **rep}))
    return rep

def brief(spec, out):
    e = html.escape
    cards = ''.join(f'''<div class="c"><div class="n">{i + 1}</div><div><div class="gs">{e(p['gs'])}</div><h3>{e(p['title'])}</h3><p>{e(p['why'])}</p></div></div>''' for i, p in enumerate(spec['picks'][:3]))
    css = """.cs{position:absolute;left:84px;right:84px;top:580px;display:flex;flex-direction:column;gap:34px;z-index:3}
.c{display:grid;grid-template-columns:70px 1fr;gap:22px;background:rgba(250,247,240,.06);border:2px solid rgba(242,183,5,.3);border-radius:24px;padding:28px 30px}
.c .n{font:500 italic 64px/0.9 var(--serif);color:var(--gold)}
.c .gs{font:600 26px/1 var(--mono);letter-spacing:.14em;color:var(--gold);margin-bottom:10px}
.c h3{margin:0 0 12px;font:600 38px/1.22 var(--sans);color:var(--ivory)}
.c p{margin:0;font:400 31px/1.4 var(--sans);color:var(--muted)}
.pose{position:absolute;right:-60px;top:1180px;height:700px;opacity:.95;z-index:1}"""
    body = f'''<div class="top">{LOGO_D}<span>Today's Brief</span><span class="d">{e(spec['date'])}</span></div>
<h1 class="h">3 stories to <em>know today</em></h1><div class="cs">{cards}</div>
<div class="bar">All of today's Brief, free · link in bio</div>'''
    return render(body, css, out)

def split(spec, out):
    e = html.escape; v = spec['votes']; tot = sum(v.values()) or 1; A = spec['answer']
    right = round(100 * v.get(A, 0) / tot)
    rows = ''.join(f'''<div class="r{' ok' if k == A else ''}"><span class="k">{k}</span><span class="b"><i style="width:{100 * v.get(k, 0) / tot:.0f}%"></i></span><span class="p">{round(100 * v.get(k, 0) / tot)}%</span></div>''' for k in 'abcd')
    css = """.sub{position:absolute;left:84px;right:84px;top:540px;font:500 34px/1.35 var(--sans);color:var(--muted)}
.rs{position:absolute;left:84px;right:84px;top:660px;display:flex;flex-direction:column;gap:30px}
.r{display:grid;grid-template-columns:80px 1fr 130px;gap:22px;align-items:center}
.r .k{width:72px;height:72px;border-radius:50%;border:3px solid var(--muted);display:flex;align-items:center;justify-content:center;font:600 34px/1 var(--mono);color:var(--muted)}
.r .b{height:56px;border-radius:12px;background:rgba(236,230,216,.1);overflow:hidden}.r .b i{display:block;height:100%;background:rgba(236,230,216,.35);border-radius:12px}
.r .p{font:600 40px/1 var(--mono);color:var(--muted);text-align:right}
.r.ok .k{border-color:var(--gold);color:#13110d;background:var(--gold)}.r.ok .b i{background:var(--gold)}.r.ok .p{color:var(--gold)}
.ans{position:absolute;left:84px;right:84px;top:1130px;font:500 46px/1.25 var(--serif);color:var(--ivory)}.ans em{font-style:italic;color:var(--gold)}
.pose{position:absolute;right:-40px;top:1240px;height:620px;z-index:1}"""
    sub = f"{tot} of you answered yesterday's PYQ ({e(spec['tag'])})"
    pz = 'priya_clap' if right >= 50 else 'priya_surprised'
    body = f'''<div class="top">{LOGO_D}<span>Yesterday's PYQ</span><span class="d">{e(spec['date'])}</span></div>
<h1 class="h">{right}% of you <em>got it right.</em></h1><div class="sub">{sub}</div><div class="rs">{rows}</div>
<div class="ans">Answer: <em>({A}) {e(spec.get('answer_text', ''))}</em></div>
<div class="clip"><img class="pose" src="{pose(pz)}"></div>
<div class="bar">Every option explained · link in bio</div>'''
    return render(body, css, out)

def evaluate(spec, out):
    css = """.sub{position:absolute;left:84px;right:84px;top:600px;font:400 38px/1.4 var(--sans);color:var(--ink)}.sub b{color:var(--ivory)}
.pose{position:absolute;left:50%;transform:translateX(-50%);top:860px;height:820px;z-index:1}"""
    body = f'''<div class="top">{LOGO_D}<span>Saturday · Mains</span></div>
<h1 class="h">Wrote an answer <em>this week?</em></h1>
<div class="sub">Get it evaluated by your mentor: a score, and the one change that lifts your marks most. <b>5 answers free</b> with a free sign-up.</div>
<div class="clip"><img class="pose" src="{pose('aarav_answersheet')}"></div>
<div class="bar">Free answer evaluation · link in bio</div>'''
    return render(body, css, out)

if __name__ == '__main__':
    kind, sp, out = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = json.load(open(sp)) if sp not in ('{}', '-') else {}
    {'brief': brief, 'split': split, 'evaluate': evaluate}[kind](spec, out)
