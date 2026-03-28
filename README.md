# 🌌 Cosmos File Explorer & Task Manager

A stunning, modern, dual-mode Python application that brings a high-end glassmorphic UI to your local file system, combined with a built-in CLI productivity task manager. 

![Cosmos Theme](https://img.shields.io/badge/Theme-Glassmorphic_Cosmic-purple.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)

## ✨ Features

### 📁 1. The Glassmorphic File Explorer (`app.py`)
A beautiful file navigation GUI running on a totally local Flask server, wrapped natively in `PyWebView` for a desktop-app experience.
* **Dual-Mode Operation:** Run it as a floating native desktop window or seamlessly open it in your web browser at `http://localhost:5050`.
* **Smart System Navigation:** Built-in sidebar shortcuts to `Desktop`, `Documents`, `Downloads`, `Pictures`, and `Videos`. 
* *OneDrive Backup Safe:* Intelligently detects and adapts if your default Windows folders are backed up to your localized OneDrive.
* **Animated Aesthetics:** Fully transparent glass panels `backdrop-filter: blur()`, glowing accents, and an ambient slowly-panning cosmic background image.
* **Actions:** View folder contents, rename files, instantly organize messy directories by extension, and double click to dynamically open PC files.

### ✅ 2. Pure Python CLI Task Manager (`file_manager.py`)
A lightweight, lightning-fast terminal-based To-Do list that drops external dependencies and stores your data firmly locally using the built-in SQLite `tasks.db`.
* `python file_manager.py add "Task Title"` — Add tasks easily to the `.db`.
* `python file_manager.py list` — View all pending/completed tasks.
* `python file_manager.py done <id>` — Check a task off your list.
* `python file_manager.py delete <id>` — Permanently delete a task.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/python_file_explorer.git
   cd python_file_explorer
   ```

2. **Install the dependencies:**
   This project specifically uses Flask for the server structure and PyWebView to draw the desktop window.
   ```bash
   pip install flask pywebview
   ```

3. **Launch the Explorer:**
   ```bash
   python app.py
   ```
   *(This will automatically launch the native app window! To use it as a web app, simply minimize the window and go to `http://127.0.0.1:5050` in Chrome).*

## 🛠️ Stack & Technologies
* **Backend logic:** Python (Flask web server, OS commands).
* **Storage:** Local Python `sqlite3` built-in database (`tasks.db`).
* **Frontend structure:** Vanilla HTML, CSS (`style.css`), and JavaScript (`script.js`).
* **Icons:** [Phosphor Icons](https://phosphoricons.com/).

## 💡 Notes
When shutting down the file explorer, you may notice a `KeyboardInterrupt` inside the terminal. This is standard expected behavior as `PyWebView` actively monitors for the `CTRL+C` shutdown request or window closure.
