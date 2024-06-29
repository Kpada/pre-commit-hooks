# Pre-commit Hooks

A set of [pre-commit](https://pre-commit.com/) hooks for various languages.

## Supported Hooks

- [shfmt](#shfmt)
- [clang-tidy-nolint](#clang-tidy-nolint)

### shfmt

Runs [shfmt](https://github.com/mvdan/sh) on the specified files with the given
options and overwrites them if necessary.

Example:

```yaml
- id: shfmt
  args:
    - -i
    - "2"
    - -ci
    - -s
```

### clang-tidy-nolint

The hook helps maintain a clean codebase by detecting and removing obsolete
[clang-tidy](https://clang.llvm.org/extra/clang-tidy) `NOLINT` comments. These
comments might become redundant after updates to your `.clang-tidy`
configuration, as checks may no longer be relevant.

This hook ensures the codebase stays up-to-date by eliminating these outdated
comments.

Arguments:

- `--clang-tidy-binary`: Specifies the path to the clang-tidy binary. Since the
  list of supported checks depends on the clang-tidy version, the binary is used
  to find the relevant checks. Defaults to the clang-tidy binary found in the
  `PATH`.
- `--config-file`: Specifies the path to the `.clang-tidy` configuration file.
  Defaults to `.clang-tidy` in the current directory.
- `--no-fix`: If set, the hook will not overwrite files.
- `--separator`: Specifies the separator string between several checks in a
  `NOLINT` comment. Defaults to ' '.

Example:

```yaml
hooks:
  - id: clang-tidy-nolint
```

## Development

To set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html)
environment, follow these steps:

### Install Python and required packages

Ensure Python and `venv` are installed on your system:

```sh
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

### Create a virtual environment

Navigate to the project directory and create a virtual environment:

```sh
python3 -m venv venv
```

### Activate the virtual environment

Activate the virtual environment:

```sh
source venv/bin/activate
```

### Install dependencies

Install the required dependencies using pip:

```sh
pip install -r requirements.txt
```

### Deactivate the virtual environment

When you are done working, deactivate the virtual environment:

```sh
deactivate
```
