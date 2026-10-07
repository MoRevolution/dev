#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf"]
# ///
"""Add blank margins to a PDF to make room for notes.

Margins are percentages of the page: left and right of its width, top and bottom
of its height. With no margin flags, each side gets 25%.

    pdfpad paper.pdf                  # -> paper-padded.pdf
    pdfpad paper.pdf -r 60            # one wide note column on the right
    pdfpad slides.pdf -s 20 -b 40 -o notes.pdf
"""

import argparse
from pathlib import Path

import pymupdf


def clip_contents(page: pymupdf.Page, r: pymupdf.Rect) -> None:
    """Wrap the page's content streams in a clip to r, in PDF coordinates (y up)."""
    doc = page.parent

    def stream(data: str) -> int:
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, data.encode())
        return xref

    push = stream(f"q {r.x0:.3f} {r.y0:.3f} {r.width:.3f} {r.height:.3f} re W n\n")
    pop = stream("\nQ\n")
    refs = " ".join(f"{x} 0 R" for x in [push, *page.get_contents(), pop])
    doc.xref_set_key(page.xref, "Contents", f"[{refs}]")


def pad_page(
    page: pymupdf.Page, left: float, top: float, right: float, bottom: float
) -> None:
    """Grow the page by margins in points, measured as the page is displayed.

    Only the page box changes, so text, links, and annotations keep their place.
    """
    # /Rotate turns the stored page clockwise for display, so at 90° the displayed
    # top edge is the stored left edge, the displayed right is the stored top, etc.
    steps = page.rotation // 90
    margins = [left, top, right, bottom]
    left, top, right, bottom = margins[steps:] + margins[:steps]

    # page.cropbox is measured down from the MediaBox top; flip it back to y-up.
    mb, cb = page.mediabox, page.cropbox
    visible = pymupdf.Rect(cb.x0, mb.y1 - cb.y1, cb.x1, mb.y1 - cb.y0)
    # Without the clip, whatever the CropBox hid (crop marks, trimmed scan edges)
    # would show up in the new margins.
    if visible != mb:
        clip_contents(page, visible)
    x0, y0, x1, y1 = visible
    page.set_mediabox(pymupdf.Rect(x0 - left, y0 - bottom, x1 + right, y1 + top))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "-o", "--output", type=Path, help="default: <name>-padded.pdf beside the input"
    )
    for edge in ["left", "right", "top", "bottom"]:
        parser.add_argument(f"-{edge[0]}", f"--{edge}", type=float, metavar="PCT")
    parser.add_argument(
        "-s", "--sides", type=float, metavar="PCT", help="left and right"
    )
    parser.add_argument("-a", "--all", type=float, metavar="PCT", help="every edge")
    args = parser.parse_args()

    edges = [args.left, args.right, args.top, args.bottom, args.sides, args.all]
    if all(v is None for v in edges):
        args.sides = 25

    def pick(*values: float | None) -> float:
        return next((v for v in values if v is not None), 0.0)

    left = pick(args.left, args.sides, args.all)
    right = pick(args.right, args.sides, args.all)
    top = pick(args.top, args.all)
    bottom = pick(args.bottom, args.all)

    out = args.output or args.pdf.with_name(f"{args.pdf.stem}-padded.pdf")
    doc = pymupdf.open(args.pdf)
    for page in doc:
        w, h = page.rect.width / 100, page.rect.height / 100
        pad_page(page, left * w, top * h, right * w, bottom * h)
    doc.save(out, garbage=1, deflate=True)
    print(out)


if __name__ == "__main__":
    main()
