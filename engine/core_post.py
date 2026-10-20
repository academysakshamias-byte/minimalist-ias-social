#!/usr/bin/env python3
"""Core 60 — Thursday carousel: one of the Syllabus X-Ray's 60 Prelims Core sub-topics per week ("Aarav asks, Priya explains").
usage: core_post.py spec.json out_dir
spec = {
 "n": 1, "date": "22 Oct 2026",
 "name": "Animals in the news",                 # short title (cover, ≤ 3 lines at 84px)
 "subject": "Environment · Biodiversity",         # label under the title
 "asked": 25, "years": {"2016": 5, ...},          # every year from..to, 0 where none (from the X-Ray data, never estimated)
 "aarav": "bubble ≤ 10 words", "priya": "bubble ≤ 10 words",
 "pattern_h": "html heading with <em>", "pattern_note": "optional one-line takeaway", "pattern": [{"label": "How it behaves", "n": 11, "eg": "waggle dance, tool use"}],  # 2–4 rows, n sums to asked
 "traps": [{"h": "bold line", "p": "one sentence"}] x3,
 "pyqs": [{"y": 2026, "q": 27, "gist": "short paraphrase of the question", "a": "a", "ans": "the answer in words"}] x3 (latest first),
 "read": [{"h": "NCERT Class 12 Biology", "p": "Ch 13 Biodiversity and Conservation"}] (2–3), "skip": "one line",
 "core_total": 60, "core_q": 1064, "core_cov": 51,         # from core_data.py
 "day": "2026-10-22", "prelims": "2027-05-23", "xray_row": {...}, "price": {...}   # xray_row and price straight from core_data.py
}
Slides: 1 cover (duo_explain + bubbles + year bars) · 2 the pattern · 3 three traps · 4 last 3 PYQs · 5 read this first · 6 this sub-topic's real X-Ray row + the one-a-week vs all-today gap + share.
Characters appear on the cover only. The X-Ray row is verbatim product content (exempt from the 45-word count, like a verbatim question).
"""
import json, os, sys, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import LOGO_D, LOGO_L, chrome, pose

