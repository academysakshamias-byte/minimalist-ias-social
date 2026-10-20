#!/usr/bin/env python3
"""Convert rendered slides (n1.png…) in a run folder to Instagram JPEGs and print their public raw URLs.
usage: export.py <render_dir> <posts/YYYY-MM-DD/kind>   (second path is relative to the repo root)"""
import sys, os, glob
from PIL import Image
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = 'https://raw.githubusercontent.com/academysakshamias-byte/minimalist-ias-social/main/'
src, rel = sys.argv[1], sys.argv[2].strip('/')
dst = os.path.join(REPO, rel); os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, 'n[0-9]*.png')), key=lambda p: int(os.path.basename(p)[1:-4])):
    out = os.path.join(dst, os.path.basename(f)[:-4] + '.jpg')
    Image.open(f).convert('RGB').save(out, 'JPEG', quality=92, optimize=True, progressive=False)
    print(RAW + rel + '/' + os.path.basename(out))
