#!/usr/bin/env python3
"""Remove CodeCV's tiled PDF watermark from exported resumes.

Supports three modes:
  - CLI mode:      python script.py <input.pdf> [output.pdf] [--backup]
  - Batch mode:    python script.py <directory> [--recursive] [--output-dir DIR] [--backup]
  - GUI mode:      python script.exe <input.pdf>   (shows message boxes, for context menu)
"""

from __future__ import annotations

import argparse
import ctypes
import sys
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, DecodedStreamObject, NameObject


DEFAULT_OUTPUT_SUFFIX = ".clean.pdf"
BACKUP_DIR_NAME = "源文件"


def _is_name(value, expected: str) -> bool:
    return isinstance(value, NameObject) and str(value) == expected


def _first_name(operands: Iterable[object]) -> str | None:
    for operand in operands:
        if isinstance(operand, NameObject):
            return str(operand)
    return None


def _is_pattern_fill(operations, index: int) -> tuple[int, str | None]:
    """Return the operation count for a CodeCV watermark fill, or zero."""
    if index + 5 >= len(operations):
        return 0, None

    op0, op1, op2, op3 = operations[index : index + 4]
    uses_pattern_space = (
        op0[1] == b"CS"
        and op1[1] == b"cs"
        and len(op0[0]) == 1
        and len(op1[0]) == 1
        and _is_name(op0[0][0], "/Pattern")
        and _is_name(op1[0][0], "/Pattern")
    )
    if not uses_pattern_space or op2[1] != b"SCN" or op3[1] != b"scn":
        return 0, None

    stroke_pattern = _first_name(op2[0])
    fill_pattern = _first_name(op3[0])
    if stroke_pattern is None or stroke_pattern != fill_pattern:
        return 0, None

    fill_index = index + 4
    if fill_index < len(operations) and operations[fill_index][1] == b"gs":
        fill_index += 1
    if fill_index + 1 >= len(operations):
        return 0, None

    rect_op, fill_op = operations[fill_index : fill_index + 2]
    fills_rectangle = rect_op[1] == b"re" and fill_op[1] in {b"f", b"f*"}
    if not fills_rectangle:
        return 0, None

    return fill_index + 2 - index, fill_pattern


def _remove_page_watermark(page, pdf) -> int:
    contents = page.get_contents()
    if contents is None:
        return 0

    stream = ContentStream(contents, pdf)
    old_operations = stream.operations
    new_operations = []
    removed_patterns = set()
    index = 0

    while index < len(old_operations):
        matched_count, pattern_name = _is_pattern_fill(old_operations, index)
        if matched_count:
            removed_patterns.add(pattern_name)
            index += matched_count
            continue

        new_operations.append(old_operations[index])
        index += 1

    if not removed_patterns:
        return 0

    stream.operations = new_operations
    replacement = DecodedStreamObject()
    replacement.set_data(stream.get_data())
    page.replace_contents(replacement)

    resources = page.get("/Resources")
    patterns = resources.get("/Pattern") if resources else None
    if patterns:
        for pattern_name in removed_patterns:
            patterns.pop(NameObject(pattern_name), None)
        if not patterns:
            resources.pop(NameObject("/Pattern"), None)

    return len(removed_patterns)


