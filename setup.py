from setuptools import setup

setup(
    name="pre-commit-hooks",
    description="A set of pre-commit hooks for shell and C/C++ codebases",
    url="https://github.com/kpada/pre-commit-hooks",
    version="0.0.0",
    packages=[
        "hooks",
    ],
    scripts=[
        "hooks/clang_tidy_nolint.py",
        "hooks/cpp_header_guard.py",
    ],
)
