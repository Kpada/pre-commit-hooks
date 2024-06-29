"""Test clang-tidy-lint pre-commit hook."""

import subprocess
import os
import re
import difflib


def get_project_root() -> str:
    """
    Returns the absolute path to the root directory of the project.

    Returns:
        str: The absolute path to the root directory of the project.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def diff(expected: str, actual: str) -> str:
    """
    Generate a unified diff between two strings.

    Args:
        expected (str): The expected string.
        actual (str): The actual string.

    Returns:
        str: The unified diff between the expected and actual strings.
    """
    return "\n".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual",
        )
    )


def test_clang_tidy_lint():
    """
    Test the pre-commit hook for shfmt by running it on a test script and
    verifying the output.
    """
    # Paths to the test shell script and temporary pre-commit config.
    cpp_file_path = os.path.join(os.path.dirname(__file__), "format.cpp")
    test_config_path = os.path.join(os.path.dirname(__file__), "test-pre-commit-config.yaml")

    try:
        # Add the test script to git index. It's required by pre-commit.
        subprocess.run(["git", "add", cpp_file_path], check=True)

        # Run pre-commit on the test script.
        result = subprocess.run(
            ["pre-commit", "run", "--config", test_config_path, "--files", cpp_file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        # Ensure the pre-commit hook ran and failed as expected.
        project_root = get_project_root()
        relative_in_file_path = os.path.relpath(cpp_file_path, project_root)
        expected_output_pattern = re.compile(
            r"clang-tidy-nolint\S+Failed\n"
            r"- hook id: clang-tidy-nolint\n"
            r"- files were modified by this hook\n\n" + re.escape(relative_in_file_path) + r"\n+"
        )

        assert (
            result.returncode != 0
        ), "pre-commit did not fail as expected.\nOutput:\n{result.stdout}"
        assert expected_output_pattern.search(
            result.stdout
        ), f"Output did not match expected pattern.\nOutput:\n{result.stdout}"

        with open(cpp_file_path, "r", encoding="utf-8") as test_file:
            content = test_file.read()

            expceted_cpp_file_path = os.path.join(os.path.dirname(__file__), "expected.cpp")
            with open(expceted_cpp_file_path, "r", encoding="utf-8") as expected_file:
                expected_content = expected_file.read()

            if content != expected_content:
                assert (
                    content == expected_content
                ), f"Output did not match expected content.\n{diff(expected_content, content)}"

    finally:
        subprocess.run(["git", "restore", cpp_file_path], check=True)


test_clang_tidy_lint()
