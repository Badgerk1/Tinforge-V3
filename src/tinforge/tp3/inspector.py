"""Conservative TP3 byte-level inspector.

This module intentionally does NOT assign semantics to undocumented records.
It provides reproducible structural observations for reverse engineering.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json, re, struct
from pathlib import Path

PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")
UTF16LE = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")

@dataclass(frozen=True)
class StringHit:
    offset: int
    encoding: str
    value: str

@dataclass(frozen=True)
class Inspection:
    size_bytes: int
    sha256: str
    first_64_bytes_hex: str
    strings: list[StringHit]


def inspect_bytes(data: bytes) -> Inspection:
    hits: list[StringHit] = []
    for m in PRINTABLE.finditer(data):
        hits.append(StringHit(m.start(), "ascii", m.group().decode("ascii")))
    for m in UTF16LE.finditer(data):
        hits.append(StringHit(m.start(), "utf-16le", m.group().decode("utf-16le")))
    hits.sort(key=lambda h: (h.offset, h.encoding))
    return Inspection(
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        first_64_bytes_hex=data[:64].hex(),
        strings=hits,
    )


def inspect_file(path: Path) -> Inspection:
    return inspect_bytes(path.read_bytes())


def to_json(report: Inspection) -> str:
    return json.dumps(asdict(report), indent=2, ensure_ascii=False) + "\n"


def candidate_f64(data: bytes, offset: int, endian: str = "little") -> float:
    """Decode an 8-byte candidate value only; no TP3 meaning is implied."""
    if offset < 0 or offset + 8 > len(data):
        raise ValueError("offset outside buffer")
    fmt = "<d" if endian == "little" else ">d"
    return struct.unpack_from(fmt, data, offset)[0]
