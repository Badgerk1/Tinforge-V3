from __future__ import annotations

import hashlib
import struct
from collections import defaultdict
from dataclasses import dataclass

from tinforge.surface import (
    SurfaceTIN,
    SurfaceTriangle,
    SurfaceVertex,
    TINValidationError,
    triangle_edges,
    triangle_twice_area_xy,
    validate_tin,
    xy_area_tolerance,
)
from tinforge.tp3.writer import parse_triangle_records

VERTEX_BLOCK_OFFSET = 380120
VERTEX_RECORD_COUNT = 53
VERTEX_RECORD_STRUCT = struct.Struct("<3d")
TRIANGLE_BLOCK_OFFSET = 431906
TRIANGLE_RECORD_COUNT = 76
COUNT_VERTEX_OFFSET = 433766
COUNT_TRIANGLE_OFFSET = 433770
ORIGIN_CANDIDATE_X_OFFSET = 433908
ORIGIN_CANDIDATE_Y_OFFSET = 433916


@dataclass(frozen=True)
class Stage3SurfaceEvidence:
    vertex_block_sha256: str
    vertex_round_trip_exact: bool
    vertex_count_header: int
    triangle_count_header: int
    origin_candidate_x: float
    origin_candidate_y: float
    vertex_count: int
    triangle_count: int
    edge_count: int
    boundary_edge_count: int
    euler_characteristic: int
    all_vertices_used: bool
    has_zero_or_near_zero_triangles: bool
    has_non_manifold_edges: bool
    reciprocal_adjacency_ok: bool
    geometric_neighbor_edge_mapping_ok: bool


def _slice_exact(data: bytes, offset: int, size: int, label: str) -> bytes:
    end = offset + size
    if offset < 0 or end > len(data):
        raise TINValidationError(f"{label} slice {offset}:{end} exceeds TP3 bounds")
    return data[offset:end]


def decode_vertex_block(data: bytes) -> tuple[SurfaceVertex, ...]:
    block = _slice_exact(
        data,
        VERTEX_BLOCK_OFFSET,
        VERTEX_RECORD_COUNT * VERTEX_RECORD_STRUCT.size,
        "vertex block",
    )
    return tuple(
        SurfaceVertex(x=local_x, y=local_y, z=elevation_z)
        for local_x, local_y, elevation_z in VERTEX_RECORD_STRUCT.iter_unpack(block)
    )


def encode_vertex_block(vertices: tuple[SurfaceVertex, ...]) -> bytes:
    if len(vertices) != VERTEX_RECORD_COUNT:
        raise TINValidationError(
            f"expected {VERTEX_RECORD_COUNT} vertices, found {len(vertices)}"
        )
    return b"".join(
        VERTEX_RECORD_STRUCT.pack(vertex.x, vertex.y, vertex.z) for vertex in vertices
    )


def decode_triangle_block(data: bytes) -> tuple[SurfaceTriangle, ...]:
    block = _slice_exact(data, TRIANGLE_BLOCK_OFFSET, TRIANGLE_RECORD_COUNT * 24, "triangle block")
    records = parse_triangle_records(block, vertex_count=VERTEX_RECORD_COUNT)
    return tuple(
        SurfaceTriangle(
            vertices=(record.vertex_0, record.vertex_1, record.vertex_2),
            neighbors=(record.neighbor_0, record.neighbor_1, record.neighbor_2),
        )
        for record in records
    )


def uint32le_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def float64le_at(data: bytes, offset: int) -> float:
    return struct.unpack_from("<d", data, offset)[0]


def build_surface_tin_from_original(data: bytes, name: str = "design grade") -> SurfaceTIN:
    vertices = decode_vertex_block(data)
    triangles = decode_triangle_block(data)
    return SurfaceTIN(name=name, origin_x=0.0, origin_y=0.0, vertices=vertices, triangles=triangles)


