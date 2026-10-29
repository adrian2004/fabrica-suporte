"""Gera os icones da Fabrica Suporte a partir de fabrica/logo-original.jpg."""
import base64, io, os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = Image.open(os.path.join(ROOT, "fabrica", "logo-original.jpg")).convert("RGB")
sym = src.crop((255, 45, 805, 403))  # apenas o simbolo <fc/>, sem o texto

# Remove o branco externo (flood fill a partir dos cantos); o branco interno do aro e preservado.
w, h = sym.size
mask = Image.new("L", (w, h), 255)
tmp = sym.copy()
MARK = (255, 0, 255)
for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
    ImageDraw.floodfill(tmp, pt, MARK, thresh=40)
px, mp = tmp.load(), mask.load()
for y in range(h):
    for x in range(w):
        if px[x, y] == MARK:
            mp[x, y] = 0
# mantem apenas o maior componente conexo (descarta restos de texto/ruido do JPG)
from collections import deque
seen = set(); best = []
for y0 in range(h):
    for x0 in range(w):
        if mp[x0, y0] and (x0, y0) not in seen:
            comp = []; dq = deque([(x0, y0)]); seen.add((x0, y0))
            while dq:
                x, y = dq.popleft(); comp.append((x, y))
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0 <= nx < w and 0 <= ny < h and mp[nx, ny] and (nx, ny) not in seen:
                        seen.add((nx, ny)); dq.append((nx, ny))
            if len(comp) > len(best): best = comp
keep = set(best)
for y in range(h):
    for x in range(w):
        if (x, y) not in keep: mp[x, y] = 0
mask = mask.filter(ImageFilter.GaussianBlur(1.2))
sym = sym.convert("RGBA")
sym.putalpha(mask)
sym = sym.crop(sym.getbbox())

def square(size, pad=0.06):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inner = int(size * (1 - 2 * pad))
    s = min(inner / sym.width, inner / sym.height)
    r = sym.resize((max(1, int(sym.width * s)), max(1, int(sym.height * s))), Image.LANCZOS)
    canvas.paste(r, ((size - r.width) // 2, (size - r.height) // 2), r)
    return canvas

def out(rel):
    return os.path.join(ROOT, *rel.split("/"))

big = square(1024)
big.save(out("res/icon.png"))
big.save(out("res/mac-icon.png"))
square(256).save(out("res/128x128@2x.png"))
square(128).save(out("res/128x128.png"))
square(64).save(out("res/64x64.png"))
square(32).save(out("res/32x32.png"))
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
big.save(out("res/icon.ico"), sizes=ico_sizes)
big.save(out("flutter/windows/runner/resources/app_icon.ico"), sizes=ico_sizes)
big.save(out("res/tray-icon.ico"), sizes=[(16, 16), (32, 32)])

buf = io.BytesIO()
square(256).save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       'width="256" height="256" viewBox="0 0 256 256"><image width="256" height="256" '
       'xlink:href="data:image/png;base64,%s"/></svg>' % b64)
for rel in ["flutter/assets/icon.svg", "res/scalable.svg"]:
    with open(out(rel), "w", encoding="utf-8") as f:
        f.write(svg)
print("ok")