CSS = """
.stp{position:absolute;left:96px;top:180px}
.cv-t{position:absolute;left:96px;right:96px;top:262px;height:378px;display:flex;flex-direction:column}
.cv-t .h{font-size:84px}
.cv-t .sb{margin-top:18px;font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.yr{margin-top:auto;height:150px;display:flex;align-items:flex-end;gap:12px}
.yr div{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.yr b{display:block;width:100%;background:var(--gold);border-radius:6px 6px 0 0}
.yr b.z{background:rgba(236,230,216,.18);height:4px!important;border-radius:2px}
.yr span{margin-top:10px;font:600 26px/1 var(--mono);color:var(--muted)}
.yr em{font:600 26px/1 var(--mono);font-style:normal;color:var(--ivory);margin-bottom:8px}
.bub{position:absolute;width:420px;box-sizing:border-box;background:var(--ivory);color:#16130e;border-radius:28px;padding:22px 26px 24px;font:600 32px/1.28 var(--sans);box-shadow:0 18px 40px rgba(0,0,0,.45);z-index:3}
.bub .nm{display:block;font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--p-lab);margin-bottom:10px}
.bub:after{content:"";position:absolute;bottom:-22px;width:0;height:0;border:22px solid transparent;border-top-color:var(--ivory);border-bottom:0}
.bub.a:after{left:300px}.bub.p:after{right:250px}
.ask{position:absolute;left:96px;right:96px;top:1120px;height:88px;border-radius:44px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 32px/1 var(--sans);z-index:3}
.blk{position:absolute;left:96px;right:96px;top:186px}
.blk .h{font-size:68px;margin-bottom:46px}
.pr{margin-bottom:36px}
.pr .top{display:flex;justify-content:space-between;align-items:baseline;font:600 34px/1.2 var(--sans);color:var(--ivory)}
.pr .top b{font:500 italic 52px/1 var(--serif);color:var(--gold)}
.pr .bar{height:14px;border-radius:7px;background:rgba(236,230,216,.12);margin:14px 0 12px;overflow:hidden}.pr .bar i{display:block;height:100%;background:var(--gold);border-radius:7px}
.pr p{margin:0;font:400 30px/1.35 var(--sans);color:var(--muted)}
.note{position:absolute;left:96px;right:96px;bottom:160px;padding:26px 30px;border-left:6px solid var(--gold);background:rgba(242,183,5,.08);font:500 32px/1.4 var(--sans);color:var(--ivory)}
.paper .tr{display:grid;grid-template-columns:84px 1fr;gap:22px;margin-bottom:64px}
.paper .tr i{font:500 italic 76px/0.9 var(--serif);color:#b98a04;font-style:italic}
.paper .tr h3{margin:0 0 14px;font:600 42px/1.22 var(--sans);color:#16130e}
.paper .tr p{margin:0;font:400 36px/1.42 var(--sans);color:#2a261f}
.pq{display:grid;grid-template-columns:120px 1fr;gap:24px;padding:52px 0;border-bottom:2px solid rgba(236,230,216,.14)}
.pq:first-of-type{padding-top:0}
.pq .y{font:600 30px/1.1 var(--mono);color:var(--gold)}.pq .y small{display:block;font-size:26px;color:var(--muted);margin-top:8px}
.pq .g{font:400 35px/1.4 var(--sans);color:var(--ink)}
.pq .r{margin-top:16px;font:600 32px/1.3 var(--sans);color:var(--ivory)}.pq .r b{color:var(--gold);font-family:var(--mono)}
.rd{display:flex;gap:24px;align-items:flex-start;margin-bottom:44px}
.rd .ck:after{content:"✓"}.rd .ck{flex:none;width:52px;height:52px;border-radius:12px;border:3px solid #7f9a7a;display:flex;align-items:center;justify-content:center;color:#7f9a7a;font:700 30px/1 var(--sans)}
.rd h3{margin:2px 0 10px;font:600 38px/1.2 var(--sans);color:#16130e}.rd p{margin:0;font:400 34px/1.42 var(--sans);color:#2a261f}
.sk{margin-top:14px;padding:26px 30px;border-radius:20px;background:rgba(198,113,79,.12);font:400 32px/1.4 var(--sans);color:#2a261f}.sk b{color:#7a3518}
.fr{margin-top:56px;font:500 32px/1.45 var(--sans);color:#2a261f}.fr b{color:#5c4002;white-space:nowrap}
.x6{position:absolute;left:70px;right:70px;top:176px}
.xk{margin-left:26px;margin-bottom:22px;font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
.xr{position:relative;background:#fffaf0;border-radius:22px;padding:30px 34px 32px 38px;border-left:10px solid #b5532f;color:#16130e;box-shadow:0 30px 70px rgba(0,0,0,.5)}
.xr .tp{display:flex;align-items:center;flex-wrap:wrap;gap:10px 16px}
.xr .chip{background:#b5532f;color:#fff;font:600 26px/1 var(--mono);letter-spacing:.08em;padding:8px 14px;border-radius:8px}
.xr .nm{font:600 34px/1.25 var(--sans)}
.xr .pm{border:2px solid #2e5153;color:#2e5153;font:600 26px/1 var(--mono);padding:4px 10px;border-radius:8px}
.xr .cn{font:600 26px/1 var(--mono);color:#b5532f}
.xr .wh{margin-top:18px;font:400 28px/1.42 var(--sans);color:#3d382f}.xr .wh .nc{color:#a8770a;font-weight:600}.xr .wh .ca{color:#2e5153;font-weight:600}.xr .sl{color:#b3ab9b}
.xr .mt{margin-top:22px;display:flex;align-items:center;flex-wrap:wrap;gap:14px 22px}
.xr .st{font:32px/1 var(--sans);color:#a8770a;letter-spacing:-1px}.xr .st .off{color:#ddd5c2}
.xr .qq{font:600 28px/1 var(--mono);color:#3d382f}
.xr .strip{display:flex;gap:5px}.xr .strip i{width:22px;height:34px;border-radius:3px;background:#e9e1cf}.xr .strip i.on{background:#1a1712}
.xr .rv{display:flex;gap:8px}.xr .rv i{width:30px;height:30px;border-radius:50%;border:2.5px solid #b3ab9b}
.xb{margin:64px 26px 0}
.xb .h{font-size:60px}
.xb .pt{margin-top:22px;font:400 32px/1.42 var(--sans);color:var(--ink)}
.xb .url{margin-top:22px;font:600 30px/1.3 var(--sans);color:var(--ivory)}.xb .url b{color:var(--gold)}
.share{position:absolute;left:96px;right:96px;top:1140px;height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 32px/1 var(--sans)}
#n1 .ft span:first-child,#n6 .ft span:first-child{visibility:hidden}
"""