def verify_stage3_surface_evidence(data: bytes) -> Stage3SurfaceEvidence:
    vertex_block = _slice_exact(
        data,
        VERTEX_BLOCK_OFFSET,
        VERTEX_RECORD_COUNT * VERTEX_RECORD_STRUCT.size,
        "vertex block",
    )
    vertices = decode_vertex_block(data)
    vertex_round_trip_exact = encode_vertex_block(vertices) == vertex_block

    surface = build_surface_tin_from_original(data)
    validate_tin(surface)

    edge_map: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    used_vertices: set[int] = set()
    reciprocal_ok = True
    geometric_neighbor_ok = True
    for triangle_index, triangle in enumerate(surface.triangles):
        used_vertices.update(triangle.vertices)
        for edge_index, edge in enumerate(triangle_edges(triangle.vertices)):
            edge_key = tuple(sorted(edge))
            edge_map[edge_key].append((triangle_index, edge_index))
            neighbor_index = triangle.neighbors[edge_index]
            if neighbor_index == -1:
                continue
            if not 0 <= neighbor_index < len(surface.triangles):
                reciprocal_ok = False
                geometric_neighbor_ok = False
                continue
            neighbor_triangle = surface.triangles[neighbor_index]
            if not set(edge).issubset(neighbor_triangle.vertices):
                geometric_neighbor_ok = False
            neighbor_edges = triangle_edges(neighbor_triangle.vertices)
            reciprocal_slot_found = False
            for neighbor_edge_index, neighbor_edge in enumerate(neighbor_edges):
                if set(neighbor_edge) == set(edge):
                    reciprocal_slot_found = True
                    if neighbor_triangle.neighbors[neighbor_edge_index] != triangle_index:
                        reciprocal_ok = False
            if not reciprocal_slot_found:
                geometric_neighbor_ok = False
                reciprocal_ok = False

    boundary_edges = 0
    non_manifold = False
    for edge_refs in edge_map.values():
        if len(edge_refs) == 1:
            boundary_edges += 1
        elif len(edge_refs) > 2:
            non_manifold = True

    area_tolerance = xy_area_tolerance(surface.vertices)
    has_zero_or_near_zero_triangles = any(
        abs(triangle_twice_area_xy(surface.vertices, triangle)) <= area_tolerance
        for triangle in surface.triangles
    )

    for triangle_index, triangle in enumerate(surface.triangles):
        for edge_index, edge in enumerate(triangle_edges(triangle.vertices)):
            edge_refs = edge_map[tuple(sorted(edge))]
            neighbor_index = triangle.neighbors[edge_index]
            if neighbor_index == -1 and len(edge_refs) != 1:
                reciprocal_ok = False
                geometric_neighbor_ok = False
            if neighbor_index != -1 and len(edge_refs) != 2:
                reciprocal_ok = False
                geometric_neighbor_ok = False
            if neighbor_index != -1 and neighbor_index not in {
                reference_triangle_index
                for reference_triangle_index, _ in edge_refs
                if reference_triangle_index != triangle_index
            }:
                geometric_neighbor_ok = False
                reciprocal_ok = False

    vertex_count = len(surface.vertices)
    triangle_count = len(surface.triangles)
    edge_count = len(edge_map)
    return Stage3SurfaceEvidence(
        vertex_block_sha256=hashlib.sha256(vertex_block).hexdigest(),
        vertex_round_trip_exact=vertex_round_trip_exact,
        vertex_count_header=uint32le_at(data, COUNT_VERTEX_OFFSET),
        triangle_count_header=uint32le_at(data, COUNT_TRIANGLE_OFFSET),
        origin_candidate_x=float64le_at(data, ORIGIN_CANDIDATE_X_OFFSET),
        origin_candidate_y=float64le_at(data, ORIGIN_CANDIDATE_Y_OFFSET),
        vertex_count=vertex_count,
        triangle_count=triangle_count,
        edge_count=edge_count,
        boundary_edge_count=boundary_edges,
        euler_characteristic=vertex_count - edge_count + triangle_count,
        all_vertices_used=used_vertices == set(range(vertex_count)),
        has_zero_or_near_zero_triangles=has_zero_or_near_zero_triangles,
        has_non_manifold_edges=non_manifold,
        reciprocal_adjacency_ok=reciprocal_ok,
        geometric_neighbor_edge_mapping_ok=geometric_neighbor_ok,
    )
