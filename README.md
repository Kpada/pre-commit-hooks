# Pre-commit Hooks

A set of [pre-commit](https://pre-commit.com/) hooks for various languages.

## Supported Hooks

- [shfmt](https://github.com/mvdan/sh)

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
