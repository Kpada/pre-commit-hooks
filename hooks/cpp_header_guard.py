#!/usr/bin/env python
"""Validate C/C++ header guards."""

import argparse
from dataclasses import dataclass
import re
import sys
from typing import Optional

HEADER_IFNDEF_RE = re.compile(r"^\s*#\s*ifndef\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?://.*)?$")
HEADER_DEFINE_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\b")
HEADER_ENDIF_RE = re.compile(r"^\s*#\s*endif\b")
HEADER_ENDIF_COMMENT_RE = re.compile(
    r"^\s*#\s*endif(?:\s*//\s*([A-Za-z_][A-Za-z0-9_]*))?\s*$"
)


@dataclass
class GuardLayout:
    """Discovered guard-related line indexes for a file."""

    start_index: Optional[int] = None
    start_macro: Optional[str] = None
    define_index: Optional[int] = None
    define_macro: Optional[str] = None
    first_non_skippable_after_start: Optional[int] = None
    endif_index: Optional[int] = None


def normalize_component(value: str) -> str:
    """Converts any string into an uppercase macro-friendly component."""
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", value)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").upper()


def expected_guard_for_path(path: str, prefix: str) -> str:
    """Builds the expected guard name from a path and optional prefix."""
    normalized_path = path.replace("\\", "/").lstrip("./")
    file_component = normalize_component(normalized_path)
    prefix_component = normalize_component(prefix)

    if prefix_component:
        return f"{prefix_component}_{file_component}"
    return file_component


def is_skippable_line(line: str) -> bool:
    """Returns True for empty/comment lines between #ifndef and #define."""
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith("//")
        or stripped.startswith("/*")
        or stripped.startswith("*")
        or stripped.startswith("*/")
    )


def discover_guard_layout(lines: list[str]) -> GuardLayout:
    """Discovers guard positions in the file."""
    layout = GuardLayout()

    for index, line in enumerate(lines):
        ifndef_match = HEADER_IFNDEF_RE.match(line)
        if ifndef_match:
            layout.start_index = index
            layout.start_macro = ifndef_match.group(1)
            break

    if layout.start_index is None:
        return layout

    for index in range(layout.start_index + 1, len(lines)):
        line = lines[index]
        if is_skippable_line(line):
            continue

        layout.first_non_skippable_after_start = index
        define_match = HEADER_DEFINE_RE.match(line)
        if define_match is not None:
            layout.define_index = index
            layout.define_macro = define_match.group(1)
        break

    for index in range(len(lines) - 1, layout.start_index, -1):
        if HEADER_ENDIF_RE.match(lines[index]):
            layout.endif_index = index
            break

    return layout


def validate_content(content: str, expected_guard: str) -> Optional[str]:
    """Validates header guard content and returns an error if invalid."""
    layout = discover_guard_layout(content.splitlines())

    if layout.start_macro is None:
        return f"missing header guard start (#ifndef ...). Expected guard: {expected_guard}"

    if layout.define_index is None:
        if layout.first_non_skippable_after_start is None:
            return (
                f"missing '#define {layout.start_macro}' after header guard start. "
                f"Expected guard: {expected_guard}"
            )
        return (
            f"expected '#define {layout.start_macro}' after header guard start. "
            f"Expected guard: {expected_guard}"
        )

    if layout.define_macro != layout.start_macro:
        return (
            f"mismatch between guard start '{layout.start_macro}' and "
            f"#define '{layout.define_macro}'. Expected guard: {expected_guard}"
        )

    if layout.endif_index is None:
        return f"missing '#endif' for header guard. Expected guard: {expected_guard}"

    if layout.start_macro != expected_guard:
        return f"header guard '{layout.start_macro}' does not match expected '{expected_guard}'."

    endif_line = content.splitlines()[layout.endif_index]
    endif_match = HEADER_ENDIF_COMMENT_RE.match(endif_line)
    if endif_match is None:
        return (
            f"invalid '#endif' format. Expected '#endif  // {expected_guard}'. "
            f"Expected guard: {expected_guard}"
        )

    endif_comment = endif_match.group(1)
    if endif_comment is None:
        return (
            f"missing comment after '#endif'. Expected '#endif  // {expected_guard}'. "
            f"Expected guard: {expected_guard}"
        )
    if endif_comment != expected_guard:
        return (
            f"'#endif' comment '{endif_comment}' does not match expected '{expected_guard}'."
        )

    return None


def with_trailing_newline(content: str) -> str:
    """Ensures content ends with a newline."""
    if content.endswith("\n"):
        return content
    return f"{content}\n"


def wrap_with_guard(content: str, expected_guard: str) -> str:
    """Wraps the full file with a canonical include guard."""
    body = content.rstrip("\n")
    if body:
        return (
            f"#ifndef {expected_guard}\n"
            f"#define {expected_guard}\n\n"
            f"{body}\n\n"
            f"#endif  // {expected_guard}\n"
        )
    return (
        f"#ifndef {expected_guard}\n"
        f"#define {expected_guard}\n\n"
        f"#endif  // {expected_guard}\n"
    )


def fix_content(content: str, expected_guard: str) -> str:
    """Returns fixed content with canonical guard for the expected macro."""
    lines = content.splitlines()
    layout = discover_guard_layout(lines)

    if layout.start_index is None:
        return wrap_with_guard(content, expected_guard)

    fixed = list(lines)
    fixed[layout.start_index] = f"#ifndef {expected_guard}"

    endif_index = layout.endif_index
    if layout.define_index is not None:
        fixed[layout.define_index] = f"#define {expected_guard}"
    else:
        insert_index = layout.first_non_skippable_after_start
        if insert_index is None:
            insert_index = len(fixed)
        fixed.insert(insert_index, f"#define {expected_guard}")
        if endif_index is not None and insert_index <= endif_index:
            endif_index += 1

    if endif_index is not None:
        fixed[endif_index] = f"#endif  // {expected_guard}"
    else:
        if fixed and fixed[-1].strip():
            fixed.append("")
        fixed.append(f"#endif  // {expected_guard}")

    return with_trailing_newline("\n".join(fixed))


def process_file(path: str, prefix: str, should_fix: bool) -> tuple[bool, Optional[str]]:
    """Validates/fixes a single file and returns (modified, error)."""
    expected_guard = expected_guard_for_path(path, prefix)

    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
    except OSError as exc:
        return False, f"{path}: failed to read file ({exc})."

    error = validate_content(content, expected_guard)
    if error is None:
        return False, None

    if not should_fix:
        return False, f"{path}: {error}"

    fixed_content = fix_content(content, expected_guard)
    modified = fixed_content != content
    if modified:
        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(fixed_content)
        except OSError as exc:
            return False, f"{path}: failed to write file ({exc})."

    fixed_error = validate_content(fixed_content, expected_guard)
    if fixed_error is not None:
        return modified, f"{path}: failed to auto-fix header guard ({fixed_error})"

    return modified, None


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate C/C++ header guards. Style: {OPTIONAL_PREFIX_}{FILEPATH}."
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional prefix for generated guards. Example: --prefix PROJECT",
    )
    parser.add_argument(
        "--fix",
        default=False,
        action="store_true",
        help="Automatically fix header guards in-place.",
    )
    parser.add_argument("files", nargs="+", help="Header files to validate.")
    args = parser.parse_args()

    modified_files = []
    errors = []
    for path in args.files:
        modified, error = process_file(path, args.prefix, args.fix)
        if modified:
            modified_files.append(path)
        if error:
            errors.append(error)

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    if modified_files:
        for path in modified_files:
            print(path)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
