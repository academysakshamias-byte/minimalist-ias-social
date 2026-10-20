"""Prop poses: blank props (screen / sheet / notebook cover) detected once, branding warped in at render time.
detect:  python3 props.py detect          -> poses/props/meta.json + cut PNGs (blank) in poses/cut/
compose: from props import compose; compose('priya_phone', 'content.png', 'out.png')
"""
import json, sys, os, glob
import numpy as np, cv2
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'poses')
PICKS = {  # name: (raw file, kind)
  'duo_sheet': ('p02', 'white'), 'duo_laptop': ('p03', 'white'), 'aarav_phone': ('p05', 'white'),
  'aarav_answersheet': ('p07', None), 'aarav_sheet': ('p09', 'white'), 'priya_sheet': ('p11', 'white'),
  'priya_notebook': ('p14', 'navy'), 'priya_phone': ('p15', 'white')}

def region_mask(rgb, kind):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    if kind == 'white':
        m = ((hsv[..., 2] > 238) & (hsv[..., 1] < 18)).astype(np.uint8)
    else:  # navy cover
        m = ((hsv[..., 0] > 100) & (hsv[..., 0] < 130) & (hsv[..., 1] > 70) & (hsv[..., 2] > 40) & (hsv[..., 2] < 150)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    m = (lab == i).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return m

def quad(m):
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    p = cv2.boxPoints(cv2.minAreaRect(c)).astype(float)
    s = p.sum(1); d = np.diff(p, axis=1).ravel()
    return [p[np.argmin(s)].tolist(), p[np.argmin(d)].tolist(), p[np.argmax(s)].tolist(), p[np.argmax(d)].tolist()]  # tl,tr,br,bl

def detect():
    from rembg import remove, new_session
    sess = new_session('isnet-anime'); meta = {}
    for name, (f, kind) in PICKS.items():
        img = Image.open(f'{ROOT}/props/{f}.webp').convert('RGB')
        cut = remove(img, session=sess, post_process_mask=True)
        a = np.array(cut)
        bbox = cut.getbbox()
        entry = {'bbox': bbox}
        if kind:
            m = region_mask(np.array(img), kind)
            # make sure the prop region stays opaque in the cut-out
            a[..., 3] = np.maximum(a[..., 3], m * 255)
            q = quad(m); entry['quad'] = [[x - bbox[0], y - bbox[1]] for x, y in q]
            mm = Image.fromarray(m * 255).crop(bbox); mm.save(f'{ROOT}/props/{name}_mask.png')
        Image.fromarray(a).crop(bbox).save(f'{ROOT}/cut/{name}.png')
        meta[name] = entry; print(name, entry, flush=True)
    json.dump(meta, open(f'{ROOT}/props/meta.json', 'w'), indent=1)

def compose(name, content, out, fit='cover'):
    meta = json.load(open(f'{ROOT}/props/meta.json'))[name]
    base = Image.open(f'{ROOT}/cut/{name}.png').convert('RGBA')
    src = Image.open(content).convert('RGBA') if isinstance(content, str) else content.convert('RGBA')
    q = np.array(meta['quad'], dtype=np.float32)
    w = int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])))
    h = int(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1])))
    # fit content to target aspect (cover)
    sw, sh = src.size; r = max(w / sw, h / sh) if fit == 'cover' else min(w / sw, h / sh)
    src = src.resize((max(1, int(sw * r)), max(1, int(sh * r))), Image.LANCZOS)
    canvas = Image.new('RGBA', (w, h), (255, 255, 255, 255)); canvas.paste(src, ((w - src.width) // 2, (h - src.height) // 2) if fit != 'cover' else ((w - src.width) // 2, 0), src)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), q)
    warped = cv2.warpPerspective(np.array(canvas), M, base.size, flags=cv2.INTER_LANCZOS4)
    mask = np.array(Image.open(f'{ROOT}/props/{name}_mask.png').convert('L')).astype(float) / 255
    mask = cv2.erode(mask, np.ones((3, 3), np.uint8))
    mask = cv2.GaussianBlur(mask, (3, 3), 0)[..., None]
    b = np.array(base).astype(float)
    b[..., :3] = b[..., :3] * (1 - mask) + warped[..., :3] * mask
    Image.fromarray(b.astype(np.uint8)).save(out)
    return out

if __name__ == '__main__' and sys.argv[1:] == ['detect']:
    detect()
