"""Canonical TIN structures and deterministic topology validation."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Vertex:
    """Canonical local/project-space vertex coordinate."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Triangle:
    """Triangle with vertex indices and optional neighbor triangle indices."""

    vertex_indices: tuple[int, int, int]
    neighbor_indices: tuple[int | None, int | None, int | None] = (None, None, None)


@dataclass(frozen=True)
class SurfaceTIN:
    """Canonical TIN surface independent from any TP3 serialization."""

    name: str
    vertices: tuple[Vertex, ...]
    triangles: tuple[Triangle, ...]


class TinValidationError(ValueError):
    """Raised when a TIN fails deterministic validation gates."""


def _triangle_xy_double_area(vertices: Sequence[Vertex], tri: Triangle) -> float:
    ia, ib, ic = tri.vertex_indices
    a, b, c = vertices[ia], vertices[ib], vertices[ic]
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def build_triangle_adjacency(vertex_index_triplets: Iterable[tuple[int, int, int]]) -> tuple[tuple[int | None, int | None, int | None], ...]:
    """Build deterministic neighbors for edges (v0,v1), (v1,v2), (v2,v0)."""

    triplets = tuple(vertex_index_triplets)
    neighbors: list[list[int | None]] = [[None, None, None] for _ in triplets]
    edge_to_refs: dict[tuple[int, int], list[tuple[int, int]]] = {}

    for tri_idx, (a, b, c) in enumerate(triplets):
        edges = ((a, b), (b, c), (c, a))
        for edge_slot, (u, v) in enumerate(edges):
            key = (u, v) if u < v else (v, u)
            edge_to_refs.setdefault(key, []).append((tri_idx, edge_slot))

    for key, refs in edge_to_refs.items():
        if len(refs) == 1:
            continue
        if len(refs) > 2:
            raise TinValidationError(f"non-manifold edge {key} shared by {len(refs)} triangles")
        (a_tri, a_slot), (b_tri, b_slot) = refs
        neighbors[a_tri][a_slot] = b_tri
        neighbors[b_tri][b_slot] = a_tri

    return tuple((row[0], row[1], row[2]) for row in neighbors)


def with_deterministic_adjacency(surface: SurfaceTIN) -> SurfaceTIN:
    """Return a copy of surface with deterministic triangle neighbor references."""

    adjacency = build_triangle_adjacency(tri.vertex_indices for tri in surface.triangles)
    triangles = tuple(
        Triangle(vertex_indices=tri.vertex_indices, neighbor_indices=adj)
        for tri, adj in zip(surface.triangles, adjacency)
    )
    return SurfaceTIN(name=surface.name, vertices=surface.vertices, triangles=triangles)


def validate_tin(surface: SurfaceTIN, *, require_neighbors: bool = True) -> None:
    """Validate index bounds, geometry, and adjacency invariants."""

    if not surface.vertices:
        raise TinValidationError("TIN must contain at least one vertex")
    if not surface.triangles:
        raise TinValidationError("TIN must contain at least one triangle")

    for i, vertex in enumerate(surface.vertices):
        if not (math.isfinite(vertex.x) and math.isfinite(vertex.y) and math.isfinite(vertex.z)):
            raise TinValidationError(f"vertex {i} has non-finite coordinate")

    edge_counts: dict[tuple[int, int], int] = {}

    for tri_idx, tri in enumerate(surface.triangles):
        if len(set(tri.vertex_indices)) != 3:
            raise TinValidationError(f"triangle {tri_idx} repeats one or more vertex indices")

        for vertex_idx in tri.vertex_indices:
            if vertex_idx < 0 or vertex_idx >= len(surface.vertices):
                raise TinValidationError(f"triangle {tri_idx} references out-of-range vertex {vertex_idx}")

        if _triangle_xy_double_area(surface.vertices, tri) == 0.0:
            raise TinValidationError(f"triangle {tri_idx} has zero XY area")

        a, b, c = tri.vertex_indices
        for edge in ((a, b), (b, c), (c, a)):
            key = edge if edge[0] < edge[1] else (edge[1], edge[0])
            edge_counts[key] = edge_counts.get(key, 0) + 1

        if require_neighbors:
            for slot, neighbor in enumerate(tri.neighbor_indices):
                if neighbor is None:
                    continue
                if neighbor < 0 or neighbor >= len(surface.triangles):
                    raise TinValidationError(
                        f"triangle {tri_idx} has out-of-range neighbor {neighbor} in slot {slot}"
                    )

    for edge, count in edge_counts.items():
        if count > 2:
            raise TinValidationError(f"non-manifold edge {edge} shared by {count} triangles")

    if require_neighbors:
        for tri_idx, tri in enumerate(surface.triangles):
            tri_edges = (
                (tri.vertex_indices[0], tri.vertex_indices[1]),
                (tri.vertex_indices[1], tri.vertex_indices[2]),
                (tri.vertex_indices[2], tri.vertex_indices[0]),
            )
            for edge_slot, neighbor_idx in enumerate(tri.neighbor_indices):
                if neighbor_idx is None:
                    continue
                neighbor = surface.triangles[neighbor_idx]
                edge = tri_edges[edge_slot]
                edge_key = edge if edge[0] < edge[1] else (edge[1], edge[0])

                reciprocal_found = False
                neighbor_edges = (
                    (neighbor.vertex_indices[0], neighbor.vertex_indices[1]),
                    (neighbor.vertex_indices[1], neighbor.vertex_indices[2]),
                    (neighbor.vertex_indices[2], neighbor.vertex_indices[0]),
                )
                for neighbor_slot, neighbor_edge in enumerate(neighbor_edges):
                    neighbor_edge_key = (
                        neighbor_edge if neighbor_edge[0] < neighbor_edge[1] else (neighbor_edge[1], neighbor_edge[0])
                    )
                    if neighbor_edge_key == edge_key and neighbor.neighbor_indices[neighbor_slot] == tri_idx:
                        reciprocal_found = True
                        break

                if not reciprocal_found:
                    raise TinValidationError(
                        f"triangle {tri_idx} neighbor {neighbor_idx} is not reciprocal across edge slot {edge_slot}"
                    )
