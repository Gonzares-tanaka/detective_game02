"""Prepare a shared Pyxel palette and contact sheet without altering source PNGs.

Requires Pillow only at preparation time. Runtime keeps 16 UI colors and adds
240 artwork colors; the original attached PNGs stay byte-for-byte unchanged.
"""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from main import PALETTE
from novel import load_story


def prepare():
    data = load_story(ROOT / "story.json")
    pictures = []
    for key, name in data["backgrounds"].items():
        with Image.open(ROOT / name) as source:
            if source.size != (256, 100):
                raise ValueError(f"{name}: 256x100ピクセルにしてください")
            rgba = source.convert("RGBA")
            picture = Image.new("RGBA", rgba.size, (16, 24, 34, 255))
            picture.alpha_composite(rgba)
            pictures.append((key, name, picture.convert("RGB")))
    strip = Image.new("RGB", (256, 100 * len(pictures)))
    for index, (_, _, picture) in enumerate(pictures):
        strip.paste(picture, (0, index * 100))
    quantized = strip.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
    triples = quantized.getpalette()[:240 * 3]
    colors = [(triples[i] << 16) | (triples[i + 1] << 8) | triples[i + 2]
              for i in range(0, len(triples), 3)]
    (ROOT / "assets/background_palette.json").write_text(
        json.dumps(colors, indent=2) + "\n", encoding="utf-8", newline="\n")
    font = ImageFont.truetype(str(ROOT / "assets/PixelMplus12-Regular.ttf"), 12)
    sheet = Image.new("RGB", (256 * 3, 122 * ((len(pictures) + 2) // 3)), "#101822")
    draw = ImageDraw.Draw(sheet)
    for index, (key, _, picture) in enumerate(pictures):
        x, y = index % 3 * 256, index // 3 * 122
        sheet.paste(picture, (x, y))
        draw.text((x + 6, y + 103), key, font=font, fill="#f3e7cc")
    output = ROOT / "verification"
    output.mkdir(exist_ok=True)
    sheet.save(output / "backgrounds.png")
    report = {"backgrounds": len(pictures), "ui_colors": len(PALETTE),
              "artwork_colors": len(colors), "total_palette_colors": len(PALETTE) + len(colors),
              "png_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                             for _, name, _ in pictures}}
    (output / "artwork_palette_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(pictures)} backgrounds; {len(PALETTE) + len(colors)} colors. PNG files unchanged.")


if __name__ == "__main__":
    prepare()
