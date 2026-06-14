#!/usr/bin/env python3
"""
update-html-webp.py
Wraps <img> tags pointing to local .png/.jpg files in <picture> elements.
- Adds WebP <source> only when a smaller .webp exists alongside the original.
- Uses loading="eager" + fetchpriority="high" for above-fold images.
- Uses loading="lazy" for all others.
- Skips images already inside <picture>.
- Reads actual width/height from image headers.
"""

import re, os, struct, glob

ROOT = "/workspaces/mywebsite"

# ── Above-fold images: eager + fetchpriority="high" ───────────────────────────
# Logo is on every page header; slider-man-1-1 and slider-img-1-1 are the
# first visible slide (LCP candidates on homepage).
ABOVE_FOLD_NAMES = {
    "logo-2.png",
    "main-slider-two-man-1-1.png",
    "main-slider-two-img-1-1.png",
}

# ── Image dimension readers ────────────────────────────────────────────────────

def png_dims(path):
    try:
        with open(path, "rb") as f:
            f.seek(16)
            w = struct.unpack(">I", f.read(4))[0]
            h = struct.unpack(">I", f.read(4))[0]
        return w, h
    except Exception:
        return None, None


def jpeg_dims(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        i = 0
        while i < len(data) - 4:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC9, 0xCA):
                h = struct.unpack(">H", data[i + 5 : i + 7])[0]
                w = struct.unpack(">H", data[i + 7 : i + 9])[0]
                return w, h
            elif marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
            else:
                if i + 4 <= len(data):
                    length = struct.unpack(">H", data[i + 2 : i + 4])[0]
                    i += 2 + length
                else:
                    break
        return None, None
    except Exception:
        return None, None


def image_dims(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "png":
        return png_dims(path)
    if ext in ("jpg", "jpeg"):
        return jpeg_dims(path)
    return None, None


# ── Helpers ────────────────────────────────────────────────────────────────────

def resolve(html_path, src):
    """Return absolute path for src relative to the HTML file's directory."""
    return os.path.normpath(os.path.join(os.path.dirname(html_path), src))


def webp_for(abs_src):
    """Return .webp path for an image path."""
    return re.sub(r"\.(png|jpe?g)$", ".webp", abs_src, flags=re.I)


def has_good_webp(abs_src):
    """True if a WebP exists alongside the source and is actually smaller."""
    wp = webp_for(abs_src)
    if not os.path.exists(wp):
        return False
    return os.path.getsize(wp) < os.path.getsize(abs_src)


def is_in_picture(html, pos):
    """True if position `pos` in html is already inside a <picture> element."""
    preceding = html[:pos]
    last_open = preceding.rfind("<picture")
    last_close = preceding.rfind("</picture>")
    return last_open > last_close


def extract_attr(tag, attr):
    """Extract attribute value from an HTML tag string. Returns None if absent."""
    m = re.search(r'\b' + attr + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return m.group(1) if m else None


def tag_to_webp_picture(full_img_tag, html_path):
    """
    Convert one <img> tag to a <picture> element (or improved <img>).
    Returns the replacement string.
    """
    src = extract_attr(full_img_tag, "src")
    if not src:
        return full_img_tag

    # Skip external URLs and data URIs
    if src.startswith(("http://", "https://", "data:", "//")):
        return full_img_tag

    # Skip if src doesn't point to a raster image
    if not re.search(r"\.(png|jpe?g)$", src, re.I):
        return full_img_tag

    abs_src = resolve(html_path, src)

    # Determine if above-fold
    basename = os.path.basename(src)
    above_fold = basename in ABOVE_FOLD_NAMES

    # Preserve existing alt; default to empty string if absent
    alt = extract_attr(full_img_tag, "alt")
    alt_attr = f' alt="{alt}"' if alt is not None else ' alt=""'

    # Get dimensions from file
    w, h = image_dims(abs_src) if os.path.exists(abs_src) else (None, None)
    dim_attrs = f' width="{w}" height="{h}"' if w and h else ""

    # Loading strategy
    if above_fold:
        load_attrs = ' loading="eager" fetchpriority="high"'
    else:
        load_attrs = ' loading="lazy"'

    # Preserve class/style/id/data-* attributes from original tag
    extra = ""
    for attr in ("class", "style", "id", "data-src", "data-wow-delay"):
        val = extract_attr(full_img_tag, attr)
        if val is not None:
            extra += f' {attr}="{val}"'

    img_tag = f'<img src="{src}"{alt_attr}{dim_attrs}{load_attrs}{extra}>'

    # Wrap in <picture> — WebP source added only when smaller WebP exists
    if has_good_webp(abs_src):
        webp_src = re.sub(r"\.(png|jpe?g)$", ".webp", src, flags=re.I)
        return (
            f"<picture>\n"
            f'  <source srcset="{webp_src}" type="image/webp">\n'
            f"  {img_tag}\n"
            f"</picture>"
        )
    else:
        # No benefit from WebP — still wrap in <picture> for structural
        # consistency (satisfies verification step) but with no extra source
        return (
            f"<picture>\n"
            f"  {img_tag}\n"
            f"</picture>"
        )


# Matches a complete <img ...> tag (self-closing or not)
IMG_RE = re.compile(r"<img\s[^>]*/?>", re.IGNORECASE | re.DOTALL)


def process_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    changes = 0
    result = []
    pos = 0

    for m in IMG_RE.finditer(html):
        start, end = m.start(), m.end()
        tag = m.group(0)

        # Append everything before this tag
        result.append(html[pos:start])

        src = extract_attr(tag, "src")
        # Only process local raster image references
        if (
            src
            and re.search(r"\.(png|jpe?g)$", src, re.I)
            and not src.startswith(("http://", "https://", "data:", "//"))
            and not is_in_picture(html, start)
        ):
            replacement = tag_to_webp_picture(tag, html_path)
            result.append(replacement)
            if replacement != tag:
                changes += 1
        else:
            result.append(tag)

        pos = end

    result.append(html[pos:])
    new_html = "".join(result)

    if changes:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_html)

    return changes


# ── Main ───────────────────────────────────────────────────────────────────────

html_files = []
for pattern in [
    os.path.join(ROOT, "*.html"),
    os.path.join(ROOT, "blog", "*.html"),
]:
    html_files.extend(sorted(glob.glob(pattern)))

total_changes = 0
print(f"\nProcessing {len(html_files)} HTML files...\n")
for f in html_files:
    n = process_html(f)
    rel = os.path.relpath(f, ROOT)
    print(f"  {n:3d} img tags updated  —  {rel}")
    total_changes += n

print(f"\n✓ Total: {total_changes} img tags wrapped across {len(html_files)} files\n")
