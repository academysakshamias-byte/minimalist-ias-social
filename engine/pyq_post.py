#!/usr/bin/env python3
"""PYQ of the Day — 5-slide carousel with Aarav & Priya.
usage: pyq_post.py spec.json out_dir
spec = {
 "no": 1, "date": "20 Oct 2026",
 "q": {prelims.json entry: id,y,n,a,t{stem,items,prompt,options}},
 "hook": "html with <em>", "hook_sub": "...",
 "aarav": {"pick":"a","line":"...","pose":"aarav_confident"},
 "priya": {"pick":"c","line":"...","pose":"priya_thinking"},
 "answer_head": "html", "verdicts": [{"ok":true,"h":"...","p":"..."}], "source": "...",
 "remember": "html", "trap": "...", "method": "...", "why_now": "optional one line",
 "utm": "pyq-of-the-day"
}"""
import json, os, sys, html, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
POSES = os.path.join(HERE, '..', 'poses', 'cut')
sys.path.insert(0, HERE)

LOGO_D = '<svg viewBox="0 0 120 120"><polygon points="60,10 92,64 28,64" fill="#f2b705"/><polygon points="60,110 92,64 28,64" fill="#faf7f0" opacity=".92"/><circle cx="60" cy="64" r="11" fill="#0a0a0c" stroke="#f2b705" stroke-width="4.5"/></svg>'
LOGO_L = '<svg viewBox="0 0 120 120"><polygon points="60,10 92,64 28,64" fill="#d9a441"/><polygon points="60,110 92,64 28,64" fill="#16130e"/><circle cx="60" cy="64" r="11" fill="#f3eee3" stroke="#b98a04" stroke-width="4.5"/></svg>'
TICK = '<svg width="28" height="28" viewBox="0 0 28 28"><path d="M5 15l6 6L23 7" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M5 5l16 16M21 5L5 21" stroke="#fff" stroke-width="4" stroke-linecap="round"/></svg>'

def pose(name): return 'file://' + os.path.abspath(os.path.join(POSES, name + '.png'))
def chrome(i, total, left, right, foot, paper=False):
    lg = LOGO_L if paper else LOGO_D
    prog = ''.join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(1, total + 1))
    return (f'<div class="tex"></div><div class="hd"><div class="l">{lg}{left}</div><div class="r">{right}</div></div><div class="rule"></div>'
            f'<div class="ft"><span>{foot}</span><span class="go">{i} / {total}</span></div><div class="prog">{prog}</div>')

