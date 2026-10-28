#!/usr/bin/env python3
"""Core 60 as a 9:16 reel + YouTube Short (1080×1920, 30 fps), made from the SAME reviewed spec as core_post.py.
usage: core_reel.py spec.json out_dir [--fast] [--deep] [--meta]
  --fast: gate + stills + sheet only, no video · --meta: rewrite meta.json only
  --deep: the ~100 s YouTube version (Shivam, 22 Oct 2026: "two versions"): each trap with a "walk" is walked through on the
          real UPSC question: the question verbatim (timer, "Pause here, try it") → Aarav's wrong pick → the tell phrase
          highlighted + Priya's line + the key → the rule card. Ends "the Core sheet: link in the description" (YouTube has no DMs).
  traps[i].walk = {"qid","y","n","key","q": {stem, items, prompt, options} copied VERBATIM from core_data.py,
                   "pick": a wrong option (the tempting one), "aarav": "≤ 9 words", "tell": "exact phrase in the question to highlight",
                   "priya": "≤ 16 words, why the tell decides it"}

Shivam, 22 Oct 2026: "convert the core pipeline into reels and shorts as well". He chose: keep the Thursday carousel
AND make a reel from the same spec, published on Sunday (a second Core touch in the week); the reel never shows the
Syllabus X-Ray (that stays on carousel slide 6, so product mentions stay near 2 in 10 posts); the reel's one ask is
comment-to-DM ("Comment WORD → we DM you the 1-page Core sheet"). No quiz ask, no tag/send/save/follow asks.

Every on-screen line comes from the carousel spec (already fact-checked by the reviewer), except the reel-only keys,
which the reviewer checks too:
  "reel": {
    "hook": "≤ 9 words, one <em> phrase, the searchable topic word in it, TRUE to the data (frame 0, cover, YT title)",
    "dm_word": "HABITAT",          # one easy keyword from the topic, ≤ 8 letters preferred; never a/b/c/d, PYQ, CORE
    "anchor": "s--…",              # core_data.py "anchor" → minimalistias.com/upsc-syllabus/prelims#<anchor>
    "hashtags": ["#UPSC", …] ≤ 5, "yt_tags": [...] optional,
    "aarav_pose": "aarav_confused", "priya_pose": "priya_explain"   # optional
  }
Arc (~38 s + 2.5 s compass sting): frame 0 = hook + year bars on two faces (bars grow in the first 1.2 s) → Aarav asks /
Priya answers → the pattern (counts animate) → 3 traps, one beat each → the latest 3 PYQs with keys → read this first →
"Comment WORD" + the sheet → sting → last 0.6 s cuts back to frame 0 (seamless loop).
Writes reel.mp4, cover.jpg, story.jpg, sheet.jpg (engine/core_sheet.py), stills/*.jpg, gate.json, meta.json.
Gate per scene (same as pyq_reel): minFs ≥ 26, no text outside x 140–920 / y 300–1300, no overlaps, ≤ 45 content words.
"""
import json, os, re, sys, html, shutil, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pyq_post import LOGO_D
import pyq_reel as R

FPS = R.FPS
P, strip = R.P, R.strip

