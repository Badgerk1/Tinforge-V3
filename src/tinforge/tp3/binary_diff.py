from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NumericInterpretation:
    width_bytes: int
    old_unsigned: int
    new_unsigned: int
    old_signed: int
    new_signed: int
    old_float: float | None = None
    new_float: float | None = None


@dataclass(frozen=True)
class UTF16LEInterpretation:
    old_text: str
    new_text: str


@dataclass(frozen=True)
class ByteContext:
    start_offset: int
    end_offset: int
    old_hex: str
    new_hex: str


@dataclass(frozen=True)
class ByteRangeChange:
    offset: int
    old_length: int
    new_length: int
    old_hex: str
    new_hex: str
    numeric_interpretations: tuple[NumericInterpretation, ...]
    utf16le_change: UTF16LEInterpretation | None
    context: ByteContext


@dataclass(frozen=True)
class TP3BinaryDiffReport:
    old_size: int
    new_size: int
    old_sha256: str
    new_sha256: str
    changed_ranges: tuple[ByteRangeChange, ...]


def read_tp3_bytes(path: Path) -> bytes:
    return path.read_bytes()


def compare_tp3_files(old_path: Path, new_path: Path, *, context_bytes: int = 16) -> TP3BinaryDiffReport:
    return compare_tp3_bytes(
        read_tp3_bytes(old_path),
        read_tp3_bytes(new_path),
        context_bytes=context_bytes,
    )


def compare_tp3_bytes(old_bytes: bytes, new_bytes: bytes, *, context_bytes: int = 16) -> TP3BinaryDiffReport:
    changed_ranges = tuple(
        _build_change(old_bytes, new_bytes, start, end, context_bytes)
        for start, end in _iter_changed_ranges(old_bytes, new_bytes)
    )
    return TP3BinaryDiffReport(
        old_size=len(old_bytes),
        new_size=len(new_bytes),
        old_sha256=hashlib.sha256(old_bytes).hexdigest(),
        new_sha256=hashlib.sha256(new_bytes).hexdigest(),
        changed_ranges=changed_ranges,
    )


def format_diff_report(report: TP3BinaryDiffReport) -> str:
    lines = [
        f"old_size={report.old_size} new_size={report.new_size}",
        f"old_sha256={report.old_sha256}",
        f"new_sha256={report.new_sha256}",
        f"changed_ranges={len(report.changed_ranges)}",
    ]
    for index, change in enumerate(report.changed_ranges, start=1):
        lines.append("")
        lines.append(
            f"[{index}] offset={change.offset} old_len={change.old_length} new_len={change.new_length}"
        )
        lines.append(f"  old_hex={change.old_hex}")
        lines.append(f"  new_hex={change.new_hex}")
        if change.numeric_interpretations:
            lines.append("  interpretations:")
            for parsed in change.numeric_interpretations:
                if parsed.old_float is None or parsed.new_float is None:
                    lines.append(
                        "    "
                        f"{parsed.width_bytes}B "
                        f"u:{parsed.old_unsigned}->{parsed.new_unsigned} "
                        f"i:{parsed.old_signed}->{parsed.new_signed}"
                    )
                else:
                    lines.append(
                        "    "
                        f"{parsed.width_bytes}B "
                        f"u:{parsed.old_unsigned}->{parsed.new_unsigned} "
                        f"i:{parsed.old_signed}->{parsed.new_signed} "
                        f"f:{parsed.old_float!r}->{parsed.new_float!r}"
                    )
        if change.utf16le_change is not None:
            lines.append(
                "  utf16le="
                f"{change.utf16le_change.old_text!r}->{change.utf16le_change.new_text!r}"
            )
        lines.append(
            "  context "
            f"[{change.context.start_offset}:{change.context.end_offset}]"
        )
        lines.append(f"    old={change.context.old_hex}")
        lines.append(f"    new={change.context.new_hex}")
    return "\n".join(lines) + "\n"


