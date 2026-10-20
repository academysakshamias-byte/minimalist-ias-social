#!/usr/bin/env python3
"""1-page PYQ revision sheet (1080×1920, reads full-screen on a phone) — the thing students get by DM when they comment
the reel's keyword ("Comment CONGO → we DM you the sheet"). Built only from the reviewed reel spec (no new claims):
question + options with the key marked, why each option, the trap, the method, the one line to remember, and
spec.extra[0] points ("Also know") when present, plus the source and the permanent explanation link.
usage: sheet.py spec.json out.jpg        (also called by pyq_reel.py → <out_dir>/sheet.jpg)
Prints {"minFs":…, "overflow":…}; minFs must be ≥ 26 and overflow false.
"""
import json, os, re, sys, html, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pyq_post import LOGO_D

FONTS = os.path.join(ROOT, 'brand', 'fonts')
CSS = """
@font-face{font-family:"Newsreader";font-weight:500;src:url(F/newsreader-latin-500-normal.woff2)}
@font-face{font-family:"Newsreader";font-weight:500;font-style:italic;src:url(F/newsreader-latin-500-italic.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:400;src:url(F/ibm-plex-sans-latin-400-normal.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:600;src:url(F/ibm-plex-sans-latin-600-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:600;src:url(F/ibm-plex-mono-latin-600-normal.woff2)}
*{box-sizing:border-box}html,body{margin:0}
#sh{width:1080px;height:1920px;position:relative;overflow:hidden;background:#f3eee3;color:#16130e;font-family:"IBM Plex Sans",sans-serif;--s:1}
.top{height:170px;background:#13110d;color:#f2b705;display:flex;align-items:center;gap:20px;padding:0 64px;font:600 28px/1 "IBM Plex Mono";letter-spacing:.14em;text-transform:uppercase}
.top svg{width:56px;height:56px}.top .r{margin-left:auto;color:#cfc6b3}
#body{position:absolute;left:64px;right:64px;top:205px;bottom:190px;overflow:hidden}
#in{font-size:calc(34px*var(--s))}
h1{margin:0 0 .5em;font:500 calc(60px*var(--s))/1.12 Newsreader,serif}h1 em{font-style:italic;color:#8a6200}
.q{margin:0 0 .55em;font:400 1em/1.38 "IBM Plex Sans"}
.op{display:flex;gap:.5em;align-items:flex-start;margin:0 0 .3em;font:400 1em/1.3 "IBM Plex Sans";padding:.18em .35em;border-radius:10px}
.op i{flex:none;width:1.5em;height:1.5em;border-radius:50%;border:2px solid #16130e;font:600 max(26px,.86em)/1 "IBM Plex Mono";display:flex;align-items:center;justify-content:center;font-style:normal;margin-top:.02em}
.op.ok{background:#f2b705}.op.ok i{background:#16130e;color:#f2b705}
.lab{margin:.95em 0 .35em;font:600 max(26px,calc(29px*var(--s)))/1 "IBM Plex Mono";letter-spacing:.14em;text-transform:uppercase;color:#7a5402}
.lab:first-child{margin-top:0}
.v{margin:0 0 .35em;font:400 1em/1.34 "IBM Plex Sans"}.v b{font-weight:600}
.box{border-radius:18px;padding:.55em .7em;margin:.2em 0 0;font:400 1em/1.36 "IBM Plex Sans"}
.trap{background:#f7dcd2}.meth{background:#e3eadf}
.rem{background:#13110d;color:#faf7f0;font:500 calc(44px*var(--s))/1.2 Newsreader,serif}.rem em{color:#f2b705;font-style:italic}
.pt{margin:0 0 .3em;font:400 1em/1.34 "IBM Plex Sans"}.pt b{font-weight:600;color:#7a5402}
.ft{position:absolute;left:64px;right:64px;bottom:60px;font:400 26px/1.4 "IBM Plex Sans";color:#4a453b}
.ft .u{display:block;font:600 34px/1.3 "IBM Plex Sans";color:#16130e;margin-top:6px}
"""

