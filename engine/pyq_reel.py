#!/usr/bin/env python3
"""PYQ of the Day as a 9:16 reel (1080×1920, 30 fps) with Aarav & Priya, captions + original music, no voice-over.
usage: pyq_reel.py spec.json out_dir [--fast]      (--fast: gate + stills only, no video)
The spec is the same spec.json as pyq_post.py (q, hook, aarav, priya, answer_head, verdicts, source, remember,
trap, trap_who, method, extra[0] optional). Optional reel-only keys:
  "reel_extra": true/false   include spec.extra[0] as one scene (default false: completion rate beats depth here)
  "seed": int                music variation (default: date digits)
Writes: reel.mp4, cover.jpg (hook frame, for cover_url), story.jpg (9:16 'new reel' story), stills/*.jpg (one per
scene, look at them), gate.json, meta.json (Instagram caption draft + YouTube title/description/tags).
Optional spec keys for the text: "topic" ("Geography · critical minerals"), "hashtags" (≤ 5), "yt_tags".
"dm_word": one easy keyword from the topic (≤ 12 letters, e.g. "CONGO"): the reel ends "Comment CONGO → we DM you
today's 1-page revision sheet" (engine/sheet.py → sheet.jpg, also checked by the gate) and the caption asks the same. Prints the gate: every scene must have minFs ≥ 26, no text outside the safe box
(x 140–920, y 300–1300), no overlapping text, and ≤ 45 content words (the verbatim question is exempt).
Arc (built for Reels/Shorts ranking: completion, replays, sends, saves): frame 0 = the full hook on two faces with
"answer in N s" → verbatim question (timer, 3-2-1) → Aarav's and Priya's picks → comment a/b/c/d → answer +
reactions → option by option → [in the news] → the trap → remember + method ("save this") → "send this to the friend
who'd pick (x)" → last 0.6 s fade back to the hook frame so the loop is seamless.
"""
import json, os, re, sys, html, shutil, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pyq_post import LOGO_D, TICK, CROSS

FPS = 30
POSES = os.path.join(ROOT, 'poses', 'cut')
FONTS = os.path.join(ROOT, 'brand', 'fonts')
GSAP = os.path.join(HERE, 'node_modules', 'gsap', 'dist', 'gsap.min.js')

def need_gsap():
    if not os.path.exists(GSAP):   # GSAP is installed from npm, not committed
        subprocess.run(['npm', 'install', '--prefix', HERE, '--no-save', '--no-audit', '--no-fund', 'gsap@3.12.5'], check=True,
                       stdout=subprocess.DEVNULL)

def P(name): return 'file://' + os.path.join(POSES, name + '.png')
def strip(h): return re.sub(r'<[^>]+>', '', h)
def nwords(s): return len(strip(s).split())

RIGHT = {'aarav': 'aarav_celebrate', 'priya': 'priya_clap'}
WRONG = {'aarav': 'aarav_oops', 'priya': 'priya_surprised'}
THINK = {'aarav': 'aarav_thinking', 'priya': 'priya_thinking'}
EXPLAIN = {'aarav': 'aarav_pointing', 'priya': 'priya_explain'}
WAVE = {'aarav': 'aarav_wave', 'priya': 'priya_wave'}