def remove_watermark(input_pdf: str | Path, output_pdf: str | Path) -> int:
    """Remove CodeCV tiled pattern watermarks and write a cleaned PDF.

    Returns the number of page-level watermark pattern fills removed.
    """
    input_path = Path(input_pdf)
    output_path = Path(output_pdf)

    reader = PdfReader(str(input_path))
    writer = PdfWriter(clone_from=reader)
    removed = 0

    for page in writer.pages:
        removed += _remove_page_watermark(page, writer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        writer.write(handle)

    return removed


def default_output_path(input_pdf: Path) -> Path:
    """Append DEFAULT_OUTPUT_SUFFIX to the stem."""
    return input_pdf.with_name(input_pdf.stem + DEFAULT_OUTPUT_SUFFIX)


def backup_original(input_pdf: Path) -> Path:
    """Move *input_pdf* into a ``BACKUP_DIR_NAME`` folder next to it.

    Uses an indexed filename (e.g. ``resume_1.pdf``) if the backup already
    exists, so repeated runs never overwrite an earlier backup.  Returns the
    backup path; the original location is freed for the cleaned output.
    """
    backup_dir = input_pdf.parent / BACKUP_DIR_NAME
    backup_dir.mkdir(exist_ok=True)

    backup_path = backup_dir / input_pdf.name
    counter = 1
    while backup_path.exists():
        stem = f"{input_pdf.stem}_{counter}"
        backup_path = backup_dir / f"{stem}{input_pdf.suffix}"
        counter += 1
    input_pdf.rename(backup_path)
    return backup_path


# ── Batch helpers (directory processing) ───────────────────────────────────

def _iter_pdf_files(directory: Path, recursive: bool) -> Iterable[Path]:
    """Yield PDF files under *directory*, optionally scanning subfolders."""
    pattern = "**/*.pdf" if recursive else "*.pdf"
    return sorted(directory.glob(pattern))


def _batch_main(
    directory: Path,
    output_dir: Path | None,
    recursive: bool,
    backup: bool,
) -> int:
    pdfs = list(_iter_pdf_files(directory, recursive))
    if not pdfs:
        print(f"No PDF files found under: {directory}")
        return 1

    processed = 0
    for pdf in pdfs:
        try:
            source = backup_original(pdf) if backup else pdf
            if output_dir is not None:
                output_dir.mkdir(parents=True, exist_ok=True)
                out = output_dir / (pdf.stem + DEFAULT_OUTPUT_SUFFIX)
            else:
                out = pdf if backup else default_output_path(pdf)
            removed = remove_watermark(source, out)
            processed += 1
            print(f"[OK]   {pdf.name} -> {out.name}  (removed {removed})")
        except Exception as exc:
            print(f"[FAIL] {pdf.name}: {exc}")

    print(f"\nProcessed {processed}/{len(pdfs)} PDF(s).")
    return 0 if processed else 1


# ── GUI helpers (message boxes for context-menu mode) ──────────────────────

def _show_message(title: str, message: str, is_error: bool = False) -> None:
    """Display a Windows message box (no console dependency)."""
    ctypes.windll.user32.MessageBoxW(
        0,
        message,
        title,
        0x10 if is_error else 0x40,  # MB_ICONERROR | MB_ICONINFORMATION
    )


# ── Entry points ───────────────────────────────────────────────────────────

def _context_menu_mode(file_path: str) -> int:
    """Invoked when a single file path is dropped on the exe."""
    input_pdf = Path(file_path)

    if not input_pdf.exists():
        _show_message("文件错误", f"找不到文件：\n{input_pdf}", is_error=True)
        return 1

    if input_pdf.suffix.lower() != ".pdf":
        _show_message("文件错误", f"不支持的文件类型：{input_pdf.suffix}\n请选择 PDF 文件。", is_error=True)
        return 1

    try:
        # 1. Back up the original file into "源文件/" (frees the original name)
        src_dir = input_pdf.parent
        backup_path = backup_original(input_pdf)

        # 2. Output cleaned PDF with the **original** file name
        output_path = src_dir / input_pdf.name

        removed = remove_watermark(backup_path, output_path)
        if removed > 0:
            _show_message(
                "去除水印完成",
                f"已去除 {removed} 个 CodeCV 水印。\n\n"
                f"原文件移至：{BACKUP_DIR_NAME}/\n"
                f"干净文件：{output_path.name}",
            )
        else:
            _show_message(
                "未检测到水印",
                f"未发现 CodeCV 水印。\n\n"
                f"原文件移至：{BACKUP_DIR_NAME}/\n"
                f"干净文件：{output_path.name}",
            )
        return 0
    except Exception as exc:
        _show_message("处理失败", f"去除水印时出错：\n{exc}", is_error=True)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove CodeCV's tiled watermark from an exported resume PDF."
    )
    parser.add_argument(
        "input_pdf",
        type=Path,
        help="Path to the exported CodeCV PDF, or a directory to batch process",
    )
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",
        help="Cleaned PDF path. Defaults to '<input>.clean.pdf'.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="When the input is a directory, also process PDFs in subfolders.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write cleaned PDFs into this directory (keeps the original filename stem).",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Back the original PDF(s) up into a '%s' folder before processing." % BACKUP_DIR_NAME,
    )
    return parser.parse_args()


def main() -> int:
    # If called with a single non-flag argument, run in GUI (context menu) mode.
    # Skip directories so batch mode is not hijacked by this branch.
    if (
        len(sys.argv) == 2
        and not sys.argv[1].startswith("-")
        and not Path(sys.argv[1]).is_dir()
    ):
        return _context_menu_mode(sys.argv[1])

    args = parse_args()
    input_path = args.input_pdf

    # Batch mode: the input is a directory.
    if input_path.is_dir():
        return _batch_main(input_path, args.output_dir, args.recursive, args.backup)

    # Classic CLI mode (single file).
    source = backup_original(input_path) if args.backup else input_path
    if args.backup and args.output_dir is None and args.output_pdf is None:
        # Back up the original and write the cleaned file under the original name.
        output_pdf = input_path
    elif args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_pdf = args.output_dir / (input_path.stem + DEFAULT_OUTPUT_SUFFIX)
    else:
        output_pdf = args.output_pdf or default_output_path(input_path)
    removed = remove_watermark(source, output_pdf)
    print(f"Removed {removed} CodeCV watermark pattern fill(s).")
    print(f"Wrote: {output_pdf}")
    return 0 if removed else 1


if __name__ == "__main__":
    raise SystemExit(main())
