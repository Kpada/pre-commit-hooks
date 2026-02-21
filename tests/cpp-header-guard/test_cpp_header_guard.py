"""Tests for cpp-header-guard pre-commit hook."""

import os
import shutil
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """Returns the project root path."""
    return Path(__file__).resolve().parents[2]


def run_pre_commit(config_relative_path: str, file_relative_path: str) -> subprocess.CompletedProcess[str]:
    """Runs pre-commit for a single file using a specific config."""
    env = os.environ.copy()
    env["PATH"] = f"{get_project_root() / '.venv' / 'bin'}:{env.get('PATH', '')}"
    env.setdefault("PRE_COMMIT_HOME", str(get_project_root() / ".pre-commit-cache"))

    subprocess.run(["git", "add", file_relative_path], check=True)
    return subprocess.run(
        ["pre-commit", "run", "--config", config_relative_path, "--files", file_relative_path],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def write_file(relative_path: str, content: str) -> None:
    """Writes file content relative to the project root."""
    full_path = get_project_root() / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")


def read_file(relative_path: str) -> str:
    """Reads file content relative to the project root."""
    return (get_project_root() / relative_path).read_text(encoding="utf-8")


def cleanup(relative_path: str) -> None:
    """Removes staged state and temporary files created by tests."""
    subprocess.run(["git", "restore", "--staged", relative_path], check=False)
    full_path = get_project_root() / relative_path
    if full_path.exists():
        full_path.unlink()

    tmp_dir = get_project_root() / "tests/cpp-header-guard/tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)


def test_negative_cpp_header_guard_fails_when_guard_is_missing():
    file_relative_path = "tests/cpp-header-guard/tmp/missing.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config.yaml"

    write_file(file_relative_path, "int DoSomething();\n")
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode != 0, result.stdout
        assert "Expected guard: TESTS_CPP_HEADER_GUARD_TMP_MISSING_HPP" in result.stdout
    finally:
        cleanup(file_relative_path)


def test_negative_cpp_header_guard_fails_when_guard_does_not_match_file_path():
    file_relative_path = "tests/cpp-header-guard/tmp/wrong.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config.yaml"
    write_file(
        file_relative_path,
        "#ifndef WRONG_GUARD\n"
        "#define WRONG_GUARD\n\n"
        "int DoSomething();\n\n"
        "#endif  // WRONG_GUARD\n",
    )
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode != 0, result.stdout
        assert "expected 'TESTS_CPP_HEADER_GUARD_TMP_WRONG_HPP'" in result.stdout
    finally:
        cleanup(file_relative_path)


def test_negative_cpp_header_guard_fails_when_if_not_defined_is_used():
    file_relative_path = "tests/cpp-header-guard/tmp/if-not-defined.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config.yaml"
    write_file(
        file_relative_path,
        "#if !defined(TESTS_CPP_HEADER_GUARD_TMP_IF_NOT_DEFINED_HPP)\n"
        "#define TESTS_CPP_HEADER_GUARD_TMP_IF_NOT_DEFINED_HPP\n\n"
        "int DoSomething();\n\n"
        "#endif  // TESTS_CPP_HEADER_GUARD_TMP_IF_NOT_DEFINED_HPP\n",
    )
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode != 0, result.stdout
        assert "missing header guard start (#ifndef ...)." in result.stdout
    finally:
        cleanup(file_relative_path)

def test_negative_cpp_header_guard_fails_when_comment_after_endif_is_missing():
    file_relative_path = "tests/cpp-header-guard/tmp/prefixed.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config-prefix.yaml"
    write_file(
        file_relative_path,
        "#ifndef PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n"
        "#define PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n\n"
        "int DoSomething();\n\n"
        "#endif\n",
    )
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode != 0, result.stdout + "\n" + result.stderr
        assert "missing comment after '#endif'" in result.stdout
    finally:
        cleanup(file_relative_path)

def test_negative_cpp_header_guard_fails_when_comment_after_endif_is_wrong():
    file_relative_path = "tests/cpp-header-guard/tmp/prefixed.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config-prefix.yaml"
    write_file(
        file_relative_path,
        "#ifndef PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n"
        "#define PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n\n"
        "int DoSomething();\n\n"
        "#endif // PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_H\n",
    )
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode != 0, result.stdout + "\n" + result.stderr
        assert "does not match expected" in result.stdout
    finally:
        cleanup(file_relative_path)

def test_cpp_header_guard_passes_with_prefix():
    file_relative_path = "tests/cpp-header-guard/tmp/prefixed.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config-prefix.yaml"
    write_file(
        file_relative_path,
        "#ifndef PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n"
        "#define PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n\n"
        "int DoSomething();\n\n"
        "#endif  // PROJECT_TESTS_CPP_HEADER_GUARD_TMP_PREFIXED_HPP\n",
    )
    try:
        result = run_pre_commit(config_relative_path, file_relative_path)

        assert result.returncode == 0, result.stdout + "\n" + result.stderr
        assert "Failed" not in result.stdout
    finally:
        cleanup(file_relative_path)


def test_cpp_header_guard_fix_adds_missing_guard():
    file_relative_path = "tests/cpp-header-guard/tmp/fix-missing.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config-fix.yaml"

    write_file(file_relative_path, "int DoSomething();\n")
    try:
        first_run = run_pre_commit(config_relative_path, file_relative_path)
        assert first_run.returncode != 0, first_run.stdout + "\n" + first_run.stderr
        assert file_relative_path in first_run.stdout

        expected_content = (
            "#ifndef TESTS_CPP_HEADER_GUARD_TMP_FIX_MISSING_HPP\n"
            "#define TESTS_CPP_HEADER_GUARD_TMP_FIX_MISSING_HPP\n\n"
            "int DoSomething();\n\n"
            "#endif  // TESTS_CPP_HEADER_GUARD_TMP_FIX_MISSING_HPP\n"
        )
        assert read_file(file_relative_path) == expected_content

        second_run = run_pre_commit(config_relative_path, file_relative_path)
        assert second_run.returncode == 0, second_run.stdout + "\n" + second_run.stderr
    finally:
        cleanup(file_relative_path)


def test_cpp_header_guard_fix_rewrites_wrong_guard():
    file_relative_path = "tests/cpp-header-guard/tmp/fix-wrong.hpp"
    config_relative_path = "tests/cpp-header-guard/test-pre-commit-config-fix.yaml"

    write_file(
        file_relative_path,
        "#if !defined(WRONG_GUARD)\n"
        "#define WRONG_GUARD\n\n"
        "int DoSomething();\n"
        "#endif\n",
    )
    try:
        first_run = run_pre_commit(config_relative_path, file_relative_path)
        assert first_run.returncode != 0, first_run.stdout + "\n" + first_run.stderr
        assert file_relative_path in first_run.stdout

        expected_content = (
            "#ifndef TESTS_CPP_HEADER_GUARD_TMP_FIX_WRONG_HPP\n"
            "#define TESTS_CPP_HEADER_GUARD_TMP_FIX_WRONG_HPP\n\n"
            "#if !defined(WRONG_GUARD)\n"
            "#define WRONG_GUARD\n\n"
            "int DoSomething();\n"
            "#endif\n\n"
            "#endif  // TESTS_CPP_HEADER_GUARD_TMP_FIX_WRONG_HPP\n"
        )
        assert read_file(file_relative_path) == expected_content

        second_run = run_pre_commit(config_relative_path, file_relative_path)
        assert second_run.returncode == 0, second_run.stdout + "\n" + second_run.stderr
    finally:
        cleanup(file_relative_path)
