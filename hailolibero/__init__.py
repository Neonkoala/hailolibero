import importlib.metadata

from .hailolibero import HailoLibero

__all__ = [
    "HailoLibero"
]

__version__ = importlib.metadata.version("hailolibero")
