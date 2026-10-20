#!/usr/bin/env python3
"""Core 60 source data for one Core number, straight from the site repo (never estimate these numbers).
usage: core_data.py <site_repo_dir> <N> [out.json]
Prints/writes: n, topic, name, anchor (for /upsc-syllabus/prelims#<anchor>), asked, years {2016..2026},
questions [{id, y, q, answer, text, explanation}] newest first, ncert [{book, chapter, title}], and the Core stats.
"""
import json, os, re, sys

def slug(s): return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))

def core(site, N):
    J = lambda p: json.load(open(os.path.join(site, p)))
    D = J('src/data/syllabus/detailed.json')['topics']; T = J('src/data/xray/tiers.json'); S = J('src/data/xray/stats.json')
    P = J('src/data/pyq/prelims.json'); NC = J('src/data/ncert/site.json')
    books = {}
    def walk(o):
        if isinstance(o, dict):
            if 'code' in o and 'chapters' in o: books[o['code']] = o
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(NC)
    for topic, t in D.items():
        for s in t['subs']:
            if T.get(f'pre|{topic}|{slug(s["n"])}') == f'c{N}':
                qs = sorted(s['q'], reverse=True)
                yrs = {str(y): 0 for y in range(S['from'], S['to'] + 1)}
                for q in qs: yrs[q.split('-')[1]] += 1
                ques = []
                for q in qs:
                    x = P[q]; tt = x['t']
                    items = [(i[1] if isinstance(i, list) else i.get('text', str(i)) if isinstance(i, dict) else str(i)) for i in (tt.get('items') or [])]
                    ques.append({'id': q, 'y': x['y'], 'q': x['n'], 'answer': x['a'], 'drop': x.get('drop'),
                                 'text': {'stem': ' '.join(tt.get('stem') or []), 'items': items, 'prompt': ' '.join(tt.get('prompt') or []), 'options': tt['options']},
                                 'explanation': (x.get('ex') or {}).get('summary', '')})
                nc = []
                for code, ch, _ in s.get('nc', []):
                    b = books.get(code)
                    c = next((c for c in (b or {}).get('chapters', []) if c['n'] == ch), None)
                    nc.append({'code': code, 'book': f"NCERT Class {b['cls']} {b['title'][0]}" if b else code, 'chapter': ch, 'title': c['title'][0] if c else None})
                return {'n': N, 'topic': topic, 'name': s['n'], 'anchor': f's--{topic}--{slug(s["n"])}', 'asked': len(qs), 'years': yrs,
                        'questions': ques, 'ncert': nc, 'core_total': S['pre']['core'], 'core_q': S['pre']['q'], 'core_cov': S['pre']['coreCov']}
    raise SystemExit(f'Core #{N} not found')

if __name__ == '__main__':
    d = core(sys.argv[1], int(sys.argv[2]))
    if len(sys.argv) > 3: json.dump(d, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in d.items() if k != 'questions'}, ensure_ascii=False, indent=1))
