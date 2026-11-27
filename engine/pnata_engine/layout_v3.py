"""Deterministic v0.3 typography and image-fit layout primitives.

This module performs layout only; it does not certify visual-policy compliance.
"""
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class LayoutV3Error(ValueError):
    """A requested text or image layout cannot be satisfied."""

@dataclass(frozen=True)
class TextLayout:
    lines: tuple
    font: object
    font_size: int
    line_height: int
    x: int
    y: int
    box_width: int
    box_height: int
    align: str
    valign: str
    clipped: bool = False

def _load_font(font_size, font_paths=()):
    size = max(1, int(font_size))
    for candidate in font_paths:
        if candidate and Path(candidate).is_file():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    # Pillow's default bitmap font historically ignored the requested size.
    # Use its scalable built-in Aileron/FreeType fallback where supported.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def _text_width(draw, text, font, stroke_width=0):
    if not text:
        return 0
    return draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)[2]

def _wrap_text(text, font, max_width, draw, stroke_width=0):
    """Wrap on whitespace; preserve explicit paragraph breaks."""
    result = []
    for paragraph in str(text).split("\n"):
        if paragraph == "":
            result.append("")
            continue
        words = paragraph.split()
        if not words:
            result.append("")
            continue
        line = words[0]
        if _text_width(draw, line, font, stroke_width) > max_width:
            raise LayoutV3Error("A single word is wider than the available text area.")
        for word in words[1:]:
            candidate = line + " " + word
            if _text_width(draw, candidate, font, stroke_width) <= max_width:
                line = candidate
            else:
                result.append(line)
                if _text_width(draw, word, font, stroke_width) > max_width:
                    raise LayoutV3Error("A single word is wider than the available text area.")
                line = word
        result.append(line)
    return result

def layout_text(text, box, font_size, font_paths=(), horizontal_align="left",
                vertical_align="top", line_spacing=1.2, padding=0,
                overflow="error", min_font_size=None, stroke_width=0):
    """Calculate wrapped text placement inside (x, y, width, height).

    overflow='error' rejects any overflow; 'clip' returns visible lines only;
    'shrink_to_fit' reduces the font no lower than min_font_size.
    """
    x, y, width, height = (int(v) for v in box)
    if width <= 0 or height <= 0:
        raise LayoutV3Error("Text box width and height must be positive.")
    if font_size <= 0 or padding < 0 or line_spacing <= 0:
        raise LayoutV3Error("Font size, padding, and line spacing must be positive (padding may be zero).")
    if horizontal_align not in {"left", "center", "right"}:
        raise LayoutV3Error("horizontal_align must be left, center, or right.")
    if vertical_align not in {"top", "middle", "bottom"}:
        raise LayoutV3Error("vertical_align must be top, middle, or bottom.")
    if overflow not in {"error", "clip", "shrink_to_fit"}:
        raise LayoutV3Error("Unsupported overflow policy.")
    available_w, available_h = width - 2 * int(padding), height - 2 * int(padding)
    if available_w <= 0 or available_h <= 0:
        raise LayoutV3Error("Padding leaves no usable text area.")
    min_size = int(min_font_size) if min_font_size is not None else int(font_size)
    if overflow == "shrink_to_fit" and (min_font_size is None or min_size <= 0 or min_size > int(font_size)):
        raise LayoutV3Error("shrink_to_fit requires min_font_size between 1 and font_size.")
    probe = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(probe)
    start_size = int(font_size)
    sizes = range(start_size, min_size - 1, -1) if overflow == "shrink_to_fit" else (start_size,)
    chosen = None
    for size in sizes:
        font = _load_font(size, font_paths)
        lines = _wrap_text(text, font, available_w, draw, int(stroke_width))
        ascent, descent = font.getmetrics()
        line_height = max(1, int((ascent + descent) * float(line_spacing)))
        fits = len(lines) * line_height <= available_h
        if fits:
            chosen = (lines, font, size, line_height, False)
            break
        if overflow != "shrink_to_fit":
            if overflow == "error":
                raise LayoutV3Error("Text exceeds its box height; enlarge the box or select an explicit overflow policy.")
            visible = max(0, available_h // line_height)
            chosen = (lines[:visible], font, size, line_height, True)
            break
    if chosen is None:
        raise LayoutV3Error("Text does not fit even at min_font_size.")
    lines, font, size, line_height, clipped = chosen
    text_h = len(lines) * line_height
    if vertical_align == "top":
        top = y + int(padding)
    elif vertical_align == "middle":
        top = y + (height - text_h) // 2
    else:
        top = y + height - int(padding) - text_h
    return TextLayout(tuple(lines), font, size, line_height, x + int(padding), top,
                      available_w, available_h, horizontal_align, vertical_align, clipped)

def draw_text_layout(canvas, text, layout, fill="#FFFFFF", stroke_width=0, stroke_fill="#000000"):
    """Draw a previously measured TextLayout onto an RGBA/RGB Pillow canvas."""
    draw = ImageDraw.Draw(canvas)
    for index, line in enumerate(layout.lines):
        bbox = draw.textbbox((0, 0), line, font=layout.font, stroke_width=int(stroke_width))
        tw = bbox[2] - bbox[0]
        if layout.align == "left":
            left = layout.x
        elif layout.align == "center":
            left = layout.x + (layout.box_width - tw) // 2
        else:
            left = layout.x + layout.box_width - tw
        top = layout.y + index * layout.line_height - bbox[1]
        draw.text((left, top), line, font=layout.font, fill=fill,
                  stroke_width=int(stroke_width), stroke_fill=stroke_fill)
    return canvas

def fit_image(source, box, mode="contain", anchor=(0.5, 0.5)):
    """Return an RGBA image exactly box-sized using deterministic fit/crop.

    contain preserves all pixels and leaves transparent padding; cover crops
    according to normalized anchor; stretch changes aspect ratio explicitly.
    """
    if not isinstance(source, Image.Image):
        source = Image.open(source)
    source = source.convert("RGBA")
    width, height = (int(v) for v in box)
    if width <= 0 or height <= 0:
        raise LayoutV3Error("Image target dimensions must be positive.")
    if mode not in {"contain", "cover", "stretch"}:
        raise LayoutV3Error("Image fit must be contain, cover, or stretch.")
    ax, ay = (float(v) for v in anchor)
    if not (0 <= ax <= 1 and 0 <= ay <= 1):
        raise LayoutV3Error("Image crop anchor values must be between 0 and 1.")
    if mode == "stretch":
        return source.resize((width, height), Image.Resampling.LANCZOS)
    sw, sh = source.size
    ratio = min(width / sw, height / sh) if mode == "contain" else max(width / sw, height / sh)
    rw, rh = max(1, round(sw * ratio)), max(1, round(sh * ratio))
    resized = source.resize((rw, rh), Image.Resampling.LANCZOS)
    if mode == "contain":
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        result.alpha_composite(resized, ((width-rw)//2, (height-rh)//2))
        return result
    left = round((rw - width) * ax)
    top = round((rh - height) * ay)
    return resized.crop((left, top, left + width, top + height))