CSS = """
@font-face{font-family:"Newsreader";font-weight:500;src:url(F/newsreader-latin-500-normal.woff2)}
@font-face{font-family:"Newsreader";font-weight:600;src:url(F/newsreader-latin-600-normal.woff2)}
@font-face{font-family:"Newsreader";font-weight:500;font-style:italic;src:url(F/newsreader-latin-500-italic.woff2)}
@font-face{font-family:"Newsreader";font-weight:600;font-style:italic;src:url(F/newsreader-latin-600-italic.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:400;src:url(F/ibm-plex-sans-latin-400-normal.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:500;src:url(F/ibm-plex-sans-latin-500-normal.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:600;src:url(F/ibm-plex-sans-latin-600-normal.woff2)}
@font-face{font-family:"IBM Plex Sans";font-weight:700;src:url(F/ibm-plex-sans-latin-700-normal.woff2)}
@font-face{font-family:"IBM Plex Mono";font-weight:600;src:url(F/ibm-plex-mono-latin-600-normal.woff2)}
:root{--bg:#13110d;--ink:#ece6d8;--ivory:#faf7f0;--muted:#b3ab9b;--gold:#f2b705;--amber:#d9a441;--sage:#7f9a7a;--terra:#c6714f;
 --serif:"Newsreader",Georgia,serif;--sans:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",monospace}
*{box-sizing:border-box}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--ink);font-family:var(--sans)}
.glow{position:absolute;inset:0;background:radial-gradient(900px 700px at 85% 8%,rgba(242,183,5,.20),transparent 60%),radial-gradient(800px 600px at 10% 95%,rgba(242,183,5,.07),transparent 60%)}
.grain{position:absolute;inset:0;opacity:.035;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence baseFrequency='.9' numOctaves='2'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")}
.sc{position:absolute;inset:0;opacity:0;visibility:hidden}
em{font-style:italic;color:var(--gold)}
.kick{position:absolute;left:140px;top:300px;display:flex;align-items:center;gap:14px;font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--gold);z-index:20}
.kick svg{width:40px;height:40px}
/* characters */
.ch{position:absolute;top:850px;z-index:2}
.ch img{position:absolute;bottom:auto;top:0;height:960px;opacity:0}
#ca{left:10px}#ca img{left:0}
#cp{right:10px}#cp img{right:0}
#dim{position:absolute;inset:0;background:rgba(10,9,7,.82);opacity:0;z-index:5}
/* hook */
.chip{position:absolute;left:140px;top:0;padding:12px 22px;border-radius:999px;border:2px solid var(--gold);font:600 28px/1 var(--mono);letter-spacing:.06em;color:var(--gold);z-index:6}
.hook{position:absolute;left:140px;width:780px;top:380px;margin:0;font:500 88px/1.04 var(--serif);color:var(--ivory);letter-spacing:-.01em;z-index:6}
/* question */
.qc{position:absolute;left:140px;width:780px;top:380px;background:var(--ivory);color:#16130e;border-radius:22px;padding:34px 36px 30px;z-index:6;box-shadow:0 30px 80px rgba(0,0,0,.55)}
.qc .stem{font:500 calc(var(--fs)*1.12)/1.25 var(--serif);margin:0 0 .7em}
.qc .hdr{font:600 calc(var(--fs)*.8)/1.3 var(--mono);color:#5c4002;margin:0 0 .4em;letter-spacing:.02em}
.qc .it{font:400 var(--fs)/1.36 var(--sans);margin:0 0 .45em;padding-left:.7em;border-left:5px solid #d9a441}
.qc .pr{font:600 var(--fs)/1.3 var(--sans);margin:.6em 0 .7em}
.qc .op{display:flex;gap:.55em;align-items:center;margin:0 0 .45em;font:400 var(--fs)/1.28 var(--sans)}
.qc .op i{flex:none;width:1.6em;height:1.6em;border-radius:50%;border:2px solid #16130e;font:600 calc(var(--fs)*.8)/1 var(--mono);display:flex;align-items:center;justify-content:center;font-style:normal}
.qc .more{font:600 calc(var(--fs)*.8)/1 var(--mono);color:#5c4002;letter-spacing:.08em;text-transform:uppercase;margin:0 0 .8em}
.timer{position:absolute;left:140px;width:780px;height:12px;border-radius:6px;background:rgba(236,230,216,.14);overflow:hidden;z-index:6}
.timer i{display:block;height:100%;width:100%;background:var(--gold);transform-origin:left center}
.cd{position:absolute;left:475px;top:1170px;width:130px;height:130px;border-radius:50%;background:var(--gold);color:#13110d;display:flex;align-items:center;justify-content:center;font:600 72px/1 var(--serif);z-index:8;opacity:0}
/* bubbles */
.bub{position:absolute;width:520px;background:var(--ivory);color:#16130e;border-radius:26px;padding:22px 28px 24px;font:600 36px/1.25 var(--sans);box-shadow:0 18px 40px rgba(0,0,0,.45);z-index:7;opacity:0}
.bub .nm{display:block;font:600 26px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:#5c4002;margin-bottom:12px}
.bub .nm b{font:600 italic 34px/1 var(--serif);letter-spacing:0;color:#7a5402;text-transform:none;margin-left:6px}
.bub:after{content:"";position:absolute;bottom:-22px;border:22px solid transparent;border-top-color:var(--ivory);border-bottom:0}
#ba{left:140px;top:380px}#ba:after{left:110px}
#bp{left:400px;top:640px}#bp:after{right:110px}
/* comment */
.cm{position:absolute;left:140px;width:780px;top:470px;text-align:center;z-index:7}
.cm h2{margin:0;font:500 96px/1.05 var(--serif);color:var(--ivory)}
.cm .opts{display:flex;justify-content:center;gap:34px;margin:70px 0 60px}
.cm .opts span{width:132px;height:132px;border-radius:50%;border:4px solid var(--gold);display:flex;align-items:center;justify-content:center;font:500 italic 76px/1 var(--serif);color:var(--gold);padding-bottom:10px}
.cm p{margin:0;font:600 40px/1.3 var(--sans);color:var(--ink)}
/* answer */
.ans{position:absolute;left:140px;width:780px;top:380px;display:flex;gap:40px;align-items:center;z-index:6}
.disc{flex:none;width:190px;height:190px;border-radius:50%;border:4px solid var(--gold);display:flex;align-items:center;justify-content:center;font:500 italic 140px/1 var(--serif);color:var(--gold);padding-bottom:20px;background:rgba(242,183,5,.08)}
.ans .t{font:500 58px/1.12 var(--serif);color:var(--ivory)}
/* verdicts / extra */
.ti{position:absolute;left:140px;width:780px;top:380px;margin:0;font:500 76px/1.05 var(--serif);color:var(--ivory);z-index:6}
.lab{font:600 26px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:22px}
.vds{position:absolute;left:140px;width:780px;top:540px;z-index:6}
.vr{display:flex;gap:26px;align-items:flex-start;margin-bottom:54px;opacity:0}
.ic{flex:none;width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-top:2px}
.ic.yes{background:var(--sage)}.ic.no{background:var(--terra)}
.vr h3{margin:0 0 10px;font:600 46px/1.2 var(--sans);color:var(--ivory)}
.vr p{margin:0;font:400 38px/1.35 var(--sans);color:var(--muted)}
.src{position:absolute;left:140px;width:780px;top:1220px;font:600 26px/1.3 var(--mono);color:var(--muted);letter-spacing:.04em;z-index:6}
.pts{position:absolute;left:140px;width:780px;z-index:6}
.pt{margin:0 0 38px;font:400 42px/1.32 var(--sans);color:var(--ink);opacity:0}.pt b{color:var(--gold);font-weight:600}
/* trap / remember */
.blk{position:absolute;left:140px;width:780px;top:380px;z-index:6}
.blk .big{font:500 60px/1.14 var(--serif);color:var(--ivory)}
.blk .rem{font:500 76px/1.08 var(--serif);color:var(--ivory);margin-bottom:56px}
.blk .meth{font:500 42px/1.32 var(--sans);color:var(--ink)}
/* cta */
.dmc{position:absolute;left:140px;width:780px;top:380px;text-align:center;z-index:6}
.dmc h2{margin:0;font:500 92px/1.05 var(--serif);color:var(--ivory);white-space:nowrap}.dmc h2 em{letter-spacing:.02em}
.dmc p{margin:20px auto 0;max-width:700px;font:600 38px/1.3 var(--sans);color:var(--ink)}
.thumb{position:absolute;left:360px;top:690px;width:360px;height:640px;border-radius:22px;box-shadow:0 40px 100px rgba(0,0,0,.6),0 0 0 3px rgba(242,183,5,.6);z-index:5;transform:rotate(-4deg)}
.cta{position:absolute;left:140px;width:780px;top:360px;text-align:center;z-index:6}
.cta svg{width:110px;height:110px}
.cta h2{margin:18px 0 26px;font:500 84px/1.04 var(--serif);color:var(--ivory)}
.cta .url{font:600 44px/1.2 var(--sans);color:var(--gold)}
.cta p{margin:26px 0 0;font:500 38px/1.3 var(--sans);color:var(--ink)}
/* captions: bottom of the safe box, ≤ 5 words */
.cap{position:absolute;left:160px;right:160px;top:1186px;text-align:center;font:600 46px/1.25 var(--sans);color:var(--ivory);z-index:30;opacity:0}
.cap span{display:inline;background:rgba(10,9,7,.8);padding:8px 22px;border-radius:8px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.cap b{color:var(--gold);font-weight:600}
.storybar{position:absolute;left:84px;right:84px;top:1560px;height:100px;border-radius:50px;background:var(--gold);color:#13110d;display:none;align-items:center;justify-content:center;font:700 36px/1 var(--sans);z-index:40}
body.story .storybar{display:flex}body.story .cap{display:none}
"""

