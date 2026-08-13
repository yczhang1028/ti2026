#!/usr/bin/env python3
"""TI2026 战报公众号封面 — Dota 风红金几何抽象 (Pillow, 无文字)"""
from PIL import Image, ImageDraw, ImageFilter
import math, random

W, H = 900, 500
img = Image.new("RGB", (W, H), (10, 13, 26))
d = ImageDraw.Draw(img, "RGBA")

# 背景径向渐变 (深蓝 -> 深红金)
for y in range(H):
    t = y / H
    r = int(10 + (30 - 10) * t)
    g = int(13 + (18 - 13) * t)
    b = int(26 + (48 - 26) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b, 255))

# 光晕
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([W*0.55, -H*0.3, W*1.15, H*0.7], fill=(245, 192, 74, 60))
gd.ellipse([-W*0.3, H*0.4, W*0.4, H*1.2], fill=(255, 77, 94, 45))
gd.ellipse([W*0.15, -H*0.2, W*0.75, H*0.5], fill=(56, 224, 208, 30))
glow = glow.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img.convert("RGBA"), glow)

d = ImageDraw.Draw(img, "RGBA")

# 网格
for x in range(0, W, 60):
    d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
for y in range(0, H, 60):
    d.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)

# 中央 Aegis 盾牌 (抽象几何)
cx, cy = W * 0.42, H * 0.5
pts = [(cx, cy-150), (cx+90, cy-110), (cx+110, cy-10), (cx+60, cy+130),
       (cx, cy+160), (cx-60, cy+130), (cx-110, cy-10), (cx-90, cy-110)]
d.polygon(pts, fill=(20, 24, 45, 255), outline=(245, 192, 74, 220), width=4)
# 盾牌内纹
d.polygon(pts, outline=(245, 192, 74, 80), width=8)
# 中心菱形
d.polygon([(cx, cy-70), (cx+45, cy), (cx, cy+70), (cx-45, cy)],
          outline=(245, 192, 74, 200), width=3)
d.polygon([(cx, cy-35), (cx+22, cy), (cx, cy+35), (cx-22, cy)],
          fill=(245, 192, 74, 90))

# 右侧数据节点 + 连线 (抽象电竞)
random.seed(42)
nodes = []
for i in range(14):
    nx = W * 0.68 + random.random() * W * 0.27
    ny = H * 0.12 + random.random() * H * 0.76
    nodes.append((nx, ny))
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        if random.random() < 0.18:
            d.line([nodes[i], nodes[j]], fill=(56, 224, 208, 40), width=1)
for (nx, ny) in nodes:
    r = random.randint(4, 9)
    col = (245, 192, 74, 200) if random.random() < 0.5 else (255, 77, 94, 190)
    d.ellipse([nx-r, ny-r, nx+r, ny+r], fill=col)

# 底部金色粒子带
for i in range(40):
    px = random.random() * W
    py = H * 0.82 + random.random() * H * 0.16
    r = random.randint(1, 3)
    d.ellipse([px-r, py-r, px+r, py+r], fill=(245, 192, 74, 120))

out = "/home/ubuntu/hermes_share/ti2026/cover_ti2026.png"
img.convert("RGB").save(out, quality=92)
print("封面已生成:", out)
