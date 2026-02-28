<!-- SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn> -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Roadmap

This document lists planned features that are not yet implemented.

The primary use case is reading emails from open-source project mailing lists.

---

## CLI Commands

### Implemented

| Command | Description |
|---------|-------------|
| `gmail-tui init` | Initialize configuration |
| `gmail-tui ls [folder]` | List emails in folder |
| `gmail-tui show <uid>` | Display full email content (supports uid or message-id) |
| `gmail-tui tree` | Display folder tree |
| `gmail-tui mkdir <folder>` | Create a new folder |
| `gmail-tui mv <src> <dest>` | Move or rename folder |
| `gmail-tui rm <folder>` | Delete a folder |
| `gmail-tui threads [folder]` | List threads (grouped by conversation) |
| `gmail-tui search <query>` | Search emails by sender/subject/content |

### Planned

| Command | Description | Status |
|---------|-------------|--------|
| `gmail-tui thread <message-id>` | Display all emails in a thread (any message-id in the thread) | ❌ |

### CLI Arguments Design

```
gmail-tui ls [folder] [options]
  -l, --limit N       Max emails to show (default: 20)
  -f, --format FMT    Output format: json/yaml/toml (default: json)

gmail-tui show <id> [options]
  <id>                Email identifier: uid (number) or message-id (e.g. <xxx@example.com>)
  -f, --format FMT    Output format: json/yaml/toml/raw (default: raw)
  --include-headers   Show all headers

gmail-tui threads [folder] [options]
  -l, --limit N       Max threads to show (default: 20)
  -f, --format FMT    Output format: json/yaml/toml (default: json)

gmail-tui thread <message-id> [options]
  <message-id>        Any message-id from the thread, will find root automatically
  -f, --format FMT    Output format: json/yaml/toml (default: json)

gmail-tui search <query> [options]
  --from ADDR         Filter by sender
  --to ADDR           Filter by recipient
  --subject TEXT      Filter by subject
  --body TEXT         Search in email body
  --address ADDR      Find threads involving this address (from/to/cc)
  -l, --limit N       Max results (default: 20)
  -f, --format FMT    Output format: json/yaml/toml (default: json)
```

---

## TUI Features

### Essential

- [ ] **Thread View** - Group and display emails by conversation thread (critical for mailing lists)
- [ ] **Email Detail View** - Display full email body (plain text focus, basic HTML support)

### Navigation

- [ ] **Open Email** (`o`) - View selected email
- [ ] **Scroll Content** - Navigate long emails (`j`/`k`)

### Search & Filter

- [ ] **Search Dialog** (`/`) - Search by sender, subject, or content
- [ ] **Search Navigation** (`n`/`N`) - Jump between search results
- [ ] **Find Threads by Address** - Show all threads involving a specific email address (as sender, recipient, or CC)

### UI/UX

- [ ] **Help Screen** (`?`) - Display key bindings
- [ ] **Loading Indicators** - Visual feedback during operations
- [ ] **Error Messages** - User-friendly error display

### Nice to Have

- [ ] **Mark Read/Unread** (`m`) - Toggle seen flag
- [ ] **Star/Unstar** (`s`) - Mark important threads
- [ ] **Archive** (`a`) - Remove from inbox after reading