def qcard(t, part='all'):
    e = html.escape; out = ''
    if part in ('all', 'a'):
        out += ''.join(f'<p class="stem">{e(s)}</p>' for s in t['stem'])
        if t.get('header'): out += f'<p class="hdr">{" — ".join(e(h) for h in t["header"])}</p>'
        out += ''.join(f'<p class="it">{e(k)}. {e(v)}</p>' if isinstance(k, str) and k else f'<p class="it">{e(v)}</p>' for k, v in t.get('items', []))
        out += ''.join(f'<p class="pr">{e(s)}</p>' for s in t.get('prompt', []))
    if part == 'a': out += '<p class="more">Options next →</p>'
    if part in ('all', 'b'):
        if part == 'b': out += '<p class="more">The options</p>'
        out += ''.join(f'<div class="op"><i>{k}</i><span>{e(v)}</span></div>' for k, v in t['options'].items())
    return out

def qwords(t, part='all'):
    s = []
    if part in ('all', 'a'): s += t['stem'] + [v for _, v in t.get('items', [])] + t.get('prompt', []) + (t.get('header') or [])
    if part in ('all', 'b'): s += list(t['options'].values())
    return len(' '.join(s).split())

def timeline(spec, split):
    """Scene list with start/end times (s). The question gets reading time by length."""
    t = spec['q']['t']; S = []; at = 0.0
    def add(sid, dur, **kw):
        nonlocal at; S.append(dict(id=sid, t0=round(at, 2), t1=round(at + dur, 2), **kw)); at += dur
    # Pacing for completion rate (the main Reels/Shorts signal): ~32–40 s, every beat ≤ 4.5 s except the question,
    # which gets reading time by length (the timer + countdown keep people watching through it).
    add('hook', 2.4)
    if split:
        wa, wb = qwords(t, 'a'), qwords(t, 'b')
        add('qa', min(12.0, max(6.0, 2.5 + wa / 6)), q=True)
        add('qb', min(8.0, max(4.5, 2.5 + wb / 6)), q=True)
    else:
        add('q', min(14.0, max(6.5, 3 + qwords(t) / 6)), q=True)
    add('pick', 3.8); add('cm', 2.2); add('rev', 3.2)
    add('vd', 3.0 + 0.45 * len(spec['verdicts'][:4]))
    ex = (spec.get('extra') or [None])[0]
    if ex and spec.get('reel_extra', False): add('ex', 3.2 + 0.45 * len(ex['points'][:4]))
    add('trap', 3.6); add('rem', 3.6); add('cta', 3.6)
    add('loop', 0.6)   # the last frames match the first, so the replay is seamless (replays count as watch time / views)
    return S, round(at, 2)

