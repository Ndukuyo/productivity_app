# productivity_app

A secure RESTful API for managing personal journal entries with session-based authentication.

## Features

- User authentication (register, login, logout)
- Journal entry CRUD operations
- Pagination for listing entries
- User data isolation (users can only access their own entries)
- Mood tracking for entries

## Installation

1. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate