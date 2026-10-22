"""
Renders posts from content/posts.json into Instagram-ready images (1080x1350).

  python generate.py          -> renders the NEXT post only (used by the automation)
  python generate.py --all    -> renders every post into output/ so you can preview them
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUT = ROOT / "output"
PREVIEW = ROOT / "preview"

W, H = 1080, 1350
MARGIN = 96


def load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"Poppins-{weight}.ttf"), size)


def wrap(text, fnt, max_width):
    """Wrap text to fit max_width. Keeps the line breaks written in the content."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for word in paragraph.split():
            trial = f"{current} {word}".strip()
            if fnt.getlength(trial) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def text_block_height(lines, fnt, line_gap):
    asc, desc = fnt.getmetrics()
    lh = asc + desc + line_gap
    blank = lh // 2
    return sum(blank if not ln else lh for ln in lines)


def draw_lines(draw, lines, fnt, x, y, fill, line_gap):
    asc, desc = fnt.getmetrics()
    lh = asc + desc + line_gap
    for ln in lines:
        if not ln:
            y += lh // 2
            continue
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def render(post, number, cfg):
    c = cfg["colors"]
    img = Image.new("RGB", (W, H), c["background"])
    d = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN

    # Top: accent bar + label + post number
    d.rectangle([MARGIN, MARGIN, MARGIN + 70, MARGIN + 8], fill=c["accent"])
    label_font = font("Medium", 32)
    d.text((MARGIN, MARGIN + 34), post["label"], font=label_font, fill=c["accent"])
    num = f"#{number:02d}"
    d.text((W - MARGIN - label_font.getlength(num), MARGIN + 34), num,
           font=label_font, fill=c["footer"])

    # Footer
    footer_font = font("Medium", 30)
    footer_y = H - MARGIN - 30
    d.line([MARGIN, footer_y - 36, W - MARGIN, footer_y - 36], fill=c["footer"], width=2)
    d.text((MARGIN, footer_y - 8), cfg["page_name"], font=footer_font, fill=c["title"])
    handle = cfg["handle"]
    d.text((W - MARGIN - footer_font.getlength(handle), footer_y - 8), handle,
           font=footer_font, fill=c["footer"])

    # Space available for title + body
    top = MARGIN + 140
    bottom = footer_y - 80
    available = bottom - top

    # Shrink sizes until everything fits
    for title_size, body_size in [(92, 44), (84, 42), (76, 40), (68, 38), (62, 36), (56, 34), (50, 32)]:
        tf, bf = font("Bold", title_size), font("Regular", body_size)
        t_lines = wrap(post["title"], tf, max_w)
        b_lines = wrap(post["body"], bf, max_w)
        t_h = text_block_height(t_lines, tf, 4)
        b_h = text_block_height(b_lines, bf, 14)
        total = t_h + 60 + b_h
        if total <= available:
            break

    # Vertically center the block in the available space
    y = top + max(0, (available - total) // 2)
    y = draw_lines(d, t_lines, tf, MARGIN, y, c["title"], 4)
    y += 18
    d.rectangle([MARGIN, y, MARGIN + 120, y + 6], fill=c["accent"])
    y += 42
    draw_lines(d, b_lines, bf, MARGIN, y, c["body"], 14)
    return img


def build_caption(post, cfg):
    return f"{post['title']}\n\n{post['caption']}\n\n{cfg['hashtags']}".strip()


def main():
    cfg = load_json("config.json")
    posts = load_json("content/posts.json")
    OUT.mkdir(exist_ok=True)

    if "--all" in sys.argv:
        PREVIEW.mkdir(exist_ok=True)
        for i, p in enumerate(posts):
            render(p, i + 1, cfg).save(PREVIEW / f"post_{i + 1:03d}.png")
        print(f"Rendered {len(posts)} posts into preview/")
        return

    state = load_json("state.json")
    i = state["next_index"]
    if i >= len(posts):
        if cfg.get("when_all_posts_used") == "repeat":
            i = i % len(posts)
        else:
            print("All posts have been used. Add more to content/posts.json. Nothing posted today.")
            (OUT / "next.json").write_text(json.dumps({"skip": True}), encoding="utf-8")
            return

    post = posts[i]
    filename = f"post_{i + 1:03d}.png"
    render(post, i + 1, cfg).save(OUT / filename)
    meta = {"skip": False, "index": state["next_index"], "image": f"output/{filename}",
            "caption": build_caption(post, cfg)}
    (OUT / "next.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered post {i + 1}: {post['title']}")


if __name__ == "__main__":
    main()