def build(spec, out):
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True); e = html.escape
    N, T = spec['n'], 6; tag = f'Core #{N} of {spec.get("core_total", 60)}'; S = []
    yrs = spec['years']; mx = max(yrs.values()) or 1
    bars = ''.join(f'<div>{f"<em>{v}</em>" if v else ""}<b class="{"" if v else "z"}" style="height:{int(118 * v / mx)}px"></b><span>{y[2:]}</span></div>' for y, v in yrs.items())
    S.append(f'''<div class="s" id="n1">{chrome(1,T,"Core 60",spec['date'],"")}
 <div class="stp"><span class="stamp"><b></b>{tag} · asked {spec['asked']} times</span></div>
 <div class="cv-t"><h1 class="h">{e(spec['name'])}</h1><div class="sb">{e(spec['subject'])} · Prelims GS</div><div class="yr">{bars}</div></div>
 <img class="pose" src="{pose('duo_explain')}" style="left:210px;top:810px;height:640px">
 <div class="bub a" style="left:70px;top:650px"><span class="nm">Aarav</span>{e(spec['aarav'])}</div>
 <div class="bub p" style="right:70px;top:690px"><span class="nm">Priya</span>{e(spec['priya'])}</div>
 <div class="fade" style="top:1060px;height:290px"></div>
 <div class="ask">Swipe: the pattern behind {spec['asked']} questions →</div></div>''')
    tot = sum(r['n'] for r in spec['pattern']) or 1
    rows = ''.join(f'<div class="pr"><div class="top"><span>{e(r["label"])}</span><b>{r["n"]}</b></div><div class="bar"><i style="width:{100 * r["n"] / tot:.0f}%"></i></div><p>{e(r["eg"])}</p></div>' for r in spec['pattern'])
    S.append(f'''<div class="s" id="n2">{chrome(2,T,"The pattern",tag,f"All {spec['asked']} questions, sorted")}
 <div class="blk"><h2 class="h">{spec['pattern_h']}</h2>{rows}</div>{f'<div class="note">{e(spec["pattern_note"])}</div>' if spec.get('pattern_note') else ''}</div>''')
    tr = ''.join(f'<div class="tr"><i>{i + 1}</i><div><h3>{e(t["h"])}</h3><p>{e(t["p"])}</p></div></div>' for i, t in enumerate(spec['traps']))
    S.append(f'''<div class="s paper" id="n3">{chrome(3,T,"3 traps",tag,"Screenshot this",True)}
 <div class="blk"><h2 class="h">UPSC's <em>traps</em></h2>{tr}</div></div>''')
    pq = ''.join(f'<div class="pq"><div class="y">{p["y"]}<small>Q{p["q"]}</small></div><div><div class="g">{e(p["gist"])}</div><div class="r">Answer <b>({p["a"]})</b> {e(p["ans"])}</div></div></div>' for p in spec['pyqs'])
    S.append(f'''<div class="s" id="n4">{chrome(4,T,"Last 3 PYQs",tag,"Asked in UPSC Prelims")}
 <div class="blk"><h2 class="h">The <em>latest</em> three</h2>{pq}</div></div>''')
    rd = ''.join(f'<div class="rd"><div class="ck"></div><div><h3>{e(r["h"])}</h3><p>{e(r["p"])}</p></div></div>' for r in spec['read'])
    S.append(f'''<div class="s paper" id="n5">{chrome(5,T,"Read this first",tag,"Save for revision",True)}
 <div class="blk"><h2 class="h">Read <em>this first</em></h2>{rd}<div class="sk"><b>Skip:</b> {e(spec['skip'])}</div>
 <div class="fr">All {spec["asked"]} questions, explained, free:<br><b>minimalistias.com/upsc-syllabus/prelims</b></div></div></div>''')
    # 6 — this sub-topic's real X-Ray row (verbatim, from planner/catalog.json + sources.json via core_data.py),
    # then the honest gap: one row a week here vs all of them in the X-Ray today. No outcome claims.
    import datetime as dt
    X = spec['xray_row']; pr = spec['price']
    day = dt.date.fromisoformat(spec['day']); exam = dt.date.fromisoformat(spec.get('prelims', '2027-05-23'))
    reach = min(spec.get('core_total', 60), N + max(0, (exam - day).days // 7))
    yset = set(X['yrs']); cells = ''.join(f'<i class="{"on" if y in yset else ""}"></i>' for y in range(2016, 2027))
    where = ' <span class="sl">/</span> '.join(
        (f'<b class="nc">{e(w["t"].split(" ", 2)[0] + " " + w["t"].split(" ", 2)[1])}</b> {e(w["t"].split(" ", 2)[2])}' if w.get('nc')
         else f'<b class="ca">Current affairs:</b>{e(w["t"].split(":", 1)[1])}' if w.get('ca') else e(w['t'])) for w in X['where'])
    stars = '★' * X['stars'] + f'<span class="off">{"★" * (5 - X["stars"])}</span>'
    launch = day <= dt.date.fromisoformat(pr['launch_ends'])
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    le = dt.date.fromisoformat(pr['launch_ends'])
    price = f'₹{pr["launch"]} till {le.day} {months[le.month-1]}, then ₹{pr["regular"]}' if launch else f'₹{pr["regular"]}'
    S.append(f'''<div class="s" id="n6">{chrome(6,T,"The X-Ray",spec['date'],"")}
 <div class="x6"><div class="xk">In the X-Ray</div>
 <div class="xr verbatim"><div class="tp"><span class="chip">CORE</span><span class="nm">{e(X['name'])}</span>{'<span class="pm">P+M</span>' if X['pm'] else ''}<span class="cn">Core #{N}</span></div>
  <div class="wh">{where}</div>
  <div class="mt"><span class="st">{stars}</span><span class="qq">{X['q']} Q · {X['weight']}%</span><span class="strip">{cells}</span><span class="rv"><i></i><i></i><i></i></span></div></div>
 <div class="xb"><h2 class="h">One a week here. <em>All 60 today.</em></h2>
  <p class="pt">At one a week, this series reaches Core #{reach} by Prelims ({exam.day} {months[exam.month-1]} {exam.year}). The X-Ray ranks all 928 sub-topics now.</p>
  <div class="url">{price} · <b>minimalistias.com/syllabus-x-ray</b></div></div></div>
 <div class="share">Send to a study partner ↗</div></div>''')
    page = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>{CSS}</style></head><body>{"".join(S)}</body></html>'
    p = os.path.join(out, 'post.html'); open(p, 'w').write(page)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'cards.py'), p, out, '.s'], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    return p

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
