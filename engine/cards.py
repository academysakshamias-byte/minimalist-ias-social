#!/usr/bin/env python3
"""Render carousel slides + phone-readability gate.
cards.py page.html out_dir selector [min_body_px] """
import asyncio, os, sys, json
from playwright.async_api import async_playwright
CHECK = r"""
(sel) => {
  const out = [];
  document.querySelectorAll(sel).forEach(sl => {
    const R = sl.getBoundingClientRect();
    let minFs = 999, words = 0, offEdge = [], overlaps = [];
    const boxes = [];
    const tw = document.createTreeWalker(sl, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) {
      const n = tw.currentNode, t = n.textContent.trim();
      if (!t) continue;
      const el = n.parentElement, cs = getComputedStyle(el);
      if (cs.opacity === '0' || cs.visibility === 'hidden') continue;
      const fs = parseFloat(cs.fontSize);
      minFs = Math.min(minFs, fs);
      words += t.split(/\s+/).length;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        const x0 = r.left - R.left, x1 = r.right - R.left, y0 = r.top - R.top, y1 = r.bottom - R.top;
        if (x0 < 60 || x1 > 1020 || y0 < 40 || y1 > 1310) offEdge.push(t.slice(0, 30));
        boxes.push({t: t.slice(0, 24), x0, x1, y0, y1});
      }
    }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      const ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (ox > 4 && oy > 6 && a.t !== b.t) overlaps.push(a.t + ' / ' + b.t);
    }
    out.push({id: sl.id, minFs, words, offEdge: [...new Set(offEdge)], overlaps: [...new Set(overlaps)].slice(0, 5)});
  });
  return out;
}"""
async def main(html, out, sel):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1200, "height": 1500}, device_scale_factor=1)
        await pg.goto("file://" + os.path.abspath(html)); await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(400)
        rep = await pg.evaluate(CHECK, sel)
        for r in rep:
            await pg.locator("#" + r["id"]).screenshot(path=f"{out}/{r['id']}.png")
        print(json.dumps(rep, indent=1))
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
