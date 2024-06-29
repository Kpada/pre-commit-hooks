"""Test shfmt pre-commit hook."""

import subprocess
import os
import re


def get_project_root() -> str:
    """
    Returns the absolute path to the root directory of the project.

    Returns:
        str: The absolute path to the root directory of the project.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def test_pre_commit_shfmt():
    """
    Test the pre-commit hook for shfmt by running it on a test script and
    verifying the output.
    """
    # Paths to the test shell script and temporary pre-commit config.
    script_path = os.path.join(os.path.dirname(__file__), "tmp_sh_script_to_format.sh")
    test_config_path = os.path.join(os.path.dirname(__file__), "test-pre-commit-config.yaml")

    # Create a test script to format.
    with open(script_path, "w", encoding="utf-8") as test_file:
        test_file.write('#!/bin/bash\necho "Hello, World!"')

    try:
        # Add the test script to git index. It's required by pre-commit.
        subprocess.run(["git", "add", script_path], check=True)

        # Run pre-commit on the test script.
        result = subprocess.run(
            ["pre-commit", "run", "--config", test_config_path, "--files", script_path],
            capture_output=True,
            text=True,
            check=False,
        )

        # Ensure the pre-commit hook ran and failed as expected.
        project_root = get_project_root()
        relative_script_path = os.path.relpath(script_path, project_root)
        expected_output_pattern = re.compile(
            r"shfmt\S+Failed\n"
            r"- hook id: shfmt\n"
            r"- files were modified by this hook\n\n" + re.escape(relative_script_path) + r"\n+"
        )

        assert (
            result.returncode != 0
        ), "pre-commit did not fail as expected.\nOutput:\n{result.stdout}"
        assert expected_output_pattern.search(
            result.stdout
        ), f"Output did not match expected pattern.\nOutput:\n{result.stdout}"

    finally:
        os.remove(script_path)
        subprocess.run(["git", "rm", "--cached", script_path], check=True)


test_pre_commit_shfmt()
