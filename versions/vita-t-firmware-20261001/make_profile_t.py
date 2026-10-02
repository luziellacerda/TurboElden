"""Build the default profile avatar: circular Turborama T, no Sambox S."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets" / "turborama-icon-v2.png"
OUT = ROOT / "assets" / "profile_mockup.png"
SIZE = 512
GREEN = (108, 245, 69, 255)  # Turborama #6CF545
RED = (225, 16, 16, 255)


def trim_letter(img: Image.Image) -> Image.Image:
    mask = img.convert("L").point(lambda p: 255 if p > 18 else 0)
    box = mask.getbbox()
    if not box:
        raise RuntimeError("T letter not found in brand icon")
    pad = 4
    x0 = max(box[0] - pad, 0)
    y0 = max(box[1] - pad, 0)
    x1 = min(box[2] + pad, img.width)
    y1 = min(box[3] + pad, img.height)
    return img.crop((x0, y0, x1, y1))


def main() -> None:
    letter = trim_letter(Image.open(SRC).convert("RGBA"))
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
    # Fit the T inside the inner circle; header avatar is ~70 px so the letter stays large.
    inner = int(SIZE * 0.62)
    scale = min(inner / letter.width, inner / letter.height)
    tw = max(1, int(letter.width * scale))
    th = max(1, int(letter.height * scale))
    fitted = letter.resize((tw, th), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((SIZE - tw) // 2, (SIZE - th) // 2), fitted)

    ring = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ring)
    m = 14
    draw.ellipse([m, m, SIZE - 1 - m, SIZE - 1 - m], outline=GREEN, width=18)
    inner_m = m + 20
    draw.ellipse(
        [inner_m, inner_m, SIZE - 1 - inner_m, SIZE - 1 - inner_m],
        outline=(225, 16, 16, 220),
        width=4,
    )
    # Soften the ring so it matches the glossy T.
    ring = ring.filter(ImageFilter.GaussianBlur(0.6))
    canvas = Image.alpha_composite(canvas, ring)
    canvas.save(OUT, "PNG")
    print("wrote", OUT, "size", canvas.size, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
