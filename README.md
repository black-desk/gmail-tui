<!-- SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn> -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Gmail TUI

[![CI](https://github.com/black-desk/gmail-tui/actions/workflows/ci.yml/badge.svg)](https://github.com/black-desk/gmail-tui/actions/workflows/ci.yml)
[![REUSE status](https://api.reuse.software/badge/github.com/black-desk/gmail-tui)](https://api.reuse.software/info/github.com/black-desk/gmail-tui)
[![Dependabot Status](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/black-desk/gmail-tui/blob/master/.github/dependabot.yml)

A terminal user interface for Gmail, built with Python and Textual.

## Features

- Modern terminal user interface
- Keyboard-driven interface

## Installation

This project is not yet available on PyPI. You can install it directly from GitHub:

```bash
# Install with pip from GitHub
pip install git+https://github.com/black-desk/gmail-tui.git

# Install with uv from GitHub
uv pip install git+https://github.com/black-desk/gmail-tui.git

# Or clone the repository and install locally
git clone https://github.com/black-desk/gmail-tui.git
cd gmail-tui
uv sync --extra dev
```

## Usage

Gmail TUI provides a command-line interface with several subcommands:

```bash
# Launch the TUI application
gmail-tui

# Initialize configuration (first-time setup)
gmail-tui init

# List emails in a folder
gmail-tui ls

# Display email folders in tree format
gmail-tui tree
```

### Available Commands

- `init`: Initialize Gmail TUI configuration
- `ls`: List emails in a folder (outputs metadata in various formats)
- `tree`: Display email folders in tree format

For more details on each command, use the `--help` option:

```bash
gmail-tui --help
gmail-tui <command> --help
```

## Contributing

If you're interested in contributing to Gmail TUI, please check the [Contributing Guidelines](CONTRIBUTING.md) for instructions on development, code style, and licensing requirements.

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later). The project follows the [REUSE Specification](https://reuse.software/spec/) for license and copyright information. For details on license compliance, please see the [Contributing Guidelines](CONTRIBUTING.md).