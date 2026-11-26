"""Explicit backend capability declarations; availability is detected separately."""
from dataclasses import dataclass

@dataclass(frozen=True)
class BackendCapabilities:
    name: str
    visual_types: tuple
    animation_properties: tuple
    transitions: tuple
    audio: tuple
    status: str
    limitations: tuple

BACKENDS = {
    "ffmpeg-pillow-2d": BackendCapabilities(
        name="FFmpeg + Pillow 2D compositor",
        visual_types=("text","rect","ellipse","line","reviewed-still-image"),
        animation_properties=("x","y","scale","opacity","rotation"),
        transitions=("cut","dissolve"),
        audio=(),
        status="implemented; requires Pillow and FFmpeg",
        limitations=("2D raster compositor only","no 3D camera or lighting",
                    "no nonlinear footage editing","no advanced particle system",
                    "no audio mixing in v0.2 renderer","visual-policy review is human, not automated")
    )
}

def describe_backend(name):
    if name not in BACKENDS:
        raise ValueError(f"Unknown backend: {name}")
    item=BACKENDS[name]
    return {key:getattr(item,key) for key in item.__dataclass_fields__}
