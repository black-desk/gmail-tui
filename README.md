<!-- SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn> -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Gmail TUI

A terminal user interface for Gmail, built with Python and Textual.

## Features

- Modern terminal user interface
- Keyboard-driven interface

## Installation

```bash
# Install with pip
pip install gmail-tui

# Or install with Poetry
poetry install
```

## Usage

```bash
gmail-tui
```

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/black-desk/gmail-tui.git
   cd gmail-tui
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run tests:
   ```bash
   poetry run pytest
   ```

4. Format code:
   ```bash
   poetry run ruff format .
   ```

5. Check code style:
   ```bash
   poetry run ruff check .
   ```

6. Verify license compliance:
   ```bash
   git clean -fdx
   poetry run reuse lint
   ```

## License

The project follows the [REUSE Specification](https://reuse.software/spec/) for license and copyright information. All files contain SPDX license and copyright headers, making it easy to verify the license status of any file in the project.

To verify the license compliance, you can run:
```bash
# Clean untracked files first
git clean -fdx

# Then run reuse lint
poetry run reuse lint
```