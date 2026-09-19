"""Tinforge V3."""

from .surface import (
    SurfaceTIN,
    TinValidationError,
    Triangle,
    Vertex,
    build_triangle_adjacency,
    validate_tin,
    with_deterministic_adjacency,
)

__all__ = [
    "SurfaceTIN",
    "TinValidationError",
    "Triangle",
    "Vertex",
    "build_triangle_adjacency",
    "validate_tin",
    "with_deterministic_adjacency",
]
