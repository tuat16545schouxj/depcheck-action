"""PDF reporter — renders detection results as a PDF document.

Uses only the stdlib (no third-party PDF library) by generating a minimal
valid PDF manually so that the action has zero extra runtime dependencies.
For richer output users can pipe the HTML reporter through a headless browser;
this reporter is intentionally lightweight.
"""
from __future__ import annotations

import textwrap
from datetime import datetime, timezone
from typing import List

from src.detectors.registry import DetectionResult


class PdfReporter:
    """Render detection results as a minimal PDF byte string."""

    _FONT = "Helvetica"
    _TITLE = "Dependency Audit Report"

    def render(self, results: List[DetectionResult]) -> bytes:
        """Return raw PDF bytes for *results*."""
        lines = self._collect_text_lines(results)
        return _build_pdf(self._TITLE, lines)

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _collect_text_lines(self, results: List[DetectionResult]) -> List[str]:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        rows: List[str] = [
            self._TITLE,
            f"Generated: {ts}",
            "",
        ]
        total_deps = sum(len(r.dependencies) for r in results)
        total_outdated = sum(
            sum(1 for d in r.dependencies if d.outdated) for r in results
        )
        rows.append(f"Summary: {total_outdated} outdated / {total_deps} total")
        rows.append("")

        for result in results:
            outdated = [d for d in result.dependencies if d.outdated]
            rows.append(
                f"[{result.ecosystem}] {result.manifest_path} "
                f"({len(outdated)} outdated)"
            )
            for dep in outdated:
                rows.append(
                    f"  - {dep.name}: {dep.current_version} -> {dep.latest_version}"
                )
            if not outdated:
                rows.append("  All dependencies up-to-date.")
            rows.append("")
        return rows


# ---------------------------------------------------------------------------
# Minimal PDF builder (no third-party deps)
# ---------------------------------------------------------------------------

def _build_pdf(title: str, lines: List[str]) -> bytes:
    """Produce a valid single-page PDF containing *lines* of plain text."""
    objects: List[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)  # 1-based object number

    # Object 1 – catalog (placeholder, patched later)
    catalog_idx = add(b"")
    # Object 2 – pages (placeholder)
    pages_idx = add(b"")
    # Object 3 – font
    font_idx = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    )

    # Object 4 – page content stream
    text_ops: List[str] = ["BT", "/F1 10 Tf", "10 TL"]
    y_start = 780
    text_ops.append(f"50 {y_start} Td")
    for line in lines[:70]:  # cap at ~70 lines for a single page
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        text_ops.append(f"({safe}) Tj T*")
    text_ops.append("ET")
    stream_body = "\n".join(text_ops).encode()
    stream_obj = (
        b"<< /Length " + str(len(stream_body)).encode() + b" >>\nstream\n"
        + stream_body + b"\nendstream"
    )
    content_idx = add(stream_obj)

    # Object 5 – page
    page_obj = (
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] "
        b"/Contents " + str(content_idx).encode() + b" 0 R "
        b"/Resources << /Font << /F1 " + str(font_idx).encode() + b" 0 R >> >> >>"
    )
    page_idx = add(page_obj)

    # Patch pages object
    objects[pages_idx - 1] = (
        b"<< /Type /Pages /Kids [" + str(page_idx).encode() + b" 0 R] /Count 1 >>"
    )
    # Patch catalog
    title_bytes = title.encode("latin-1", errors="replace")
    objects[catalog_idx - 1] = (
        b"<< /Type /Catalog /Pages 2 0 R "
        b"/Info << /Title (" + title_bytes + b") >> >>"
    )

    # Assemble PDF
    buf: List[bytes] = [b"%PDF-1.4\n"]
    offsets: List[int] = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(b"".join(buf)))
        buf.append(str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n")

    xref_offset = len(b"".join(buf))
    xref = [b"xref\n", f"0 {len(objects) + 1}\n".encode(),
            b"0000000000 65535 f \n"]
    for off in offsets:
        xref.append(f"{off:010d} 00000 n \n".encode())
    buf.extend(xref)
    buf.append(
        b"trailer\n<< /Size " + str(len(objects) + 1).encode()
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode() + b"\n%%EOF\n"
    )
    return b"".join(buf)
