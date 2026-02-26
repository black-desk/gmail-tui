# Contributing Guidelines

## Code Style

### Comments and Documentation
- All comments and documentation should be written in English
- Use clear and concise language
- Follow Python docstring conventions (Google style)
- Include type hints for function parameters and return values

### Coding Standards
- Avoid trailing whitespace at the end of lines
- Use 4 spaces for indentation (no tabs)
- Keep line length under 88 characters

### Commit Messages
- Write commit messages in English
- Follow [Conventional Commits](https://www.conventionalcommits.org/) format

### Licensing and Copyright

This project follows the [REUSE Specification](https://reuse.software/spec/) for license and copyright information. The following guidelines should be followed:

1. All source files must include SPDX license and copyright information directly in file headers:
   ```python
   """Module description.

   SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
   SPDX-License-Identifier: GPL-3.0-or-later
   """
   ```

2. Only use `.reuse/dep5` for files that cannot include inline license headers (e.g., binary files, data files)

3. To verify license compliance before submitting your contribution:
   ```bash
   # Clean untracked files first
   git clean -fdx

   # Run reuse lint
   uv run reuse lint
   ```

## Development Process

1. Clone the repository:
   ```bash
   git clone https://github.com/black-desk/gmail-tui.git
   cd gmail-tui
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Format code:
   ```bash
   uv run ruff format .
   ```

5. Check code style:
   ```bash
   uv run ruff check .
   ```

6. Check for trailing whitespace:
   ```bash
   uv run python scripts/check_trailing_whitespace.py
   ```

7. Verify license compliance:
   ```bash
   git clean -fdx
   uv run reuse lint
   ```

## Continuous Integration

This project uses GitHub Actions for continuous integration. The following checks are run on every pull request and push to the main branch:

1. **CI Workflow**: Runs on multiple Python versions and performs:
   - Trailing whitespace checks
   - Formatting checks
   - Code style checks
   - Unit tests

2. **REUSE Compliance**: Ensures all files have proper copyright and license information.

3. **Dependabot**: Automatically checks for dependency updates and security vulnerabilities.
   - Creates pull requests for outdated dependencies
   - Flags dependencies with known security issues
   - Updates GitHub Actions workflows

These checks help maintain code quality and consistency. Pull requests will not be merged until all checks pass.

For local development, make sure to run the same checks before submitting a pull request:

```bash
# Run all checks
uv run python scripts/check_trailing_whitespace.py
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run reuse lint
```