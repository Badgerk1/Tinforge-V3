from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

BOUNDARY_NEIGHBOR = -1
AREA_TOLERANCE_FACTOR = 1e-12


class TINValidationError(ValueError):
    """Raised when a TIN violates canonical geometry or topology rules."""


class NonManifoldTINError(TINValidationError):
    """Raised when more than two triangles share the same undirected edge."""


@dataclass(frozen=True)
class SurfaceVertex:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SurfaceTriangle:
    vertices: tuple[int, int, int]
    neighbors: tuple[int, int, int] = (
        BOUNDARY_NEIGHBOR,
        BOUNDARY_NEIGHBOR,
        BOUNDARY_NEIGHBOR,
    )


@dataclass(frozen=True)
class SurfaceTIN:
    name: str
    origin_x: float
    origin_y: float
    vertices: tuple[SurfaceVertex, ...]
    triangles: tuple[SurfaceTriangle, ...]


@dataclass(frozen=True)
class _EdgeReference:
    triangle_index: int
    edge_index: int


def triangle_edges(vertex_indices: tuple[int, int, int]) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    a, b, c = vertex_indices
    return ((a, b), (b, c), (c, a))


def xy_area_tolerance(vertices: tuple[SurfaceVertex, ...]) -> float:
    """Return an absolute XY twice-area tolerance scaled to the local coordinate magnitudes."""
    max_xy_magnitude = max(
        1.0,
        *(max(abs(vertex.x), abs(vertex.y)) for vertex in vertices),
    )
    return (max_xy_magnitude * max_xy_magnitude) * AREA_TOLERANCE_FACTOR


def triangle_twice_area_xy(
    vertices: tuple[SurfaceVertex, ...],
    triangle: SurfaceTriangle,
) -> float:
    a_index, b_index, c_index = triangle.vertices
    a = vertices[a_index]
    b = vertices[b_index]
    c = vertices[c_index]
    return ((b.x - a.x) * (c.y - a.y)) - ((b.y - a.y) * (c.x - a.x))


def build_triangle_adjacency(
    vertex_count: int,
    triangle_vertices: tuple[tuple[int, int, int], ...] | list[tuple[int, int, int]],
) -> tuple[SurfaceTriangle, ...]:
    triangles = tuple(tuple(vertices) for vertices in triangle_vertices)
    for triangle_index, vertices in enumerate(triangles):
        _validate_vertex_indexes(vertices, vertex_count, triangle_index)

    edge_map = _build_edge_map(triangles)
    neighbors = [
        [BOUNDARY_NEIGHBOR, BOUNDARY_NEIGHBOR, BOUNDARY_NEIGHBOR]
        for _ in triangles
    ]
    for references in edge_map.values():
        if len(references) == 2:
            left, right = references
            neighbors[left.triangle_index][left.edge_index] = right.triangle_index
            neighbors[right.triangle_index][right.edge_index] = left.triangle_index

    return tuple(
        SurfaceTriangle(vertices=vertices, neighbors=tuple(neighbor_indexes))
        for vertices, neighbor_indexes in zip(triangles, neighbors, strict=True)
    )


def validate_tin(surface: SurfaceTIN, *, area_tolerance: float | None = None) -> None:
    if not isfinite(surface.origin_x) or not isfinite(surface.origin_y):
        raise TINValidationError("surface origin must be finite")
    if not surface.vertices:
        raise TINValidationError("surface must contain at least one vertex")
    if not surface.triangles:
        raise TINValidationError("surface must contain at least one triangle")

    for vertex_index, vertex in enumerate(surface.vertices):
        if not (isfinite(vertex.x) and isfinite(vertex.y) and isfinite(vertex.z)):
            raise TINValidationError(f"vertex {vertex_index} must contain only finite coordinates")

    resolved_area_tolerance = (
        xy_area_tolerance(surface.vertices)
        if area_tolerance is None
        else area_tolerance
    )
    if resolved_area_tolerance < 0.0:
        raise TINValidationError("area tolerance must be non-negative")

    raw_triangles = tuple(triangle.vertices for triangle in surface.triangles)
    edge_map = _build_edge_map(raw_triangles)

    for triangle_index, triangle in enumerate(surface.triangles):
        _validate_vertex_indexes(triangle.vertices, len(surface.vertices), triangle_index)
        for neighbor_index in triangle.neighbors:
            if neighbor_index != BOUNDARY_NEIGHBOR and not 0 <= neighbor_index < len(surface.triangles):
                raise TINValidationError(
                    f"triangle {triangle_index} references invalid neighbor {neighbor_index}"
                )

        twice_area = abs(triangle_twice_area_xy(surface.vertices, triangle))
        if twice_area <= resolved_area_tolerance:
            raise TINValidationError(
                "triangle "
                f"{triangle_index} is degenerate or near-degenerate in XY "
                f"(abs(twice_area)={twice_area:.3e}, tolerance={resolved_area_tolerance:.3e})"
            )

    for edge_key, references in edge_map.items():
        if len(references) == 1:
            reference = references[0]
            neighbor_index = surface.triangles[reference.triangle_index].neighbors[reference.edge_index]
            if neighbor_index != BOUNDARY_NEIGHBOR:
                raise TINValidationError(
                    f"boundary edge {edge_key} on triangle {reference.triangle_index} must use neighbor -1"
                )
            continue

        left, right = references
        left_neighbor = surface.triangles[left.triangle_index].neighbors[left.edge_index]
        right_neighbor = surface.triangles[right.triangle_index].neighbors[right.edge_index]
        if left_neighbor == BOUNDARY_NEIGHBOR or right_neighbor == BOUNDARY_NEIGHBOR:
            raise TINValidationError(
                f"shared edge {edge_key} is missing reciprocal neighbor references"
            )
        if left_neighbor != right.triangle_index or right_neighbor != left.triangle_index:
            raise TINValidationError(
                "shared edge "
                f"{edge_key} has non-reciprocal or incorrect neighbor references "
                f"({left.triangle_index}->{left_neighbor}, {right.triangle_index}->{right_neighbor})"
            )


def _build_edge_map(
    triangles: tuple[tuple[int, int, int], ...],
) -> dict[tuple[int, int], list[_EdgeReference]]:
    edge_map: dict[tuple[int, int], list[_EdgeReference]] = {}
    for triangle_index, triangle_vertices in enumerate(triangles):
        for edge_index, edge in enumerate(triangle_edges(triangle_vertices)):
            key = tuple(sorted(edge))
            references = edge_map.setdefault(key, [])
            references.append(_EdgeReference(triangle_index=triangle_index, edge_index=edge_index))
            if len(references) > 2:
                raise NonManifoldTINError(
                    f"edge {key} is shared by more than two triangles"
                )
    return edge_map


def _validate_vertex_indexes(
    vertex_indexes: tuple[int, int, int],
    vertex_count: int,
    triangle_index: int,
) -> None:
    if len(set(vertex_indexes)) != 3:
        raise TINValidationError(
            f"triangle {triangle_index} reuses a vertex index and is degenerate"
        )
    for vertex_index in vertex_indexes:
        if not 0 <= vertex_index < vertex_count:
            raise TINValidationError(
                f"triangle {triangle_index} references invalid vertex {vertex_index}"
            )
