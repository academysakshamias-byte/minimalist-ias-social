#!/usr/bin/env python3
"""1-page Core 60 revision sheet (1080×1920, reads full-screen on a phone): what students get by DM when they comment the
Core reel's keyword. Built only from the reviewed Core spec (no new claims, no X-Ray/product): the year bars, the
pattern with real counts, the 3 traps, the latest 3 PYQs with keys, what to read first, the skip line and the free link.
usage: core_sheet.py spec.json out.jpg        (also called by core_reel.py → <out_dir>/sheet.jpg)
Prints {"minFs":…, "overflow":…}; minFs must be ≥ 26 and overflow false.
"""
import json, os, re, sys, html, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import LOGO_D
import sheet as BASE

CSS = BASE.CSS + """
.sub{margin:-.2em 0 .7em;font:600 max(26px,calc(26px*var(--s)))/1.2 "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#4a453b}
.yrs{display:flex;align-items:flex-end;gap:8px;height:calc(120px*var(--s));margin:.2em 0 .3em}
.yrs div{flex:1;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}
.yrs b{display:block;width:100%;background:#f2b705;border-radius:4px 4px 0 0}.yrs b.z{background:#d9d1bf;height:3px!important}
.yrs em{font:600 26px/1 "IBM Plex Mono";font-style:normal;margin-bottom:4px}.yrs span{margin-top:6px;font:600 26px/1 "IBM Plex Mono";color:#4a453b}
.pr{display:flex;gap:.5em;align-items:baseline;margin:0 0 .25em;font:400 1em/1.3 "IBM Plex Sans"}
.pr b{flex:none;min-width:1.6em;font:500 italic 1.3em/1 Newsreader,serif;color:#8a6200}.pr small{color:#4a453b;font-size:max(26px,.86em)}
"""

def build_html(spec):
    nb = lambda x: re.sub(r'(\d)([–-])(\d)', '\\1\u2060\\2\u2060\\3', x)
    e = lambda x: nb(html.escape(str(x)))
    yrs = spec['years']; ymax = max(yrs.values()) or 1; y0, y1 = min(yrs), max(yrs)
    bars = ''.join(f'<div>{f"<em>{v}</em>" if v else ""}<b class="{"" if v else "z"}" style="height:{int(round(70 * v / ymax)) if v else 3}%"></b><span>’{k[2:]}</span></div>' for k, v in yrs.items())
    pat = ''.join(f'<div class="pr"><b>{r["n"]}</b><span>{e(r["label"])}{(" <small>· " + e(r["eg"]) + "</small>") if r.get("eg") else ""}</span></div>' for r in spec['pattern'])
    note = f'<div class="box meth">{e(spec["pattern_note"])}</div>' if spec.get('pattern_note') else ''
    traps = ''.join(f'<p class="v"><b>{e(t["h"])}</b> — {e(t["p"])}</p>' for t in spec['traps'][:3])
    pyqs = ''.join(f'<p class="v"><b>{p["y"]} Q{p["q"]}</b> {e(p["gist"])} <b>({e(p["a"])})</b> {e(p["ans"])}</p>' for p in spec['pyqs'][:3])
    reads = ''.join(f'<p class="v"><b>✓ {e(r["h"])}</b> — {e(r["p"])}</p>' for r in spec['read'])
    skip = f'<div class="box trap"><b>Skip:</b> {e(spec["skip"])}</div>' if spec.get('skip') else ''
    body = f'''<div class="top">{LOGO_D}<span>Core sheet</span><span class="r">Core {spec["n"]} of {spec.get("core_total", 60)}</span></div>
<div id="body"><div id="in">
<h1>{e(spec['name'])}</h1>
<div class="sub">{e(spec['subject'])} · asked {spec['asked']} times, {y0}–{y1}</div>
<div class="yrs">{bars}</div>
<div class="lab">The pattern</div><div class="q">{spec['pattern_h']}</div>{pat}{note}
<div class="lab">UPSC's traps</div>{traps}
<div class="lab">The latest 3 PYQs</div>{pyqs}
<div class="lab">Read this first</div>{reads}{skip}
</div></div>
<div class="ft">Answer keys: UPSC (2026: provisional where marked).<span class="u">All {spec['asked']} questions explained: minimalistias.com/upsc-syllabus/prelims</span></div>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace("url(F/", "url(file://" + BASE.FONTS + "/")}</style></head><body><div id="sh">{body}</div></body></html>'

def render(spec, out):
    from playwright.sync_api import sync_playwright
    td = tempfile.mkdtemp(prefix='coresheet-'); hp = os.path.join(td, 's.html'); png = os.path.join(td, 's.png')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        open(hp, 'w').write(build_html(spec))
        pg.goto('file://' + hp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        rep = pg.evaluate(BASE.MEASURE)
        pg.query_selector('#sh').screenshot(path=png); b.close()
    from PIL import Image
    Image.open(png).convert('RGB').save(out, 'JPEG', quality=90)
    print(json.dumps({'sheet': out, **rep}))
    return rep

if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2])
