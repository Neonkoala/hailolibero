from pathlib import Path

from .hailolibero import HailoLibero

__all__ = [
    "HailoLibero"
]

__version__ = (Path(__file__).parent / "VERSION").read_text().strip()
