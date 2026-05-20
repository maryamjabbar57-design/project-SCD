# Online Quiz Game Application

A professional, full-featured quiz application built with Python (Tkinter) and a modern Web interface.

## Features
- **User Authentication**: Secure login and registration.
- **Dynamic Quiz Engine**: Multiple categories and difficulty levels.
- **Real-time Timer**: Countdown system for every question.
- **Advanced Scoring**: Point calculation based on difficulty and penalties.
- **Admin Module**: Manage question bank via SQLite.
- **Web Version**: Premium glassmorphism design for browser-based play.

## Setup Instructions

### Python Version
1. Ensure Python 3.x is installed.
2. Run the application:
   ```bash
   python main.py
   ```
3. Default Admin Credentials:
   - Username: `admin`
   - Password: `admin123`

### Web Version
1. Open `app/web/index.html` in any modern browser.

## Project Structure
- `app/database`: SQLite management and schema.
- `app/gui`: Tkinter screens and UI logic.
- `app/models`: Core OOP classes.
- `app/web`: HTML/CSS/JS web implementation.
- `tests`: Unit tests for core logic.

## Software Engineering Concepts Applied
- **OOP**: Inheritance (for screens), Encapsulation (ScoreManager), and Polymorphism.
- **Modular Design**: Separation of concerns between UI, Logic, and Data.
- **Testing**: Automated unit tests for critical paths.
- **Lehman's Laws**: Adhered to "Continuing Change" and "Increasing Complexity" by maintaining a modular structure that allows for future enhancements.