CSS = """
/* cover */
.cv-hook{position:absolute;left:96px;right:96px;top:282px}
.cv-hook .h{font-size:76px}
.who{position:absolute;bottom:0;}
.bub{position:absolute;top:0;width:410px;background:var(--ivory);color:#16130e;border-radius:28px;padding:24px 28px 26px;font:600 32px/1.28 var(--sans);box-shadow:0 18px 40px rgba(0,0,0,.45)}
.bub .nm{display:block;font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--p-lab);margin-bottom:12px}
.bub:after{content:"";position:absolute;bottom:-22px;width:0;height:0;border:22px solid transparent;border-top-color:var(--ivory);border-bottom:0}
.bub.a:after{left:120px}.bub.p:after{right:120px}
.bub .pk{display:inline-block;margin-left:6px;color:#7a5402;font-style:italic;font-family:var(--serif);font-weight:600}
.ask{position:absolute;left:96px;right:96px;top:1110px;height:92px;border-radius:46px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 34px/1 var(--sans)}
/* question */
.qw{position:absolute;left:96px;right:96px;top:196px}
.qw .stem{font:500 60px/1.2 var(--serif);color:#16130e;margin:40px 0 64px}
.qw.short .op{font-size:42px;margin-bottom:40px}.qw.short .op i{width:70px;height:70px;font-size:32px;line-height:66px}
.qw .stem.long{font:400 33px/1.42 var(--sans)}
.qw .it{font:400 32px/1.42 var(--sans);margin:0 0 18px;padding-left:30px;border-left:5px solid #d9a441}
.qw .pr{font:600 32px/1.35 var(--sans);margin:22px 0 30px}
.op{display:flex;gap:22px;align-items:center;margin-bottom:26px;font:400 34px/1.3 var(--sans);color:#1a1712}
.op i{flex:none;width:58px;height:58px;border-radius:50%;border:2px solid #1a1712;font:600 28px/54px var(--mono);text-align:center;font-style:normal}
/* answer */
.ans{position:absolute;left:96px;right:96px;top:186px;display:flex;align-items:center;gap:44px}
.disc{flex:none;width:210px;height:210px;border-radius:50%;border:3px solid var(--gold);display:flex;align-items:center;justify-content:center;font:500 italic 150px/1 var(--serif);color:var(--gold);padding-bottom:22px;box-sizing:border-box}
.ans .t{font:500 56px/1.15 var(--serif);color:var(--ivory)}.ans .t em{color:var(--gold)}
.vds{position:absolute;left:96px;right:96px;top:470px}
.vrow{display:flex;gap:26px;align-items:flex-start;margin-bottom:40px}
.ic{flex:none;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.ic.no{background:#c6714f}.ic.yes{background:#7f9a7a}
.vrow h3{margin:4px 0 10px;font:600 36px/1.2 var(--sans);color:var(--ivory)}
.vrow p{margin:0;font:400 32px/1.42 var(--sans);color:var(--ink)}
.src{position:absolute;left:96px;right:96px;bottom:150px;font:500 26px/1.35 var(--sans);color:var(--muted)}
/* revision card */
.card{position:absolute;left:96px;right:96px;top:176px;height:900px;background:#f3eee3;border-radius:26px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.55)}
.card .band{height:12px;background:var(--gold)}
.card .in{position:absolute;left:62px;right:62px;top:62px;bottom:56px}
.card .lab{color:var(--p-lab)}
.card .big{margin:26px 0 0;font:500 50px/1.2 var(--serif);color:#16130e}.card .big em{font-style:italic;color:var(--p-acc)}
.card .ln{height:2px;background:rgba(26,23,18,.14);margin:36px 0 30px}
.card .k{font:600 26px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;margin-bottom:14px}
.card .k.tr{color:#7a3518}.card .k.me{color:#2e5153}
.card p{margin:0;font:400 32px/1.42 var(--sans);color:#1a1712}
.card .narrow{padding-right:250px}
.card .mk{position:absolute;left:0;bottom:0;display:flex;align-items:center;gap:12px;font:600 26px/1 var(--mono);letter-spacing:.06em;color:#4a453b}
.card .mk svg{width:34px;height:34px}
.card .cpose{position:absolute;right:20px;bottom:0;height:390px}
.save{position:absolute;left:96px;right:96px;top:1118px;text-align:center;font:500 32px/1.3 var(--sans);color:var(--ink)}.save b{color:var(--gold);font-weight:600}
/* cta */
.cta-l{position:absolute;left:0;bottom:0;height:940px}
#n5 .ft span:first-child,#n1 .ft span:first-child{visibility:hidden}
.cta-r{position:absolute;left:500px;right:70px;top:210px}
.cta-r .h{font-size:64px}
.cta-r .url{margin-top:30px;font:600 32px/1.3 var(--sans);color:var(--gold);white-space:nowrap}
.cta-r .pt{margin-top:34px;font:400 32px/1.42 var(--sans);color:var(--ink)}
.cta-r .pt b{color:var(--ivory)}
.share{position:absolute;left:500px;right:70px;top:1030px;height:96px;border-radius:48px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 32px/1 var(--sans)}
.now{position:absolute;left:96px;right:96px;top:170px;font:500 28px/1.35 var(--sans);color:var(--muted)}
"""