CSS = R.CSS + """
/* core reel */
.yb{position:absolute;left:140px;width:780px;top:1150px;height:146px;padding:14px 22px 12px;border-radius:22px;background:rgba(19,17,13,.86);
    box-shadow:0 18px 40px rgba(0,0,0,.45);display:flex;align-items:flex-end;gap:10px;z-index:30}
.yb div{flex:1;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}
.yb b{display:block;width:100%;background:var(--gold);border-radius:5px 5px 0 0;transform-origin:50% 100%}
.yb b.z{background:rgba(236,230,216,.22);height:4px!important}
.yb em{font:600 26px/1 var(--mono);font-style:normal;color:var(--ivory);margin-bottom:6px}
.yb span{margin-top:8px;font:600 26px/1 var(--mono);color:var(--muted)}
.chip2{position:absolute;left:140px;top:0;padding:12px 22px;border-radius:999px;border:2px solid var(--gold);font:600 28px/1 var(--mono);letter-spacing:.04em;color:var(--gold);z-index:6}
.bub2 .nm{color:#5c4002}
#ba2{left:140px;top:380px}#ba2:after{left:110px}
#bp2{left:400px;top:620px}#bp2:after{right:110px}
.prs{position:absolute;left:140px;width:780px;z-index:6}
.prw{margin-bottom:22px;opacity:0}
.prw .top{display:flex;justify-content:space-between;align-items:baseline;gap:20px;font:600 40px/1.2 var(--sans);color:var(--ivory)}
.prw .top b{font:500 italic 62px/1 var(--serif);color:var(--gold)}
.prw .bar{height:14px;border-radius:7px;background:rgba(236,230,216,.12);margin:10px 0 8px;overflow:hidden}
.prw .bar i{display:block;height:100%;background:var(--gold);border-radius:7px;transform-origin:left center}
.prw p{margin:0;font:400 30px/1.25 var(--sans);color:var(--muted)}
.pnote{margin-top:6px;padding:20px 26px;border-left:6px solid var(--gold);background:rgba(242,183,5,.10);font:500 34px/1.35 var(--sans);color:var(--ivory);opacity:0}
.tb .big{font:500 66px/1.1 var(--serif);color:var(--ivory);margin-bottom:28px}
.tb .tp{font:400 40px/1.36 var(--sans);color:var(--ink)}
.pq2{display:grid;grid-template-columns:150px 1fr;gap:22px;padding:30px 0;border-bottom:2px solid rgba(236,230,216,.14);opacity:0}
.pq2:last-child{border-bottom:0}
.pq2 .y{font:600 30px/1.15 var(--mono);color:var(--gold)}.pq2 .y small{display:block;font-size:26px;color:var(--muted);margin-top:6px}
.pq2 .g{font:400 36px/1.34 var(--sans);color:var(--ink)}
.pq2 .r{margin-top:12px;font:600 34px/1.3 var(--sans);color:var(--ivory)}.pq2 .r b{color:var(--gold);font-family:var(--mono)}
.rd2{display:flex;gap:22px;align-items:flex-start;margin-bottom:34px;opacity:0}
.rd2 .ck{flex:none;width:54px;height:54px;border-radius:12px;border:3px solid var(--sage);display:flex;align-items:center;justify-content:center;color:var(--sage);font:700 30px/1 var(--sans)}
.rd2 h3{margin:2px 0 8px;font:600 40px/1.2 var(--sans);color:var(--ivory)}.rd2 p{margin:0;font:400 36px/1.36 var(--sans);color:var(--ink)}
.wc{position:absolute;left:140px;width:780px;top:380px;background:var(--ivory);color:#16130e;border-radius:22px;padding:30px 34px 26px;z-index:6;box-shadow:0 30px 80px rgba(0,0,0,.55)}
.wc .hd{font:600 max(26px,calc(var(--fs)*.75))/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#5c4002;margin:0 0 .7em}
.wc .stem{font:500 calc(var(--fs)*1.08)/1.25 var(--serif);margin:0 0 .55em}
.wc .it{font:400 var(--fs)/1.34 var(--sans);margin:0 0 .4em;padding-left:.7em;border-left:5px solid #d9a441}
.wc .pr{font:600 var(--fs)/1.3 var(--sans);margin:.5em 0 .6em}
.wc .op{display:flex;gap:.5em;align-items:center;margin:0 0 .35em;font:400 var(--fs)/1.26 var(--sans);border-radius:10px;padding:.08em .2em}
.wc .op i{flex:none;width:1.5em;height:1.5em;border-radius:50%;border:2px solid #16130e;font:600 max(26px,calc(var(--fs)*.78))/1 var(--mono);display:flex;align-items:center;justify-content:center;font-style:normal}
.wc mark{background:none;color:inherit;box-shadow:inset 0 -.42em 0 rgba(242,183,5,.75);padding:0 .06em}
.wc .op.ok{background:#f2b705}.wc .op.ok i{background:#16130e;color:#f2b705}
.wc .op.no i{border-color:#b5532f;color:#b5532f}
.wtimer{position:absolute;left:140px;width:780px;height:12px;border-radius:6px;background:rgba(236,230,216,.14);overflow:hidden;z-index:6}
.wtimer i{display:block;height:100%;width:100%;background:var(--gold);transform-origin:left center}
.pl{position:absolute;left:140px;width:780px;z-index:7;background:rgba(19,17,13,.92);border:2px solid var(--gold);border-radius:22px;padding:22px 28px;font:600 36px/1.3 var(--sans);color:var(--ivory)}
.pl .nm{display:block;font:600 26px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}
#bw{left:140px;top:380px}#bw:after{left:110px}
.sk2{margin-top:10px;padding:22px 26px;border-radius:18px;background:rgba(198,113,79,.16);font:400 34px/1.36 var(--sans);color:var(--ink);opacity:0}.sk2 b{color:var(--terra)}
"""

def hook_of(spec):
    return (spec.get('reel') or {}).get('hook') or f"<em>{html.escape(spec['name'])}</em>: {spec['asked']} Prelims questions."

def dmw_of(spec):
    return re.sub(r'[^A-Z0-9]', '', str((spec.get('reel') or {}).get('dm_word', '')).upper())[:12]

def timeline(spec, deep=False):
    S = []; at = 0.0
    def add(sid, dur, **kw):
        nonlocal at; S.append(dict(id=sid, t0=round(at, 2), t1=round(at + dur, 2), **kw)); at += dur
    words = lambda *xs: len(' '.join(strip(x) for x in xs).split())
    add('hook', 2.6)
    add('ask', 3.8)
    add('pat', min(6.0, max(5.0, 2.6 + words(spec['pattern_h'], spec.get('pattern_note', ''), *[r['label'] + ' ' + r.get('eg', '') for r in spec['pattern']]) / 6)))
    for i, t in enumerate(spec['traps'][:3]):
        w = t.get('walk') if deep else None
        if w:   # the deep (YouTube) version: walk through the real UPSC question behind the trap
            q = w['q']; nw = len(' '.join([q['stem'], q.get('prompt', '')] + q.get('items', []) + list(q['options'].values())).split())
            add(f'wq{i + 1}', min(13.0, max(6.0, 3.5 + nw / 4.5 + 1.0 * len(q.get('items', [])))), q=True)
            add(f'wa{i + 1}', 3.4)
            add(f'wt{i + 1}', min(6.5, max(5.0, 3.0 + words(w['priya']) / 3.2)))
        add(f'tr{i + 1}', min(4.4, max(3.0, 1.4 + words(t['h'], t['p']) / 5)))
    add('pyq', min(6.2, max(5.0, 2.2 + words(*[p['gist'] + ' ' + p['ans'] for p in spec['pyqs'][:3]]) / 6)))
    add('read', min(4.8, max(3.8, 1.8 + words(*[r['h'] + ' ' + r['p'] for r in spec['read']], spec.get('skip', '')) / 6)))
    add('cta', 3.8)
    add('loop', 0.6)
    return S, round(at, 2)