def page(spec, split, story=False):
    e = html.escape; q = spec['q']; t = q['t']; A = spec['aarav']; Pr = spec['priya']; key = q['a']
    S, dur = timeline(spec, split)
    a_ok, p_ok = A['pick'] == key, Pr['pick'] == key
    ans_in = int(round(next(s['t0'] for s in S if s['id'] == 'rev')))
    trap_pick = A['pick'] if not a_ok else (Pr['pick'] if not p_ok else '')
    send_h = (f'Send this to the friend who\'d pick <em>({trap_pick})</em>' if trap_pick else 'Send this to <em>your study partner</em>')
    dmw = re.sub(r'[^A-Z0-9]', '', str(spec.get('dm_word', '')).upper())[:12]
    dm = bool(dmw and spec.get('_sheet') and os.path.exists(spec['_sheet']))
    if dm:   # comments + DMs: the keyword ask (sends a free revision sheet) is the reel's last ask
        cta_html = (f'<div class="sc" id="s-cta"><div class="dmc t"><h2>Comment <em>{dmw}</em></h2>'
                    f'<p>We\'ll DM you today\'s 1-page revision sheet, free.</p></div>'
                    f'<img class="thumb t" id="thumb" src="file://{spec["_sheet"]}"></div>')
    else:
        cta_html = (f'<div class="sc" id="s-cta"><div class="cta t">{LOGO_D}<h2>{send_h}</h2><div class="url">minimalistias.com/pyq-today</div>'
                    f'<p>Every option explained, free</p></div></div>')
    if a_ok and p_ok: rcap = 'Both got it.'
    elif p_ok: rcap = '<b>Priya</b> got it.'
    elif a_ok: rcap = '<b>Aarav</b> got it.'
    else: rcap = 'Both fell for it.'
    tw = spec.get('trap_who', 'aarav' if not a_ok else 'priya'); other = 'priya' if tw == 'aarav' else 'aarav'
    poses = {'aarav': {THINK['aarav'], A['pose'], RIGHT['aarav'] if a_ok else WRONG['aarav'], WRONG['aarav'], EXPLAIN['aarav'], WAVE['aarav']},
             'priya': {THINK['priya'], Pr['pose'], RIGHT['priya'] if p_ok else WRONG['priya'], WRONG['priya'], EXPLAIN['priya'], WAVE['priya']}}
    imgs = {w: ''.join(f'<img data-p="{p}" src="{P(p)}">' for p in sorted(ps)) for w, ps in poses.items()}
    vd = ''.join(f'<div class="vr t"><span class="ic {"yes" if v["ok"] else "no"}">{TICK if v["ok"] else CROSS}</span><div><h3>{e(v["h"])}</h3><p>{e(v["p"])}</p></div></div>' for v in spec['verdicts'][:4])
    ex = (spec.get('extra') or [None])[0]
    exh = ''
    if any(s['id'] == 'ex' for s in S):
        pts = ''.join(f'<p class="pt">{"<b>" + e(p["h"]) + "</b> " + e(p["p"]) if isinstance(p, dict) else e(p)}</p>' for p in ex['points'][:4])
        exh = f'''<div class="sc" id="s-ex"><div class="blk t"><div class="lab">{e(ex.get('lab', 'Deeper'))}</div><div class="big">{ex['h']}</div></div>
 <div class="pts" id="expts">{pts}</div><div class="src t chrome">Source: {e(ex.get('source', spec['source']))}</div></div>'''
    qh = (f'<div class="sc" id="s-qa"><div class="qc t verbatim" id="qca">{qcard(t, "a")}</div></div>'
          f'<div class="sc" id="s-qb"><div class="qc t verbatim" id="qcb">{qcard(t, "b")}</div></div>') if split else \
         f'<div class="sc" id="s-q"><div class="qc t verbatim" id="qc">{qcard(t)}</div></div>'
    kick = f'{LOGO_D}<span>PYQ of the day · Prelims {q["y"]}</span>'
    body = f'''<div class="glow"></div><div class="grain"></div>
<div class="kick chrome" id="kick">{kick}</div>
<div class="ch" id="ca">{imgs['aarav']}</div><div class="ch" id="cp">{imgs['priya']}</div><div id="dim"></div>
<div class="sc" id="s-hook"><h1 class="hook t" id="hookh">{spec['hook']}</h1><div class="chip t chrome" id="hchip">Prelims {q['y']} · answer in {ans_in} s</div></div>
{qh}
<div class="timer" id="timer"><i id="tbar"></i></div><div class="cd" id="cd3">3</div><div class="cd" id="cd2">2</div><div class="cd" id="cd1">1</div>
<div class="bub t" id="ba"><span class="nm">Aarav <b>({A['pick']})</b></span>{e(A['line'])}</div>
<div class="bub t" id="bp"><span class="nm">Priya <b>({Pr['pick']})</b></span>{e(Pr['line'])}</div>
<div class="sc" id="s-cm"><div class="cm t"><h2>Your answer?</h2><div class="opts chrome"><span>a</span><span>b</span><span>c</span><span>d</span></div><p>Comment a, b, c or d before the reveal</p></div></div>
<div class="sc" id="s-rev"><div class="ans t"><div class="disc chrome">{key}</div><div class="t">{spec['answer_head']}</div></div></div>
<div class="sc" id="s-vd"><h2 class="ti t">Option by <em>option</em></h2><div class="vds" id="vds">{vd}</div><div class="src t chrome">Source: {e(spec['source'])}</div></div>
{exh}
<div class="sc" id="s-trap"><div class="blk t"><div class="lab">The trap</div><div class="big">{e(spec['trap'])}</div></div></div>
<div class="sc" id="s-rem"><div class="blk t"><div class="lab">Remember</div><div class="rem">{spec['remember']}</div><div class="lab">Method</div><div class="meth">{e(spec['method'])}</div></div></div>
{cta_html}
{{caps_html}}
<div class="storybar">New PYQ reel · on our profile</div>'''
    caps = {'hook': 'Can you solve this?', 'q': 'Pause. <b>Pick your answer.</b>', 'qa': 'Pause. <b>Read carefully.</b>',
            'qb': 'Now <b>pick your answer.</b>', 'pick': "Who's <b>right?</b>", 'cm': '', 'rev': rcap, 'vd': '', 'ex': '',
            'trap': "Don't <b>fall for this.</b>", 'rem': 'Save this <b>for revision.</b>', 'cta': '' if dm else 'Follow for <b>tomorrow\'s PYQ.</b>', 'loop': ''}
    for s in S: s['cap'] = caps.get(s['id'], '')
    body = body.replace('{caps_html}', ''.join(f'<div class="cap" id="cap-{s["id"]}"><span>{s["cap"]}</span></div>' for s in S if s['cap']))
    js_cfg = json.dumps({'S': S, 'dur': dur, 'tw': tw, 'other': other, 'dm': dm,
                         'pose': {'think': THINK, 'pick': {'aarav': A['pose'], 'priya': Pr['pose']},
                                  'react': {'aarav': RIGHT['aarav'] if a_ok else WRONG['aarav'], 'priya': RIGHT['priya'] if p_ok else WRONG['priya']},
                                  'wrong': WRONG, 'explain': EXPLAIN, 'wave': WAVE}})
    js = """
const C=CFG, $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function fit(el,max){let fs=40;el.style.setProperty('--fs',fs+'px');while(el.offsetHeight>max&&fs>26){fs--;el.style.setProperty('--fs',fs+'px')}return {fs,h:el.offsetHeight}}
window.FIT={};$$('.qc').forEach(q=>{window.FIT[q.id]=fit(q,760)});
function placeTimer(){const q=$$('.qc').map(x=>x.offsetTop+x.offsetHeight);$('#timer').style.top=(Math.max(...q)+28)+'px'}placeTimer();
const TL=gsap.timeline({paused:true});
const show=(s,at)=>TL.set(s,{opacity:1,visibility:'visible'},at), hide=(s,at)=>TL.set(s,{opacity:0,visibility:'hidden'},at);
gsap.set('#timer',{opacity:0});
function cap(at,id,d){if(!$('#cap-'+id))return;TL.fromTo('#cap-'+id,{opacity:0,y:16},{opacity:1,y:0,duration:.25,ease:'power2.out'},at+.05).to('#cap-'+id,{opacity:0,duration:.18},at+d-.2)}
function pose(who,name,at,pop=true){const box=who=='aarav'?'#ca':'#cp';TL.set(box+' img',{opacity:0},at);
  if(!name)return;TL.set(box+` img[data-p="${name}"]`,{opacity:1},at);if(pop)TL.fromTo(box+` img[data-p="${name}"]`,{y:30,scale:.97,transformOrigin:'50% 100%'},{y:0,scale:1,duration:.4,ease:'back.out(1.6)'},at)}
function chars(at,a,p,pop=true){pose('aarav',a,at,pop);pose('priya',p,at,pop)}
for(const s of C.S){const d=s.t1-s.t0, t0=s.t0;
  if(s.id!=='pick')show('#s-'+s.id,t0);
  if(s.id==='hook'){chars(t0,C.pose.think.aarav,C.pose.think.priya,false);TL.set('#hchip',{top:()=>$('#hookh').offsetTop+$('#hookh').offsetHeight+30},0);
     TL.fromTo('#ca,#cp',{scale:1},{scale:1.03,duration:d,ease:'none',transformOrigin:'50% 0%'},t0)}
  if(s.q){chars(t0,null,null);TL.from('#s-'+s.id+' .qc',{y:60,opacity:0,duration:.45,ease:'power3.out'},t0);
     TL.set('#timer',{opacity:1},t0).fromTo('#tbar',{scaleX:1},{scaleX:0,duration:d,ease:'none'},t0).set('#timer',{opacity:0},s.t1);
     const last=C.S.filter(x=>x.q).slice(-1)[0];
     if(s===last){for(let k=0;k<3;k++){const at=s.t1-3+k, el='#cd'+(3-k);TL.set(el,{opacity:1},at).from(el,{scale:1.3,duration:.3,ease:'back.out(2)'},at).set(el,{opacity:0},at+1)}}}
  if(s.id==='pick'){chars(t0,C.pose.pick.aarav,C.pose.pick.priya);TL.to('#ba',{opacity:1,duration:.01},t0+.3).from('#ba',{scale:.6,y:30,duration:.35,ease:'back.out(2)',transformOrigin:'25% 100%'},t0+.3);
     TL.to('#bp',{opacity:1,duration:.01},t0+1.9).from('#bp',{scale:.6,y:30,duration:.35,ease:'back.out(2)',transformOrigin:'75% 100%'},t0+1.9);
     TL.set('#ba,#bp',{opacity:0},s.t1)}
  if(s.id==='cm'){TL.to('#dim',{opacity:1,duration:.25},t0).set('#dim',{opacity:0},s.t1);TL.from('#s-cm .opts span',{scale:0,duration:.35,stagger:.1,ease:'back.out(2)'},t0+.2);
     TL.to('#s-cm .opts span',{scale:1.08,duration:.3,yoyo:true,repeat:3,ease:'sine.inOut'},t0+.9)}
  if(s.id==='rev'){chars(t0,C.pose.react.aarav,C.pose.react.priya);TL.from('#s-rev .disc',{scale:0,rotation:-90,duration:.5,ease:'back.out(1.8)'},t0+.1).from('#s-rev .t .t, #s-rev .ans > .t',{opacity:0,x:40,duration:.4},t0+.4)}
  if(s.id==='vd'){chars(t0,null,null);TL.from('#s-vd .ti',{opacity:0,y:20,duration:.3},t0);$$('#vds .vr').forEach((r,i)=>TL.to(r,{opacity:1,duration:.3},t0+.4+i*.5).from(r,{x:40,duration:.35,ease:'power2.out'},t0+.4+i*.5))}
  if(s.id==='ex'){chars(t0,null,null);const b=$('#s-ex .blk');TL.call(()=>{},null,t0);$('#expts').style.top=(b.offsetTop+b.offsetHeight+44)+'px';
     $$('#expts .pt').forEach((r,i)=>TL.to(r,{opacity:1,duration:.3},t0+.5+i*.5))}
  if(s.id==='trap'){chars(t0,C.tw=='aarav'?C.pose.wrong.aarav:null,C.tw=='priya'?C.pose.wrong.priya:null);TL.from('#s-trap .blk',{opacity:0,y:30,duration:.4},t0+.1)}
  if(s.id==='rem'){chars(t0,C.other=='aarav'?C.pose.explain.aarav:null,C.other=='priya'?C.pose.explain.priya:null);TL.from('#s-rem .rem',{opacity:0,scale:.9,transformOrigin:'0 50%',duration:.4,ease:'back.out(1.5)'},t0+.1).from('#s-rem .meth',{opacity:0,y:20,duration:.35},t0+.9)}
  if(s.id==='loop'){show('#s-hook',t0);chars(t0,C.pose.think.aarav,C.pose.think.priya,false);TL.set('#kick',{opacity:1},t0);TL.set('#ca,#cp',{scale:1},t0)}   // a cut to the exact frame-0 layout: the end→start join is invisible
  if(s.id==='cta'&&C.dm){chars(t0,null,null);TL.set('#kick',{opacity:0},t0);{const h=$('#s-cta .dmc h2');let f=92;while(h.scrollWidth>780&&f>56){f-=2;h.style.fontSize=f+'px'}}$('#thumb').style.top=($('#s-cta .dmc').offsetTop+$('#s-cta .dmc').offsetHeight+40)+'px';TL.from('#s-cta .dmc > *',{opacity:0,y:24,duration:.35,stagger:.15},t0+.05).from('#thumb',{y:260,rotation:8,opacity:0,duration:.6,ease:'power3.out'},t0+.35)}
  else if(s.id==='cta'){chars(t0,C.pose.wave.aarav,C.pose.wave.priya);TL.set('#kick',{opacity:0},t0);TL.from('#s-cta .cta > *',{opacity:0,y:24,duration:.35,stagger:.15},t0+.1)}
  cap(t0,s.id,(s===C.S.filter(x=>x.q).slice(-1)[0])?d-3:d);
  if(s.id!=='pick')hide('#s-'+s.id,s.t1);
}
TL.set({}, {}, C.dur);
TL.progress(1).seek(0.001);   // zero-time sets only apply once the playhead is past 0, so every seek is +1 ms: frame 0 = full hook
window.TL=TL;
"""
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace('url(F/', 'url(file://' + FONTS + '/')}</style></head>
<body{' class="story"' if story else ''}>{body}<script src="file://{GSAP}"></script><script>const CFG={js_cfg};
document.fonts.ready.then(()=>{{{js}}});</script></body></html>''', S, dur

GATE_JS = """(S) => { const out = {};
  for (const s of S) {
    const pts = [s.t0 + Math.min(1.6, (s.t1 - s.t0) / 2), s.t1 - 0.25]; let r = {minFs: 999, unsafe: [], overlaps: [], cwords: 0};
    for (const t of pts) {
      window.TL.seek(t, false);
      const vis = el => { for (let e = el; e && e !== document.body; e = e.parentElement) { const cs = getComputedStyle(e);
          if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) < 0.05) return false } return true };
      const blocks = [...document.querySelectorAll('.t, .cap')].filter(vis);
      const boxes = blocks.map(b => b.getBoundingClientRect());
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        if (blocks[i].contains(blocks[j]) || blocks[j].contains(blocks[i])) continue;
        const a = boxes[i], b = boxes[j];
        if (a.left < b.right - 2 && b.left < a.right - 2 && a.top < b.bottom - 2 && b.top < a.bottom - 2) r.overlaps.push(blocks[i].className + ' × ' + blocks[j].className) }
      let words = 0; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (tw.nextNode()) { const n = tw.currentNode; const tx = n.textContent.trim(); if (!tx) continue; const el = n.parentElement;
        if (!vis(el) || el.closest('script,style,.storybar')) continue;
        r.minFs = Math.min(r.minFs, parseFloat(getComputedStyle(el).fontSize));
        const rg = document.createRange(); rg.selectNodeContents(n);
        for (const b of rg.getClientRects()) if (b.top < 296 || b.bottom > 1300 || b.left < 132 || b.right > 928) r.unsafe.push(tx.slice(0, 28));
        if (!el.closest('.verbatim,.chrome,.cap')) words += tx.split(/\\s+/).length }
      r.cwords = Math.max(r.cwords, words) }
    r.unsafe = [...new Set(r.unsafe)]; r.overlaps = [...new Set(r.overlaps)]; out[s.id] = r }
  return out }"""

def meta(spec):
    """Search-first text for both platforms (Instagram search reads captions more than hashtags; YouTube classifies a
    Short by its title/description). Drafts: the run may edit them, but keep the keyword-first first line."""
    q = spec['q']; t = q['t']; hook = re.sub(r'\s+', ' ', strip(spec['hook'])).strip()
    stem = ' '.join(t['stem']); items = [f'{k}. {v}' for k, v in t.get('items', [])]
    opts = [f'({k}) {v}' for k, v in t['options'].items()]
    qtext = '\n'.join([stem] + items + t.get('prompt', []) + opts)
    A, Pr = spec['aarav'], spec['priya']
    topic = spec.get('topic', '')            # e.g. "Geography · critical minerals"
    tags = spec.get('hashtags') or ['#UPSC', '#UPSCPrelims', '#UPSCPYQ', '#IAS']
    utm = 'https://www.minimalistias.com/pyq-today?utm_source={src}&utm_medium=social&utm_campaign=pyq-of-the-day'
    ig = (f"{hook} UPSC Prelims {q['y']} PYQ{(' | ' + topic) if topic else ''}\n\n"
          f"UPSC Prelims {q['y']}, Q{q['n']}:\n{qtext}\n\n"
          f"Aarav says ({A['pick']}). Priya says ({Pr['pick']}). Who's right?\n\n"
          "Pause the reel and pick yours. Comment a, b, c or d 👇\n"
          + (f"💬 Comment {re.sub(r'[^A-Z0-9]', '', str(spec.get('dm_word', '')).upper())[:12]} and we'll DM you today's 1-page revision sheet (free).\n" if spec.get('dm_word') else "")
          + "📤 Send this to the friend you study with.\n\n"
          "Every option explained, free: minimalistias.com/pyq-today (link in bio)\n\n" + ' '.join(tags[:5]))
    yt_title = f"{hook} | UPSC Prelims {q['y']} PYQ #Shorts"
    if len(yt_title) > 100: yt_title = f"{hook[:100 - 26].rstrip()}… UPSC PYQ #Shorts"
    yt_desc = (f"UPSC Prelims {q['y']}, Q{q['n']}: can you answer before the reveal?\n\n{qtext}\n\n"
               f"Every option explained, free: https://www.minimalistias.com/pyqs/prelims/{q['y']}/q{q['n']}?utm_source=youtube&utm_medium=social&utm_campaign=pyq-of-the-day\n"
               "A new UPSC PYQ every evening with Aarav & Priya. Subscribe for tomorrow's.\n\n"
               "#UPSC #UPSCPrelims #UPSCPYQ #Shorts")
    yt_tags = ['UPSC', 'UPSC Prelims', 'UPSC PYQ', f'UPSC Prelims {q["y"]}', 'IAS', 'Civil Services', 'Minimalist IAS'] + spec.get('yt_tags', [])
    return {'ig_caption': ig[:2200], 'yt_title': yt_title, 'yt_description': yt_desc[:4900], 'yt_tags': yt_tags[:15]}

def build(spec, out, fast=False):
    from playwright.sync_api import sync_playwright
    need_gsap(); out = os.path.abspath(out); os.makedirs(os.path.join(out, 'stills'), exist_ok=True)
    seed = spec.get('seed') or int(re.sub(r'\D', '', spec.get('date', '1'))[:8] or 1)
    import sheet as SH
    sheet_rep = SH.render(spec, os.path.join(out, 'sheet.jpg'))
    spec = {**spec, '_sheet': os.path.join(out, 'sheet.jpg')}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        def load(split, story=False):
            h, S, dur = page(spec, split, story); hp = os.path.join(out, 'story.html' if story else 'reel.html'); open(hp, 'w').write(h)
            pg.goto('file://' + hp); pg.wait_for_function('window.TL !== undefined', timeout=20000); return S, dur
        S, dur = load(False)
        fit = pg.evaluate('window.FIT')
        split = fit['qc']['h'] > 760
        if split: S, dur = load(True); fit = pg.evaluate('window.FIT')
        gate = pg.evaluate(GATE_JS, S)
        bad = {k: v for k, v in gate.items() if v['minFs'] < 26 or v['unsafe'] or v['overlaps'] or (v['cwords'] > 45)}
        if sheet_rep['minFs'] < 26 or sheet_rep['overflow']: bad['sheet'] = sheet_rep
        for s in S:   # one still per scene, at the point where everything is on screen
            pg.evaluate(f'window.TL.seek({s["t1"] - 0.3}, false); 1'); pg.screenshot(path=os.path.join(out, 'stills', f'{s["t0"]:05.1f}-{s["id"]}.jpg'), type='jpeg', quality=85)
        pg.evaluate(f'window.TL.seek({S[0]["t1"] - 0.5}, false); 1'); pg.screenshot(path=os.path.join(out, 'cover.jpg'), type='jpeg', quality=92)
        report = {'dur': dur, 'split': split, 'fit': fit, 'scenes': S, 'gate': gate, 'fail': bad}
        json.dump(report, open(os.path.join(out, 'gate.json'), 'w'), indent=1)
        json.dump(meta(spec), open(os.path.join(out, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
        print(json.dumps({'dur': dur, 'split': split, 'fit': fit, 'fail': bad, 'cwords': {k: v['cwords'] for k, v in gate.items()},
                          'minFs': min(v['minFs'] for v in gate.values())}, ensure_ascii=False))
        load(split, story=True); pg.evaluate(f'window.TL.seek({S[0]["t1"] - 0.5}, false); 1'); pg.screenshot(path=os.path.join(out, 'story.jpg'), type='jpeg', quality=92)
        if fast or bad: b.close(); return report
        load(split); frames = tempfile.mkdtemp(prefix='reel-frames-'); n = int(round(dur * FPS))
        for i in range(n):
            pg.evaluate(f'window.TL.seek({i / FPS + 0.001}, false); 1'); pg.screenshot(path=f'{frames}/f{i:05d}.jpg', type='jpeg', quality=95)
            if i % 150 == 0: print(f'  frame {i}/{n}', flush=True)
        b.close()
    cues = {'dur': dur, 'seed': seed, 'whoosh': [s['t0'] for s in S[1:]]}
    qs = [s for s in S if s.get('q')]; cues['q'] = [qs[0]['t0'], qs[-1]['t1']]
    g = {s['id']: s for s in S}
    cues.update(count=qs[-1]['t1'], pops=[g['pick']['t0'] + .3, g['pick']['t0'] + 1.9], comment=[g['cm']['t0'], g['cm']['t1']],
                reveal=g['rev']['t0'], cta=g['cta']['t0'])
    cj = os.path.join(frames, 'cues.json'); json.dump(cues, open(cj, 'w')); wav = os.path.join(frames, 'score.wav')
    subprocess.run([sys.executable, os.path.join(HERE, 'reel_score.py'), cj, wav], check=True, stdout=subprocess.DEVNULL)
    mp4 = os.path.join(out, 'reel.mp4')
    subprocess.run(['ffmpeg', '-y', '-framerate', str(FPS), '-i', f'{frames}/f%05d.jpg', '-i', wav, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-profile:v', 'high',
                    '-r', str(FPS), '-movflags', '+faststart', mp4], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(frames)
    for f in ('reel.html', 'story.html'):
        try: os.remove(os.path.join(out, f))
        except OSError: pass
    print('wrote', mp4, f'{os.path.getsize(mp4) / 1e6:.1f} MB')
    return report

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    build(json.load(open(a[0])), a[1], fast='--fast' in sys.argv)
