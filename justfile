set shell := ["bash", "-e", "-o", "pipefail", "-c"]

venv_dir := ".venv"
pre_commit_home := ".pre-commit-cache"

default:
    @just --list

venv:
    python3 -m venv {{venv_dir}}

install: venv
    {{venv_dir}}/bin/pip install -r requirements.txt

test:
    PATH="{{venv_dir}}/bin:$PATH" PRE_COMMIT_HOME="{{pre_commit_home}}" pytest tests -vvv

pre-commit:
    PATH="{{venv_dir}}/bin:$PATH" PRE_COMMIT_HOME="{{pre_commit_home}}" pre-commit run --all-files --verbose

check: install test pre-commit
    @:

clean:
    rm -rf {{venv_dir}} {{pre_commit_home}} .pytest_cache .mypy_cache
