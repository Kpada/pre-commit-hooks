#!/usr/bin/env python
""" Formats clang-tidy NOLINT comments and removes unused ones. """

import re
import argparse
import subprocess
import os
from typing import List, Optional
import shutil
import sys


def get_clang_tidy_path() -> Optional[str]:
    """
    Returns the path of the 'clang-tidy' binary if it is found in the system's PATH.

    Returns:
        str: The path of the 'clang-tidy' binary, or None if it is not found.
    """
    clang_tidy_path = shutil.which("clang-tidy")
    if clang_tidy_path:
        return clang_tidy_path

    return None


def get_enabled_checks(clang_tidy_bin: str, clang_tidy_config: str) -> List[str]:
    """
    Retrieves a list of enabled checks from the clang-tidy binary.

    Args:
        clang_tidy_bin (str): The path to the clang-tidy binary.
        clang_tidy_config (str): The path to the clang-tidy configuration file.

    Returns:
        List[str]: A list of enabled checks.

    Raises:
        RuntimeError: If there is an error running clang-tidy.
    """
    if not os.path.exists(clang_tidy_bin):
        raise RuntimeError(f"Clang-tidy binary not found: {clang_tidy_bin}")
    if not os.path.exists(clang_tidy_config):
        raise RuntimeError(f"Clang-tidy configuration not found: {clang_tidy_config}")

    # Command to retrieve the list of enabled checks.
    cmd = [clang_tidy_bin, "--list-checks", "--config-file", clang_tidy_config]

    # Run clang-tidy and retrieve the list of enabled checks.
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error running clang-tidy: {result.stderr}")

    # Parse.
    checks = []
    in_checks_section = False
    for line in result.stdout.split("\n"):
        if line.strip() == "Enabled checks:":
            in_checks_section = True
        elif in_checks_section:
            check = line.strip()
            if check:
                checks.append(check)

    return checks


def update_checks(content: str, enabled_checks: List[str], separator: str) -> str:
    """
    Updates the NOLINT comments in the given content to only include the enabled checks.

    Args:
        content (str): The content to update.
        enabled_checks (List[str]): The list of enabled checks.
        separator (str): The separator to use for multiple checks in a NOLINT comment.

    Returns:
        str: The updated content.
    """

    def process_nolint_comment(match: re.Match) -> str:
        comment = match.group(1)
        trailing_comment = match.group(2).strip()
        if "(" in comment and ")" in comment:  # If there are rules in the comment
            prefix, rules_part = comment.split("(", 1)
            rules_part = rules_part.rstrip(")")
            rules = rules_part.split(",")
            rules = [rule.strip() for rule in rules]

            # Keep only enabled rules
            kept_rules = []
            for rule in rules:
                if rule in enabled_checks:
                    kept_rules.append(rule)
                elif "*" in rule:
                    # Create a regex pattern to match the wildcard rule
                    pattern = re.compile(rule.replace("*", ".*"))
                    for enabled_check in enabled_checks:
                        if pattern.fullmatch(enabled_check):
                            kept_rules.append(rule)
                            break

            # Return the new comment or None if no rules are left
            if kept_rules:
                return (
                    f"// {prefix}({f',{separator}'.join(kept_rules)}) {trailing_comment}".rstrip()
                )
            else:
                return ""
        else:
            return match.group(0)  # Return the whole match if no rules are specified

    # Regex to match NOLINT comments with and without rules, and optional trailing comments
    nolint_pattern = re.compile(r"//\s*(NOLINT(?:BEGIN|END|NEXTLINE)?(?:\([^)]*\))?)\s*(.*)")

    processed_lines = []
    for line in content.split("\n"):
        original_line = line
        new_line = nolint_pattern.sub(process_nolint_comment, line)
        # Remove empty NOLINT comments but preserve formatting
        new_line = re.sub(r"//\s*NOLINT(?:BEGIN|END|NEXTLINE)?\(\s*\)\s*$", "", new_line).rstrip()

        # Only change the line if the NOLINT comment was modified
        if new_line != original_line.strip():
            if new_line:  # Do not add a blank line
                processed_lines.append(new_line)
        else:
            processed_lines.append(original_line)

    return "\n".join(processed_lines)


def main():
    """
    Processes C++ files to remove unused NOLINT comments.
    """
    parser = argparse.ArgumentParser(description="Remove unused NOLINT comments from C++ files.")
    parser.add_argument(
        "--config-file",
        required=False,
        default=".clang-tidy",
        help="Path to the .clang-tidy file. "
        "Used to get the list of enabled checks for this specific version of clang-tidy.",
    )
    parser.add_argument(
        "--clang-tidy-binary",
        required=False,
        default=get_clang_tidy_path(),
        help="Path to the clang-tidy binary. "
        "Required to get the list of enabled checks for this specific version of clang-tidy.",
    )
    parser.add_argument(
        "--no-fix",
        required=False,
        default=False,
        action="store_true",
        help="Do not modify the files in place.",
    )
    parser.add_argument(
        "--separator",
        required=False,
        default=" ",
        help="Separator for multiple checks in a NOLINT comment. "
        "For example, ' ' for '// NOLINT(foo, bar)'.",
    )
    parser.add_argument(
        "--extra-checks",
        required=False,
        default="",
        help="Additional checks to enable that are not in the .clang-tidy file. "
        "Provide as a comma-separated string. For example, 'clang-diagnostic-error'. "
        "These checks are added to the list of enabled checks.",
    )
    parser.add_argument("files", nargs="+", help="Files to process.")
    args = parser.parse_args()

    enabled_checks = get_enabled_checks(args.clang_tidy_binary, args.config_file)

    extra_checks = (
        [check.strip() for check in args.extra_checks.split(",")] if args.extra_checks else []
    )
    enabled_checks += extra_checks

    ret_code = 0
    for file in args.files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = update_checks(content, enabled_checks, args.separator)

        # Write the new content to the file.
        if not args.no_fix:
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)

        # Print the name of the file if it was modified.
        if new_content != content:
            print(f"{file}")
            ret_code = 1

    sys.exit(ret_code)


if __name__ == "__main__":
    main()
