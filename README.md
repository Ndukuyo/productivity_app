# productivity_app

A productivity app for managing personal journal entries with session-based authentication.

# Description

This App allows users to create, read, update, and delete journal entries with full authentication and authorization. Each user can only access their own journal entries, ensuring data privacy and security.

Perfect for journaling apps, note-taking applications, or any personal tracking system where users need to manage their own private content.

## Features

- User authentication (register, login, logout)
- Password Security
- Journal entry CRUD operations
- Pagination for listing entries
- User data isolation (users can only access their own entries)
- Mood tracking for entries

## Setup and Installation

1. Install dependancies
pipenv install -r requirements.txt

2. Initialize database:
    -flask db init
    -flask db migrate -m "message"
    -flask db upgrade head 

3. Run the app
    python app.py
