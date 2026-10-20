#!/usr/bin/env python3
"""Instagram story frame (1080×1920, 9:16) around a 4:5 feed slide — never post a feed slide as a story directly:
Instagram zooms a 4:5 image to fill 9:16 and crops its sides.
usage: story.py slide.jpg out.jpg ["kicker"] ["line under the slide"]
Layout keeps Instagram's UI zones clear: nothing in the top 250 px (progress bar, name) or the bottom 260 px (reply bar).
"""
import os, sys, html
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pyq_post import LOGO_D

def story(slide, out, kicker='New post', line='Tap the post below · link in bio'):
    e = html.escape; slide = os.path.abspath(slide); out = os.path.abspath(out)
    page = f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{HERE}/brand.css"><style>
body{{margin:0}}#st{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#13110d}}
#st .g{{position:absolute;inset:0;background:radial-gradient(1200px 900px at 100% 0%,rgba(242,183,5,.16),transparent 60%),radial-gradient(900px 700px at 0% 100%,rgba(242,183,5,.07),transparent 60%)}}
.top{{position:absolute;left:84px;right:84px;top:262px;display:flex;align-items:center;gap:16px;font:600 30px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}}
.top svg{{width:46px;height:46px}}
.sl{{position:absolute;left:84px;top:340px;width:912px;height:1140px;border-radius:28px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 0 2px rgba(242,183,5,.35)}}
.sl img{{width:100%;height:100%;display:block}}
.ln{{position:absolute;left:84px;right:84px;top:1530px;height:96px;border-radius:48px;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:700 34px/1 var(--sans);text-align:center;padding:0 30px;box-sizing:border-box}}
</style></head><body><div id="st"><div class="g"></div>
<div class="top">{LOGO_D}<span>{e(kicker)}</span></div>
<div class="sl"><img src="file://{slide}"></div>
<div class="ln">{e(line)}</div></div></body></html>'''
    hp = out.rsplit('.', 1)[0] + '.html'; open(hp, 'w').write(page)
    png = out.rsplit('.', 1)[0] + '.png'
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + hp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        pg.query_selector('#st').screenshot(path=png); b.close()
    from PIL import Image
    Image.open(png).convert('RGB').save(out, 'JPEG', quality=92)
    return out

if __name__ == '__main__':
    a = sys.argv[1:]
    print(story(a[0], a[1], *(a[2:4])))