def build(spec, out):
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True)
    q = spec['q']; t = q['t']; Y, N = q['y'], q['n']; tag = f'Prelims {Y} · Q{N}'
    T = 5; A, P = spec['aarav'], spec['priya']
    e = html.escape
    S = []
    # 1 cover
    S.append(f'''<div class="s" id="n1">{chrome(1,T,f"PYQ of the Day · No. {spec['no']}",spec['date'],"Swipe for the answer →")}
 <div style="position:absolute;left:96px;top:186px"><span class="stamp"><b></b>UPSC {tag}</span></div>
 <div class="cv-hook"><h1 class="h">{spec['hook']}</h1></div>
 <img class="pose" src="{pose(A['pose'])}" style="left:-30px;top:610px;height:700px">
 <img class="pose" src="{pose(P['pose'])}" style="right:-20px;top:640px;height:670px">
 <div class="fade" style="top:1010px;height:340px"></div>
 <div class="bub a" style="left:70px;top:470px"><span class="nm">Aarav</span>{e(A['line'])}<span class="pk">({A['pick']})</span></div>
 <div class="bub p" style="right:70px;top:500px"><span class="nm">Priya</span>{e(P['line'])}<span class="pk">({P['pick']})</span></div>
 <div class="ask">Who's right? Comment a, b, c or d</div></div>''')
    # 2 question
    stem = ' '.join(t.get('stem') or [])
    longq = len(stem) > 140 or t.get('items')
    items = ''.join(f'<p class="it">{e(x if isinstance(x,str) else x.get("text",""))}</p>' for x in (t.get('items') or []))
    prompt = ' '.join(t.get('prompt') or [])
    ops = ''.join(f'<div class="op"><i>{k}</i><span>{e(v)}</span></div>' for k, v in t['options'].items())
    S.append(f'''<div class="s paper" id="n2">{chrome(2,T,"The question",tag,"Lock your answer, then swipe",True)}
 <div class="qw{'' if longq else ' short'}"><p class="stem{' long' if longq else ''}">{e(stem)}</p>{items}{f'<p class="pr">{e(prompt)}</p>' if prompt else ''}{ops}</div></div>''')
    # 3 answer
    vd = ''.join(f'<div class="vrow"><div class="ic {"yes" if v["ok"] else "no"}">{TICK if v["ok"] else CROSS}</div><div style="flex:1"><h3>{e(v["h"])}</h3><p>{e(v["p"])}</p></div></div>' for v in spec['verdicts'])
    S.append(f'''<div class="s" id="n3">{chrome(3,T,"Answer",tag,"Got it right? Comment ✓")}
 <div class="ans"><div class="disc">{q['a']}</div><div class="t">{spec['answer_head']}</div></div>
 <div class="vds">{vd}</div><div class="src">Source: {e(spec['source'])}</div></div>''')
    # 4 revision card
    fell = spec.get('trap_who')  # 'aarav' | 'priya' | None
    who_pose = {'aarav': 'aarav_oops', 'priya': 'priya_surprised'}.get(fell)
    trap_lab = {'aarav': "Aarav's trap", 'priya': "Priya's slip"}.get(fell, 'The trap')
    S.append(f'''<div class="s" id="n4">{chrome(4,T,"Revision card","Screenshot this",tag)}
 <div class="card"><div class="band"></div><div class="in">
  <div class="lab">Remember</div><p class="big">{spec['remember']}</p>
  <div class="ln"></div>
  <div class="k tr">{trap_lab}</div><p class="{'narrow' if who_pose else ''}">{e(spec['trap'])}</p>
  <div class="ln" style="margin:30px 0 26px{';margin-right:250px' if who_pose else ''}"></div>
  <div class="k me">The method</div><p class="{'narrow' if who_pose else ''}">{e(spec['method'])}</p>
  <div class="mk">{LOGO_L}MINIMALIST IAS</div>
 </div>{f'<img class="cpose" src="{pose(who_pose)}">' if who_pose else ''}</div>
 <div class="save">Save the post — <b>this card is your revision.</b></div></div>''')
    # 5 CTA — phone shows the real explanation page
    phone = os.path.join(out, 'phone.png'); phone_screen(spec, os.path.join(out, 'screen.png'))
    import props; props.compose('priya_phone', os.path.join(out, 'screen.png'), phone)
    now = f'<div class="now">{e(spec["why_now"])}</div>' if spec.get('why_now') else ''
    S.append(f'''<div class="s" id="n5">{chrome(5,T,"Go deeper",spec['date'],"Follow for tomorrow's PYQ")}
 <img class="pose cta-l" src="file://{os.path.abspath(phone)}">
 <div class="cta-r"><h2 class="h">The full <em>explanation</em> is free.</h2>
  <div class="url">minimalistias.com/pyq-today</div>
  <p class="pt">Every option explained, with sources — plus <b>1,100 Prelims PYQs</b> from 2016 to 2026.</p>
  <p class="pt">Comment <b>PYQ</b> and we'll reply with the link.</p></div>
 <div class="share">Send to a study partner ↗</div></div>''')
    page = f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>{CSS}</style></head><body>{"".join(S)}</body></html>'
    p = os.path.join(out, 'post.html'); open(p, 'w').write(page)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'cards.py'), p, out, '.s'], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    return p