def build_html(spec):
    nb = lambda x: re.sub(r'(\d)([–-])(\d)', '\\1\u2060\\2\u2060\\3', x)   # keep 2026–27 on one line
    e = lambda x: nb(html.escape(x)); q = spec['q']; t = q['t']; key = q['a']
    opts = ''.join(f'<div class="op{" ok" if k == key else ""}"><i>{k}</i><span>{e(v)}</span></div>' for k, v in t['options'].items())
    items = ''.join(f'<p class="v">{e(k)}. {e(v)}</p>' for k, v in t.get('items', []))
    prompt = ''.join(f'<p class="q"><b>{e(s)}</b></p>' for s in t.get('prompt', []))
    vds = ''.join(f'<p class="v"><b>{"✓" if v["ok"] else "✗"} {e(v["h"])}</b> — {e(v["p"])}</p>' for v in spec['verdicts'][:4])
    ex = (spec.get('extra') or [None])[0]
    also = ''
    if ex and ex.get('points'):
        also = '<div class="lab">Also know</div>' + ''.join(
            f'<p class="pt">{"<b>" + e(p["h"]) + "</b> " + e(p["p"]) if isinstance(p, dict) else e(p)}</p>' for p in ex['points'][:(3 if (spec.get('bonus') or {}).get('short') else 4)])
    link = f"minimalistias.com/pyqs/prelims/{q['y']}/q{q['n']}"
    bm = re.match(r'^pre-(\d{4})-0*(\d{1,3})$', str((spec.get('bonus') or {}).get('id', '')))
    if bm and spec['bonus'].get('short'):
        also += (f'<div class="lab">Try this next · UPSC {bm.group(1)}</div><p class="pt">{e(spec["bonus"]["short"])} '
                 f'<b>minimalistias.com/pyqs/prelims/{bm.group(1)}/q{int(bm.group(2))}</b></p>')
    srcs = e(spec['source'] + ((' · ' + ex['source']) if ex and ex.get('source') and ex['source'] not in spec['source'] else ''))
    body = f'''<div class="top">{LOGO_D}<span>PYQ revision sheet</span><span class="r">Prelims {q["y"]} · Q{q["n"]}</span></div>
<div id="body"><div id="in">
<h1>{spec['answer_head']}</h1>
<div class="lab">The question</div><p class="q">{e(' '.join(t['stem']))}</p>{items}{prompt}{opts}
<div class="lab">Why each option</div>{vds}
<div class="lab">The trap</div><div class="box trap">{e(spec['trap'])}</div>
<div class="lab">Method</div><div class="box meth">{e(spec['method'])}</div>
<div class="lab">Remember</div><div class="box rem">{spec['remember']}</div>
{also}
</div></div>
<div class="ft">Sources: {srcs}<span class="u">Every option explained: {link}</span></div>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace("url(F/", "url(file://" + FONTS + "/")}</style></head><body><div id="sh">{body}</div></body></html>'

def lighter(spec):
    """Same sheet with less optional content, for long questions: fewer "Also know" points first, then no bonus.
    The question, verdicts, trap, method and remember are never cut."""
    ex = (spec.get('extra') or [None])[0]
    if ex and ex.get('points'):
        return {**spec, 'extra': [{**ex, 'points': ex['points'][:len(ex['points'][:4]) - 1]}] + (spec.get('extra') or [])[1:]}
    if (spec.get('bonus') or {}).get('short'):
        return {**spec, 'bonus': {}}
    return None

def render(spec, out):
    from playwright.sync_api import sync_playwright
    td = tempfile.mkdtemp(prefix='sheet-'); hp = os.path.join(td, 's.html'); png = os.path.join(td, 's.png')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        while True:
            open(hp, 'w').write(build_html(spec))
            pg.goto('file://' + hp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            rep = pg.evaluate(MEASURE)
            nxt = lighter(spec) if rep['overflow'] else None
            if not nxt: break
            spec = nxt
        rep['trimmed'] = {'also': len(((spec.get('extra') or [{}])[0] or {}).get('points') or []), 'bonus': bool((spec.get('bonus') or {}).get('short'))}
        pg.query_selector('#sh').screenshot(path=png); b.close()
    from PIL import Image
    Image.open(png).convert('RGB').save(out, 'JPEG', quality=90)
    print(json.dumps({'sheet': out, **rep}))
    return rep

MEASURE = """() => { const sh = document.querySelector('#sh'), body = document.querySelector('#body'), inn = document.querySelector('#in');
          let s = 1.12; sh.style.setProperty('--s', s);
          while (inn.scrollHeight > body.clientHeight && s > 0.77) { s -= 0.01; sh.style.setProperty('--s', s.toFixed(2)); }
          let m = 999; const tw = document.createTreeWalker(sh, NodeFilter.SHOW_TEXT);
          while (tw.nextNode()) { if (tw.currentNode.textContent.trim()) m = Math.min(m, parseFloat(getComputedStyle(tw.currentNode.parentElement).fontSize)); }
          return {scale: +s.toFixed(2), minFs: Math.round(m * 10) / 10, overflow: inn.scrollHeight > body.clientHeight}; }"""

if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2])