def _iter_changed_ranges(old_bytes: bytes, new_bytes: bytes) -> tuple[tuple[int, int], ...]:
    min_len = min(len(old_bytes), len(new_bytes))
    ranges: list[tuple[int, int]] = []

    start: int | None = None
    for offset in range(min_len):
        changed = old_bytes[offset] != new_bytes[offset]
        if changed and start is None:
            start = offset
        elif not changed and start is not None:
            ranges.append((start, offset))
            start = None

    if start is not None:
        ranges.append((start, min_len))

    if len(old_bytes) != len(new_bytes):
        ranges.append((min_len, max(len(old_bytes), len(new_bytes))))

    return tuple(ranges)


def _build_change(
    old_bytes: bytes,
    new_bytes: bytes,
    start: int,
    end: int,
    context_bytes: int,
) -> ByteRangeChange:
    old_chunk = old_bytes[start:end]
    new_chunk = new_bytes[start:end]
    context_start = max(0, start - context_bytes)
    context_end = min(max(len(old_bytes), len(new_bytes)), end + context_bytes)
    return ByteRangeChange(
        offset=start,
        old_length=len(old_chunk),
        new_length=len(new_chunk),
        old_hex=old_chunk.hex(),
        new_hex=new_chunk.hex(),
        numeric_interpretations=_numeric_interpretations(old_chunk, new_chunk),
        utf16le_change=_utf16le_change(old_chunk, new_chunk),
        context=ByteContext(
            start_offset=context_start,
            end_offset=context_end,
            old_hex=old_bytes[context_start:context_end].hex(),
            new_hex=new_bytes[context_start:context_end].hex(),
        ),
    )


def _numeric_interpretations(old_chunk: bytes, new_chunk: bytes) -> tuple[NumericInterpretation, ...]:
    if len(old_chunk) != len(new_chunk):
        return ()
    width = len(old_chunk)
    if width not in (1, 2, 4, 8):
        return ()

    old_unsigned = int.from_bytes(old_chunk, byteorder="little", signed=False)
    new_unsigned = int.from_bytes(new_chunk, byteorder="little", signed=False)
    old_signed = int.from_bytes(old_chunk, byteorder="little", signed=True)
    new_signed = int.from_bytes(new_chunk, byteorder="little", signed=True)

    old_float: float | None = None
    new_float: float | None = None
    if width == 4:
        old_float = struct.unpack("<f", old_chunk)[0]
        new_float = struct.unpack("<f", new_chunk)[0]
    elif width == 8:
        old_float = struct.unpack("<d", old_chunk)[0]
        new_float = struct.unpack("<d", new_chunk)[0]

    if old_float is not None and new_float is not None:
        if (not math.isfinite(old_float)) and (not math.isfinite(new_float)):
            old_float = float(old_float)
            new_float = float(new_float)

    return (
        NumericInterpretation(
            width_bytes=width,
            old_unsigned=old_unsigned,
            new_unsigned=new_unsigned,
            old_signed=old_signed,
            new_signed=new_signed,
            old_float=old_float,
            new_float=new_float,
        ),
    )


def _utf16le_change(old_chunk: bytes, new_chunk: bytes) -> UTF16LEInterpretation | None:
    old_text = _decode_meaningful_utf16le(old_chunk)
    new_text = _decode_meaningful_utf16le(new_chunk)
    if old_text is None and new_text is None:
        return None
    return UTF16LEInterpretation(old_text=old_text or "", new_text=new_text or "")


def _decode_meaningful_utf16le(chunk: bytes) -> str | None:
    if not chunk or len(chunk) % 2 != 0:
        return None
    try:
        decoded = chunk.decode("utf-16le")
    except UnicodeDecodeError:
        return None

    cleaned = decoded.replace("\x00", "").strip()
    if len(cleaned) < 3:
        return None
    if not any(character.isalnum() for character in cleaned):
        return None
    if not all(character.isprintable() or character.isspace() for character in cleaned):
        return None
    return cleaned