def phone_screen(spec, path):
    q = spec['q']; t = q['t']; e = html.escape
    stem = ' '.join(t.get('stem') or [])
    opts = ''.join(f'<div style="display:flex;gap:10px;margin:8px 0;font:500 17px/1.3 IBM Plex Sans;color:{"#13110d" if k==q["a"] else "#3d382f"};{"background:#f2e2a8;border-radius:8px;padding:6px 8px;margin-left:-8px" if k==q["a"] else ""}"><b style="font-family:IBM Plex Mono">{k}</b>{e(v)}{" ✓" if k==q["a"] else ""}</div>' for k, v in t['options'].items())
    h = f'''<html><head><link rel="stylesheet" href="file://{HERE}/brand.css"></head><body style="margin:0">
<div id="ph" style="width:420px;height:900px;background:#f6f2ea;overflow:hidden;font-family:IBM Plex Sans">
<div style="background:#13110d;padding:26px 22px 20px;display:flex;align-items:center;gap:10px"><span style="width:30px;height:30px;display:inline-block">{LOGO_D}</span><span style="font:600 14px IBM Plex Mono;letter-spacing:.16em;color:#f2b705">MINIMALIST IAS</span></div>
<div style="padding:22px">
<div style="font:600 13px IBM Plex Mono;letter-spacing:.14em;color:#5c4002">PYQ OF THE DAY · PRELIMS {q['y']} · Q{q['n']}</div>
<div style="font:500 26px/1.25 Newsreader;color:#16130e;margin:12px 0 14px">{e(stem[:150])}</div>{opts}
<div style="margin-top:18px;border-top:2px solid #e2d9c6;padding-top:16px;font:600 13px IBM Plex Mono;letter-spacing:.14em;color:#5c4002">EXPLANATION</div>
<div style="font:400 16px/1.45 IBM Plex Sans;color:#2a261f;margin-top:8px">{e(q.get('ex',{}).get('summary','')[:260])}</div>
<div style="margin-top:16px;font:600 13px IBM Plex Mono;letter-spacing:.14em;color:#5c4002">SOURCES · SIMILAR PYQS</div>
<div style="height:10px;background:#e2d9c6;border-radius:5px;margin:12px 0 8px;width:90%"></div><div style="height:10px;background:#e2d9c6;border-radius:5px;width:70%"></div>
</div></div></body></html>'''
    hp = path.replace('.png', '.html'); open(hp, 'w').write(h)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(device_scale_factor=2); pg.goto('file://' + hp); pg.wait_for_timeout(500)
        pg.query_selector('#ph').screenshot(path=path); b.close()

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
