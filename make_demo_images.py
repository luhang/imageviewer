"""生成示例图片，供 image_viewer.py 演示使用。

运行：
    python make_demo_images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def gradient(size: tuple[int, int], c1: tuple[int, int, int], c2: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        color = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = color
    return img


def draw_text(img: Image.Image, text: str) -> Image.Image:
    d = ImageDraw.Draw(img)
    w, h = img.size
    try:
        font = ImageFont.truetype("arial.ttf", size=48)
    except OSError:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((w - tw) / 2 - bbox[0], (h - th) / 2 - bbox[1]), text, fill=(255, 255, 255), font=font)
    return img


def circles(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, (30, 30, 60))
    d = ImageDraw.Draw(img)
    colors = [(255, 99, 132), (255, 205, 86), (54, 162, 235), (102, 255, 178), (200, 130, 255)]
    r = min(w, h) // 3
    import math
    for i, (cx, cy) in enumerate([(w // 4, h // 4), (3 * w // 4, h // 3),
                                  (w // 2, 2 * h // 3), (w // 5, 3 * h // 4),
                                  (4 * w // 5, 3 * h // 4)]):
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                  fill=colors[i % len(colors)])
    return img


def checker(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(img)
    cell = 40
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2 == 0:
                d.rectangle([x, y, x + cell, y + cell], fill=(20, 20, 20))
    return img


def main() -> None:
    out = Path(__file__).parent / "demo_images"
    out.mkdir(exist_ok=True)

    # 1) 横向渐变图
    draw_text(gradient((1200, 800), (0, 120, 200), (255, 80, 120)), "横图 1200x800").save(out / "01_渐变_横图.png")

    # 2) 纵向渐变图
    draw_text(gradient((800, 1200), (60, 40, 140), (0, 200, 160)), "竖图 800x1200").save(out / "02_渐变_竖图.png")

    # 3) 圆形彩色图
    draw_text(circles((1000, 1000)), "彩色圆点 方形").save(out / "03_圆点.png")

    # 4) 棋盘格图
    draw_text(checker((900, 600)), "棋盘格 900x600").save(out / "04_棋盘格.png")

    print("已生成示例图片到:", out)
    for p in sorted(out.iterdir()):
        print(" -", p.name)


if __name__ == "__main__":
    main()