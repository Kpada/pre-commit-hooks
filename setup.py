from setuptools import setup

setup(
    name="clang-tidy-nolint",
    description="A pre-commit hook to lint clang-tidy NOLINT comments",
    url="https://github.com/kpada/pre-commit-hooks",
    version="0.0.0",
    packages=[
        "hooks",
    ],
    scripts=[
        "hooks/clang_tidy_nolint.py",
    ],
)
