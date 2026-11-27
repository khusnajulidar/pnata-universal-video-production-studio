import pytest
from PIL import Image
from pnata_engine.layout_v3 import LayoutV3Error, layout_text, draw_text_layout, fit_image

def test_text_wraps_and_aligns():
    text = "This heading is deliberately much longer so it must wrap across multiple lines"
    layout = layout_text(text, (0, 0, 120, 180), 18,
                         horizontal_align="center", vertical_align="middle")
    assert len(layout.lines) > 1
    assert " ".join(layout.lines) == text
    assert layout.align == "center"
    assert layout.y > 0

def test_overflow_error_is_explicit():
    with pytest.raises(LayoutV3Error, match="exceeds its box"):
        layout_text("This is a long paragraph that cannot fit", (0, 0, 150, 12), 20)

def test_shrink_to_fit_respects_minimum():
    layout = layout_text("A long but manageable line of text", (0, 0, 180, 45), 24,
                         overflow="shrink_to_fit", min_font_size=8)
    assert 8 <= layout.font_size <= 24

def test_shrink_to_fit_fails_if_minimum_is_too_large():
    with pytest.raises(LayoutV3Error, match="min_font_size"):
        layout_text("text", (0, 0, 100, 30), 20, overflow="shrink_to_fit", min_font_size=21)

def test_clip_is_explicit_and_reported():
    layout = layout_text("one two three four five six", (0, 0, 60, 12), 16, overflow="clip")
    assert layout.clipped is True
    assert len(layout.lines) == 0

def test_draw_text_layout_returns_canvas():
    canvas = Image.new("RGBA", (160, 80), (0, 0, 0, 0))
    layout = layout_text("Hello layout", (0, 0, 160, 80), 20)
    assert draw_text_layout(canvas, "ignored", layout) is canvas
    assert canvas.getbbox() is not None

def test_contain_preserves_full_image_and_transparent_padding():
    source = Image.new("RGBA", (100, 50), (255, 0, 0, 255))
    result = fit_image(source, (50, 50), "contain")
    assert result.size == (50, 50)
    assert result.getpixel((25, 0))[3] == 0
    assert result.getpixel((25, 25))[3] == 255

def test_cover_crops_to_target_and_honors_anchor():
    source = Image.new("RGBA", (100, 50), (255, 0, 0, 255))
    result = fit_image(source, (50, 50), "cover", anchor=(1, 0.5))
    assert result.size == (50, 50)
    assert result.getpixel((0, 0))[3] == 255

def test_stretch_and_invalid_anchor():
    source = Image.new("RGBA", (100, 50), (0, 255, 0, 255))
    assert fit_image(source, (40, 60), "stretch").size == (40, 60)
    with pytest.raises(LayoutV3Error, match="anchor"):
        fit_image(source, (40, 60), "cover", anchor=(2, 0.5))