def page(spec, story=False, deep=False):
    e = html.escape; S, dur = timeline(spec, deep); rl = spec.get('reel') or {}
    yrs = spec['years']; ymax = max(yrs.values()) or 1; y0, y1 = min(yrs), max(yrs)
    bars = ''.join(f'<div>{f"<em>{v}</em>" if v else ""}<b class="{"" if v else "z"}" style="height:{int(round(96 * v / ymax)) if v else 4}px"></b><span>{"’" + k[2:]}</span></div>'
                   for k, v in yrs.items())
    pmax = max(r['n'] for r in spec['pattern']) or 1
    prow = ''.join(f'<div class="prw"><div class="top"><span>{e(r["label"])}</span><b>{r["n"]}</b></div><div class="bar"><i style="width:{100 * r["n"] / pmax:.0f}%"></i></div>'
                   f'{("<p>" + e(r["eg"]) + "</p>") if r.get("eg") else ""}</div>' for r in spec['pattern'])
    note = f'<div class="pnote">{e(spec["pattern_note"])}</div>' if spec.get('pattern_note') else ''
    traps = ''.join(f'<div class="sc" id="s-tr{i + 1}"><div class="blk tb t"><div class="lab chrome">UPSC’s trap · {i + 1} of {len(spec["traps"][:3])}</div>'
                    f'<div class="big">{e(t["h"])}</div><div class="tp">{e(t["p"])}</div></div></div>' for i, t in enumerate(spec['traps'][:3]))
    def wcard(i, w, tell):
        q = w['q']; key = w['key']; hl = lambda x: e(x).replace(e(w['tell']), f'<mark>{e(w["tell"])}</mark>') if tell else e(x)
        out = f'<p class="hd chrome">UPSC Prelims {w["y"]} · Q{w["n"]}</p><p class="stem">{hl(q["stem"])}</p>'
        out += ''.join(f'<p class="it">{k + 1}. {hl(v)}</p>' for k, v in enumerate(q.get('items', [])))
        if q.get('prompt'): out += f'<p class="pr">{e(q["prompt"])}</p>'
        out += ''.join(f'<div class="op{(" ok" if k == key else (" no" if k == w["pick"] else "")) if tell else ""}"><i>{k}</i><span>{hl(v)}</span></div>' for k, v in q['options'].items())
        return out
    walks = ''
    for i, t in enumerate(spec['traps'][:3]):
        w = t.get('walk')
        if not (deep and w): continue
        walks += (f'<div class="sc" id="s-wq{i + 1}"><div class="wc t verbatim" id="wcq{i + 1}">{wcard(i, w, False)}</div><div class="wtimer" id="wtm{i + 1}"><i></i></div></div>'
                  f'<div class="sc" id="s-wa{i + 1}"><div class="bub t" id="bw{i + 1}" style="left:140px;top:380px"><span class="nm">Aarav <b>({e(w["pick"])})</b></span>{e(w["aarav"])}</div></div>'
                  f'<div class="sc" id="s-wt{i + 1}"><div class="wc t verbatim" id="wct{i + 1}">{wcard(i, w, True)}</div>'
                  f'<div class="pl t" id="pl{i + 1}"><span class="nm">Priya · answer ({e(w["key"])})</span>{e(w["priya"])}</div></div>')
    pyqs = ''.join(f'<div class="pq2"><div class="y chrome">{p["y"]}<small>Q{p["q"]}</small></div><div><div class="g">{e(p["gist"])}</div>'
                   f'<div class="r"><b>({e(p["a"])})</b> {e(p["ans"])}</div></div></div>' for p in spec['pyqs'][:3])
    reads = ''.join(f'<div class="rd2"><span class="ck chrome">✓</span><div><h3>{e(r["h"])}</h3><p>{e(r["p"])}</p></div></div>' for r in spec['read'])
    skip = f'<div class="sk2"><b>Skip:</b> {e(spec["skip"])}</div>' if spec.get('skip') else ''
    dmw = dmw_of(spec); dm = bool(dmw and spec.get('_sheet') and os.path.exists(spec['_sheet']))
    cta_h, cta_p = (('The <em>Core sheet</em>', f'Free, with all {spec["asked"]} questions explained: link in the description.') if deep else
                    (f'Comment <em>{dmw}</em>', "We'll DM you the 1-page Core sheet, free."))   # YouTube has no DMs: the deep version points to the description
    cta = (f'<div class="sc" id="s-cta"><div class="dmc t"><h2>{cta_h}</h2><p>{cta_p}</p></div>'
           f'<img class="thumb t" id="thumb" src="file://{spec["_sheet"]}"></div>') if dm else \
          (f'<div class="sc" id="s-cta"><div class="cta t">{LOGO_D}<h2>All {spec["asked"]} questions, <em>explained free</em></h2>'
           f'<div class="url">minimalistias.com/upsc-syllabus</div></div></div>')
    ap = rl.get('aarav_pose', 'aarav_confused'); pp = rl.get('priya_pose', 'priya_explain')
    poses = {'aarav': {'aarav_thinking', ap, 'aarav_oops', 'aarav_shocked'}, 'priya': {'priya_thinking', pp, 'priya_explain'}}
    imgs = {w: ''.join(f'<img data-p="{p}" src="{P(p)}">' for p in sorted(ps)) for w, ps in poses.items()}
    body = f'''<div class="glow"></div><div class="grain"></div>
<div class="kick chrome" id="kick">{LOGO_D}<span>Core {spec["n"]} of {spec.get("core_total", 60)} · Prelims</span></div>
<div class="ch" id="ca">{{IMGS_A}}</div><div class="ch" id="cp">{{IMGS_P}}</div><div id="dim"></div>
<div class="sc" id="s-hook"><h1 class="hook t" id="hookh">{hook_of(spec)}</h1><div class="chip2 t chrome" id="hchip">{e(spec["subject"])} · {y0}–{y1}</div>
 <div class="yb t chrome" id="yb">{bars}</div></div>
<div class="bub bub2 t" id="ba2"><span class="nm">Aarav</span>{e(spec['aarav'])}</div>
<div class="bub bub2 t" id="bp2"><span class="nm">Priya</span>{e(spec['priya'])}</div>
<div class="sc" id="s-pat"><h2 class="ti t" id="path">{spec['pattern_h']}</h2><div class="prs t" id="prs">{prow}{note}</div></div>
{walks}{traps}
<div class="sc" id="s-pyq"><h2 class="ti t" id="pyqh">The latest <em>3 PYQs</em></h2><div class="prs t" id="pqs">{pyqs}</div></div>
<div class="sc" id="s-read"><h2 class="ti t" id="readh">Read this <em>first</em></h2><div class="prs t" id="rds">{reads}{skip}</div></div>
{cta}
{{caps_html}}
<div class="storybar">New Core reel · on our profile</div>
{('<img class="wm" src="file://' + R.WATERMARK + '">') if os.path.exists(R.WATERMARK) else ''}'''
    caps = {**{f'wq{k}': 'Pause here <i class="pz"></i> <b>try it.</b>' for k in (1, 2, 3)}, 'ask': '', 'cta': '' if dm else 'New Core <b>every Thursday.</b>'}
    for s in S: s['cap'] = caps.get(s['id'], '')
    body = body.replace('{caps_html}', ''.join(f'<div class="cap" id="cap-{s["id"]}"><span>{s["cap"]}</span></div>' for s in S if s['cap']))
    poses['aarav'].add('aarav_confident')
    imgs = {w: ''.join(f'<img data-p="{p}" src="{P(p)}">' for p in sorted(ps)) for w, ps in poses.items()}
    body = body.replace('{IMGS_A}', imgs['aarav']).replace('{IMGS_P}', imgs['priya'])
    who = {'tr1': ('aarav', 'aarav_oops'), 'tr2': ('priya', 'priya_explain'), 'tr3': ('aarav', 'aarav_shocked')}
    cfg = json.dumps({'S': S, 'dur': dur, 'dm': dm, 'ap': ap, 'pp': pp, 'who': who})
    js = """
const C=CFG, $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const TL=gsap.timeline({paused:true});
const show=(s,at)=>TL.set(s,{opacity:1,visibility:'visible'},at), hide=(s,at)=>TL.set(s,{opacity:0,visibility:'hidden'},at);
function below(head,box,gap){$(box).style.top=($(head).offsetTop+$(head).offsetHeight+gap)+'px'}
below('#path','#prs',34);
function fit(el,max){let fs=40;el.style.setProperty('--fs',fs+'px');while(el.offsetHeight>max&&fs>28){fs--;el.style.setProperty('--fs',fs+'px')}return fs}
$$('[id^=wcq]').forEach(c=>{fit(c,800);const k=c.id.slice(3);$('#wtm'+k).style.top=(c.offsetTop+c.offsetHeight+26)+'px'});
$$('[id^=wct]').forEach(c=>{const k=c.id.slice(3);fit(c,880-$('#pl'+k).offsetHeight);$('#pl'+k).style.top=(c.offsetTop+c.offsetHeight+24)+'px'});below('#pyqh','#pqs',30);below('#readh','#rds',40);
function cap(at,id,d){if(!$('#cap-'+id))return;TL.fromTo('#cap-'+id,{opacity:0,y:16},{opacity:1,y:0,duration:.25,ease:'power2.out'},at+.05).to('#cap-'+id,{opacity:0,duration:.18},at+d-.2)}
function pose(who,name,at,pop=true){const box=who=='aarav'?'#ca':'#cp';TL.set(box+' img',{opacity:0},at);
  if(!name)return;TL.set(box+` img[data-p="${name}"]`,{opacity:1},at);if(pop)TL.fromTo(box+` img[data-p="${name}"]`,{y:30,scale:.97,transformOrigin:'50% 100%'},{y:0,scale:1,duration:.4,ease:'back.out(1.6)'},at)}
function chars(at,a,p,pop=true){pose('aarav',a,at,pop);pose('priya',p,at,pop)}
for(const s of C.S){const d=s.t1-s.t0,t0=s.t0;
  if(s.id!=='ask')show('#s-'+s.id,t0);
  if(s.id==='hook'){chars(t0,'aarav_thinking','priya_thinking',false);TL.set('#hchip',{top:()=>$('#hookh').offsetTop+$('#hookh').offsetHeight+30},0);
     TL.fromTo('#ca,#cp',{scale:1},{scale:1.03,duration:d,ease:'none',transformOrigin:'50% 0%'},t0);
     TL.fromTo('#hookh em',{backgroundSize:'0% 6px'},{backgroundSize:'100% 6px',duration:.35,ease:'power2.out'},t0+.12);
     // movement from the first frames: the year bars grow and their counts pop in (frame 0 already shows hook, chip and faces)
     TL.fromTo('#yb b:not(.z)',{scaleY:.08},{scaleY:1,duration:.5,stagger:.05,ease:'back.out(1.4)'},t0+.2);
     TL.fromTo('#yb em',{opacity:0,y:10},{opacity:1,y:0,duration:.2,stagger:.05},t0+.45);
     TL.fromTo('#ca',{y:0},{y:-16,duration:.14,yoyo:true,repeat:1,ease:'sine.out'},t0+.9)}
  if(s.id==='ask'){chars(t0,C.ap,C.pp);TL.to('#ba2',{opacity:1,duration:.01},t0+.2).from('#ba2',{scale:.6,y:30,duration:.35,ease:'back.out(2)',transformOrigin:'25% 100%'},t0+.2);
     TL.to('#bp2',{opacity:1,duration:.01},t0+1.5).from('#bp2',{scale:.6,y:30,duration:.35,ease:'back.out(2)',transformOrigin:'75% 100%'},t0+1.5);
     TL.set('#ba2,#bp2',{opacity:0},s.t1)}
  if(s.id==='pat'){chars(t0,null,null);TL.from('#path',{opacity:0,y:20,duration:.3},t0);
     $$('#prs .prw').forEach((r,i)=>{const at=t0+.45+i*.45;TL.to(r,{opacity:1,duration:.25},at).from(r.querySelector('.bar i'),{scaleX:0,duration:.5,ease:'power2.out'},at)});
     if($('#prs .pnote'))TL.to('#prs .pnote',{opacity:1,duration:.3},t0+.45+$$('#prs .prw').length*.45+.2)}
  if(/^wq/.test(s.id)){const k=s.id.slice(2);chars(t0,null,null);TL.from('#wcq'+k,{y:60,opacity:0,duration:.35,ease:'power3.out'},t0);
     TL.fromTo('#wtm'+k+' i',{scaleX:1},{scaleX:0,duration:d,ease:'none'},t0)}
  if(/^wa/.test(s.id)){const k=s.id.slice(2);chars(t0,'aarav_confident','priya_thinking');TL.to('#bw'+k,{opacity:1,duration:.01},t0+.15).from('#bw'+k,{scale:.6,y:30,duration:.35,ease:'back.out(2)',transformOrigin:'25% 100%'},t0+.15)}
  if(/^wt/.test(s.id)){const k=s.id.slice(2);chars(t0,null,null);TL.from('#wct'+k+' mark',{boxShadow:'inset 0 0 0 rgba(242,183,5,.75)',duration:.5,stagger:.12},t0+.3);
     TL.from('#wct'+k+' .op.ok, #wct'+k+' .op.no',{backgroundColor:'rgba(0,0,0,0)',duration:.4},t0+1.0);TL.from('#pl'+k,{opacity:0,y:30,duration:.35},t0+1.3)}
  if(/^tr/.test(s.id)){const w=C.who[s.id];chars(t0,w[0]=='aarav'?w[1]:null,w[0]=='priya'?w[1]:null);
     TL.from('#s-'+s.id+' .big',{opacity:0,y:24,duration:.35},t0+.05).from('#s-'+s.id+' .tp',{opacity:0,y:20,duration:.35},t0+.45)}
  if(s.id==='pyq'){chars(t0,null,null);TL.from('#pyqh',{opacity:0,y:20,duration:.3},t0);$$('#pqs .pq2').forEach((r,i)=>TL.to(r,{opacity:1,duration:.3},t0+.4+i*.7).from(r,{x:40,duration:.35,ease:'power2.out'},t0+.4+i*.7))}
  if(s.id==='read'){chars(t0,null,null);TL.from('#readh',{opacity:0,y:20,duration:.3},t0);$$('#rds .rd2, #rds .sk2').forEach((r,i)=>TL.to(r,{opacity:1,duration:.3},t0+.4+i*.5))}
  if(s.id==='cta'&&C.dm){chars(t0,null,null);TL.set('#kick',{opacity:0},t0);{const h=$('#s-cta .dmc h2');let f=92;while(h.scrollWidth>780&&f>56){f-=2;h.style.fontSize=f+'px'}}
     $('#thumb').style.top=($('#s-cta .dmc').offsetTop+$('#s-cta .dmc').offsetHeight+40)+'px';TL.from('#s-cta .dmc > *',{opacity:0,y:24,duration:.35,stagger:.15},t0+.05).from('#thumb',{y:260,rotation:8,opacity:0,duration:.6,ease:'power3.out'},t0+.35)}
  else if(s.id==='cta'){chars(t0,'aarav_thinking','priya_explain');TL.set('#kick',{opacity:0},t0);TL.from('#s-cta .cta > *',{opacity:0,y:24,duration:.35,stagger:.15},t0+.1)}
  if(s.id==='loop'){show('#s-hook',t0);chars(t0,'aarav_thinking','priya_thinking',false);TL.set('#kick',{opacity:1},t0);TL.set('#ca,#cp',{scale:1,y:0},t0);
     TL.set('#hookh em',{backgroundSize:'0% 6px'},t0);TL.set('#yb b:not(.z)',{scaleY:.08},t0);TL.set('#yb em',{opacity:0},t0)}   // exact frame-0 layout: seamless loop
  cap(t0,s.id,d);
  if(s.id!=='ask')hide('#s-'+s.id,s.t1);
}
TL.set({}, {}, C.dur);
TL.progress(1).seek(0.001);
window.TL=TL;
"""
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS.replace('url(F/', 'url(file://' + R.FONTS + '/')}</style></head>
<body{' class="story"' if story else ''}>{body}<script src="file://{R.GSAP}"></script><script>const CFG={cfg};
document.fonts.ready.then(()=>{{{js}}});</script></body></html>''', S, dur

def meta(spec, deep=False):
    """Search-first text for both platforms. One ask only: the sheet keyword (no quiz, no tag/send/save/follow asks)."""
    rl = spec.get('reel') or {}; hook = re.sub(r'\s+', ' ', strip(hook_of(spec))).strip()
    y0, y1 = min(spec['years']), max(spec['years']); word = dmw_of(spec)
    anchor = rl.get('anchor', ''); link = 'https://www.minimalistias.com/upsc-syllabus/prelims'
    rr = [f"{r['n']} others" if r['label'].strip().lower() == 'other' else f"{r['n']} on {r['label'] if r.get('keep_case') else r['label'][0].lower() + r['label'][1:]}" for r in spec['pattern']]
    rows = '; '.join(rr[:-1]) + ('; and ' if len(rr) > 1 else '') + rr[-1]
    pat = re.sub(r'\s+', ' ', strip(spec['pattern_h'])).strip()
    tags = (rl.get('hashtags') or ['#UPSC', '#UPSCPrelims', '#UPSCPYQ', '#MinimalistIAS'])[:5]
    ig = (f"{hook} | UPSC Prelims Core #{spec['n']} of {spec.get('core_total', 60)}\n\n"
          f"UPSC set {spec['asked']} Prelims questions on this sub-topic from {y0} to {y1}. {pat}\n"
          f"Sorted: {rows}.\n\n"
          "In 40 seconds: the pattern, 3 traps from real questions, the latest 3 PYQs and what to read first.\n\n"
          + (f"💬 Comment {word} and we'll DM you the 1-page Core sheet (free).\n\n" if word else "")
          + f"All {spec['asked']} questions, explained, free: minimalistias.com/upsc-syllabus/prelims (link in bio)\n"
          "A new Core every Thursday.\n\n" + ' '.join(tags))
    walks = [t['walk'] for t in spec['traps'][:3] if deep and t.get('walk')]
    yt_title = (f"{hook} | {len(walks)} UPSC traps explained #Shorts" if walks else f"{hook} | UPSC Prelims Core #{spec['n']} #Shorts")
    if len(yt_title) > 100: yt_title = f"{hook[:100 - 30].rstrip()}… UPSC Core #{spec['n']} #Shorts"
    yt_desc = (f"Core #{spec['n']} of {spec.get('core_total', 60)}: {spec['name']}. UPSC set {spec['asked']} Prelims questions on it from {y0} to {y1}. {pat}\n\n"
               f"The pattern: {rows}.\n\n"
               + (("UPSC's traps, walked through on the real questions:\n" + '\n'.join(f"{w['y']} Q{w['n']}: {t['h']} → answer ({w['key']})" for t, w in ((t, t['walk']) for t in spec['traps'][:3] if t.get('walk'))) + "\n\n") if walks else '')
               + (f"The 1-page Core sheet, free: {rl['sheet_url']}\n\n" if rl.get('sheet_url') else '')
               + "The latest 3 PYQs:\n" + '\n'.join(f"{p['y']} Q{p['q']}: {p['gist']} Answer ({p['a']}) {p['ans']}" for p in spec['pyqs'][:3]) + "\n\n"
               f"All {spec['asked']} questions, explained, free: {link}?utm_source=youtube&utm_medium=social&utm_campaign=core-60{('#' + anchor) if anchor else ''}\n\n"
               "One of the 60 most-asked Prelims sub-topics every week with Aarav & Priya. A new Core every Thursday.\n\n"
               "#UPSC #UPSCPrelims #UPSCPYQ #Shorts")
    yt_tags = ['UPSC', 'UPSC Prelims', 'UPSC PYQ', 'UPSC syllabus', 'IAS', 'Civil Services', 'Minimalist IAS', spec['name']] + rl.get('yt_tags', [])
    return {'ig_caption': ig[:2200], 'yt_title': yt_title, 'yt_description': yt_desc[:4900], 'yt_tags': yt_tags[:15],
            'dm_word': word, 'n': spec['n'], 'name': spec['name'], 'asked': spec['asked'], 'anchor': anchor,
            'dm_link': f"{link}?utm_source=instagram&utm_medium=dm&utm_campaign=core-sheet{('#' + anchor) if anchor else ''}"}

def build(spec, out, fast=False, deep=False):
    from playwright.sync_api import sync_playwright
    R.need_gsap(); out = os.path.abspath(out); os.makedirs(os.path.join(out, 'stills'), exist_ok=True)
    seed = spec.get('seed') or int(re.sub(r'\D', '', spec.get('day', '1'))[:8] or 1)
    import core_sheet as SH
    sheet_rep = SH.render(spec, os.path.join(out, 'sheet.jpg'))
    spec = {**spec, '_sheet': os.path.join(out, 'sheet.jpg')}
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        def load(story=False):
            h, S, dur = page(spec, story, deep); hp = os.path.join(out, 'story.html' if story else 'reel.html'); open(hp, 'w').write(h)
            pg.goto('file://' + hp); pg.wait_for_function('window.TL !== undefined', timeout=20000); return S, dur
        S, dur = load()
        gate = pg.evaluate(R.GATE_JS, S)
        bad = {k: v for k, v in gate.items() if v['minFs'] < 26 or v['unsafe'] or v['overlaps'] or v['cwords'] > 45}
        if sheet_rep['minFs'] < 26 or sheet_rep['overflow']: bad['sheet'] = sheet_rep
        for s in S:
            pg.evaluate(f'window.TL.seek({s["t1"] - 0.3}, false); 1'); pg.screenshot(path=os.path.join(out, 'stills', f'{s["t0"]:05.1f}-{s["id"]}.jpg'), type='jpeg', quality=85)
        pg.evaluate(f'window.TL.seek({S[0]["t1"] - 0.5}, false); 1'); pg.screenshot(path=os.path.join(out, 'cover.jpg'), type='jpeg', quality=92)
        report = {'dur': dur, 'scenes': S, 'gate': gate, 'fail': bad}
        json.dump(report, open(os.path.join(out, 'gate.json'), 'w'), indent=1)
        json.dump(meta(spec, deep), open(os.path.join(out, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
        print(json.dumps({'dur': dur, 'fail': bad, 'cwords': {k: v['cwords'] for k, v in gate.items()},
                          'minFs': min(v['minFs'] for v in gate.values())}, ensure_ascii=False))
        load(story=True); pg.evaluate(f'window.TL.seek({S[0]["t1"] - 0.5}, false); 1'); pg.screenshot(path=os.path.join(out, 'story.jpg'), type='jpeg', quality=92)
        if fast or bad: b.close(); return report
        load(); frames = tempfile.mkdtemp(prefix='core-frames-'); n = int(round(dur * FPS))
        loop_t0 = next(s['t0'] for s in S if s['id'] == 'loop')
        sting = R.STING_S if (spec.get('sting', True) and os.path.exists(R.STING)) else 0.0
        n_main = int(round(loop_t0 * FPS)); n_sting = int(round(sting * FPS)); k = 0
        for i in range(n):
            if i == n_main and n_sting:
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', R.STING, '-frames:v', str(n_sting), '-vf', f'fps={FPS},scale=1080:1920',
                                '-q:v', '2', '-start_number', str(k), f'{frames}/f%05d.jpg'], check=True)
                k += n_sting
            pg.evaluate(f'window.TL.seek({i / FPS + 0.001}, false); 1'); pg.screenshot(path=f'{frames}/f{k:05d}.jpg', type='jpeg', quality=95); k += 1
            if i % 150 == 0: print(f'  frame {i}/{n}', flush=True)
        b.close()
    total = round(dur + sting, 2)
    sh = lambda t: t + sting if t >= loop_t0 - 1e-6 else t
    g = {s['id']: s for s in S}; last_tr = [s for s in S if s['id'].startswith('wa' if deep else 'tr')][-1]
    # the score's arc mapped onto the Core beats: reading pad over ask + pattern, arpeggio through the traps,
    # held tension on the last trap, the bell on the latest PYQs (the answers), resolve on the CTA
    cues = {'dur': total, 'seed': seed, 'whoosh': [sh(s['t0']) for s in S[1:]], 'q': [g['ask']['t0'], g['pat']['t1']],
            'count': g['pat']['t1'], 'pops': [g['ask']['t0'] + .2, g['ask']['t0'] + 1.5], 'comment': [last_tr['t0'], last_tr['t1']],
            'reveal': g['wt3']['t0'] if (deep and 'wt3' in g) else g['pyq']['t0'], 'cta': g['cta']['t0']}
    if deep: cues['pops'] += [s['t0'] + .15 for s in S if s['id'].startswith('wa')]
    if sting: cues['sting'] = loop_t0
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
    if '--meta' in sys.argv:   # rewrite meta.json only (e.g. after reel.sheet_url is known): no render
        sp = json.load(open(a[0])); os.makedirs(a[1], exist_ok=True)
        json.dump(meta(sp, '--deep' in sys.argv), open(os.path.join(a[1], 'meta.json'), 'w'), indent=1, ensure_ascii=False)
    else:
        build(json.load(open(a[0])), a[1], fast='--fast' in sys.argv, deep='--deep' in sys.argv)
