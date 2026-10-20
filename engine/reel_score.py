#!/usr/bin/env python3
"""Original procedural score for the PYQ reel (felt piano + warm pad + soft SFX). No samples, no licensed music.
usage: reel_score.py cues.json out.wav
cues = {"dur": 44.0, "seed": 20261020,
        "q": [3.0, 13.0],          # question on screen (reading: sparse pad + soft clock)
        "count": 13.0,             # 3-2-1 before the picks (louder ticks over the last 3 s of the question)
        "pops": [13.6, 15.4],      # speech bubbles
        "comment": [17.4, 19.8],   # 'comment your answer' (held tension)
        "reveal": 19.8,            # answer: bell + lift
        "whoosh": [3.0, 13.0, ...],# scene changes
        "cta": 40.0}               # resolve + fade
"""
import json, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve

SR = 48000

def build(c):
    DUR = c['dur']; N = int(SR * DUR); rng = np.random.default_rng(c.get('seed', 1))
    mus = np.zeros((N, 2)); sfx = np.zeros((N, 2))

    def put(buf, sig, at, gain=1.0, pan=0.0):
        i = int(at * SR); n = min(len(sig), N - i)
        if n <= 0 or i < 0: return
        l = np.sqrt((1 - pan) / 2); r = np.sqrt((1 + pan) / 2)
        buf[i:i + n, 0] += sig[:n] * gain * l; buf[i:i + n, 1] += sig[:n] * gain * r
    def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), btype='high'); return lfilter(b, a, x)
    def bp(x, lo, hi): return hp(lp(x, hi), lo)
    def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
    def env(n, a=.005, d=.1, s=0., r=.05):
        e = np.ones(n); A = max(1, min(n, int(a * SR))); D = max(0, min(int(d * SR), n - A)); R = min(int(r * SR), n)
        e[:A] = np.linspace(0, 1, A)
        if D > 0: e[A:A + D] = np.linspace(1, s, len(e[A:A + D]))
        e[A + D:] = s
        if R > 0: e[-R:] *= np.linspace(1, 0, R)
        return e
    def midi(m): return 440 * 2 ** ((m - 69) / 12)
    def piano(m, dur=2.6, vel=1.0):
        f = midi(m); n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for k, (a, dec) in enumerate([(1, 2.2), (.45, 1.4), (.22, .9), (.12, .6), (.06, .4)]):
            x += a * np.sin(2 * np.pi * f * (k + 1) * (1 + .0004 * k * k) * t) * np.exp(-t / (dec * (1.2 if m < 60 else .9)))
        x = (x + lp(rng.standard_normal(n), 2500) * np.exp(-t / .012) * .05) * env(n, .004, 0, 1, .25)
        return lp(x, 3200 + vel * 1500) * vel
    def pad(ms, dur, a=1.2, r=1.6, bright=900):
        n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for m in ms:
            for det in (-7, 0, 7):
                ff = midi(m) * 2 ** (det / 1200); x += 2 * ((t * ff + rng.random()) % 1) - 1
        x = lp(x, bright, 4) * (0.85 + 0.15 * np.sin(2 * np.pi * .15 * t))
        return norm(x) * env(n, a, 0, 1, r)
    def sub(m, dur): n = int(dur * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * midi(m) * t) * env(n, .3, 0, 1, .6)
    def softkick():
        n = int(.4 * SR); t = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(95 * np.exp(-t * 22) + 48) / SR) * env(n, .003, .3, 0, .08)
    def bell(m, dur=3.0):
        f = midi(m); n = int(dur * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .6) + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .3)
        return x * np.exp(-t / 1.6) * env(n, .002, 0, 1, .3)
    def tick(): n = int(.03 * SR); return norm(hp(rng.standard_normal(n), 3000)) * env(n, .001, .02, 0, .01)
    def pop(): n = int(.08 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(800 * np.exp(-t * 40) + 250) / SR) * env(n, .001, .06, 0, .02)
    def whoosh(dur=.5):
        n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); seg = 2048
        for i in range(0, n, seg): out[i:i + seg] = lp(x[i:i + seg], 300 + 4500 * i / n)
        return norm(out) * env(n, .15 * dur, .6 * dur, .2, .25 * dur)

    # key: one of D / F / G, picked by seed so the daily reels don't all sound the same
    T = [0, 3, 5][c.get('seed', 1) % 3]
    CH = {'I': [50, 57, 62, 66, 69], 'V': [45, 57, 61, 64, 69], 'vi': [47, 59, 62, 66, 71], 'IV': [43, 55, 59, 62, 67]}
    ARP = {'I': [62, 66, 69, 74, 69, 66], 'V': [61, 64, 69, 73, 69, 64], 'vi': [62, 66, 71, 74, 71, 66], 'IV': [62, 67, 71, 74, 71, 67]}
    CH = {k: [m + T for m in v] for k, v in CH.items()}; ARP = {k: [m + T for m in v] for k, v in ARP.items()}
    q0, q1 = c['q']; rv = c['reveal']; cta = c['cta']; cm0, cm1 = c['comment']

    # hook: two plucked chords
    for t0, k in ((0.0, 'vi'), (1.5, 'IV')):
        put(mus, pad(CH[k][1:4], 1.8, a=.3, r=.8, bright=800), t0, .10); put(mus, sub(CH[k][0] - 12, 1.5), t0, .10)
        for j, m in enumerate(CH[k][2:5]): put(mus, piano(m + 12, 2.0, .6), t0 + .1 + j * .18, .2, -.3 + .3 * j)
    # question: sustained pad (quiet, reading) + soft clock each second, louder for the last 3
    put(mus, pad(CH['I'][1:4], q1 - q0 + .6, a=1.0, r=1.2, bright=600), q0, .12)
    put(mus, sub(CH['I'][0] - 12, q1 - q0), q0, .08)
    t = q0 + 1.0
    while t < q1 - 3.05: put(sfx, tick(), t, .06, .3); t += 1.0
    for j in range(3): put(sfx, tick(), q1 - 3 + j, .2); put(mus, piano(CH['I'][3] + 12, 1.0, .5), q1 - 3 + j, .08)
    # picks: gentle arpeggio I–V–vi–IV until the comment beat
    prog = ['I', 'V', 'vi', 'IV']; t = q1; k = 0
    while t < cm0 - .05:
        ch = prog[k % 4]; L = min(1.6, cm0 - t)
        put(mus, pad(CH[ch][1:4], L + .3, a=.4, r=.5, bright=850), t, .12); put(mus, sub(CH[ch][0] - 12, L), t, .1)
        for j, m in enumerate(ARP[ch]):
            if t + j * .2667 < cm0: put(mus, piano(m, 1.4, .5), t + j * .2667, .12, -.25 if j % 2 else .25)
        t += 1.6; k += 1
    # comment: held V (tension) + rising pulses
    put(mus, pad(CH['V'][1:5], cm1 - cm0 + .2, a=.3, r=.3, bright=1100), cm0, .14); put(mus, sub(CH['V'][0] - 12, cm1 - cm0), cm0, .12)
    for j in range(int((cm1 - cm0) / .4)): put(mus, piano(CH['V'][4] + 12 * (j % 2), .5, .5), cm0 + j * .4, .07)
    # reveal: bell + kick + brighter arpeggio until the CTA
    put(mus, bell(CH['I'][4] + 12), rv, .16); put(sfx, softkick(), rv, .4)
    for j, m in enumerate([CH['I'][2] + 12, CH['I'][3] + 12, CH['I'][4] + 12]): put(mus, piano(m, 2.6, .9), rv + j * .06, .16)
    t = rv; k = 0
    while t < cta - .05:
        ch = prog[k % 4]; L = min(1.6, cta - t)
        put(mus, pad(CH[ch][1:5], L + .3, a=.25, r=.5, bright=1300), t, .13); put(mus, sub(CH[ch][0] - 12, L), t, .12)
        put(mus, piano(CH[ch][0], 2.2, .6), t, .14)
        for j, m in enumerate(ARP[ch]):
            if t + j * .2667 < cta: put(mus, piano(m, 1.3, .55), t + j * .2667, .11, -.3 if j % 2 else .3)
        if k % 2 == 0: put(sfx, softkick(), t, .18)
        t += 1.6; k += 1
    # CTA: resolve on I
    put(mus, pad(CH['I'][1:5], DUR - cta, a=.4, r=1.5, bright=1200), cta, .15); put(mus, sub(CH['I'][0] - 12, DUR - cta), cta, .12)
    for j, m in enumerate([CH['I'][2], CH['I'][3], CH['I'][4], CH['I'][2] + 12]): put(mus, piano(m, 3.0, .7), cta + j * .4, .15, -.3 + .2 * j)
    put(mus, bell(CH['I'][2] + 24), cta + .2, .08)

    for at in c.get('pops', []): put(sfx, pop(), at, .15)
    for at in c.get('whoosh', []): put(sfx, whoosh(.45), max(0, at - .2), .10)

    # room reverb on the music, fade out
    irn = int(2.0 * SR); ir = rng.standard_normal((irn, 2)) * np.exp(-np.arange(irn) / SR / .6)[:, None]; ir[:int(.01 * SR)] = 0
    wet = np.stack([fftconvolve(mus[:, ch], ir[:, ch])[:N] for ch in range(2)], 1)
    mus = mus + norm(wet) * np.max(np.abs(mus)) * .3
    fade = np.ones(N); fs = int((DUR - 1.6) * SR); fade[fs:] = np.linspace(1, 0, N - fs); mus *= fade[:, None]
    mix = mus * .9 + sfx * .8
    mix = np.tanh(mix * 1.2); mix /= np.max(np.abs(mix)) * 1.12
    return (mix * 32767).astype(np.int16)

if __name__ == '__main__':
    wavfile.write(sys.argv[2], SR, build(json.load(open(sys.argv[1])))); print('wrote', sys.argv[2])
