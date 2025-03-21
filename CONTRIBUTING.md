# Contributing Guidelines

## Code Style

### Comments and Documentation
- All comments and documentation should be written in English
- Use clear and concise language
- Follow Python docstring conventions (Google style)
- Include type hints for function parameters and return values

### Commit Messages
- Write commit messages in English
- Follow [Conventional Commits](https://www.conventionalcommits.org/) format

### Licensing and Copyright
- All source files must include SPDX license and copyright information
- Add license and copyright information directly in file headers when possible:
  ```python
  """Module description.

  SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
  SPDX-License-Identifier: GPL-3.0-or-later
  """
  ```
- Only use `.reuse/dep5` for files that cannot include inline license headers (e.g. binary files, data files)
- Run `reuse lint` to verify license compliance