import argparse
import sqlite3
import os
from datetime import datetime

# Initialize the SQLite database within the same folder
DB_FILE = os.path.join(os.path.dirname(__file__), 'tasks.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO tasks (title, status, created_at) VALUES (?, ?, ?)', (title, 'pending', created_at))
    conn.commit()
    print(f"✅ Task added: '{title}'")
    conn.close()

def list_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, status, created_at FROM tasks')
    tasks = cursor.fetchall()
    conn.close()

    if not tasks:
        print("📭 No tasks found. Add a task using 'python file_manager.py add \"<task>\"'.")
        return

    print(f"\n{'ID':<5} | {'Status':<12} | {'Title':<40} | {'Created At':<20}")
    print("-" * 85)
    for t_id, title, status, created_at in tasks:
        icon = "✅ Done" if status == 'completed' else "⏳ Pending"
        print(f"{t_id:<5} | {icon:<12} | {title:<40} | {created_at:<20}")
    print()

def complete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', ('completed', task_id))
    if cursor.rowcount > 0:
        print(f"🎉 Task {task_id} marked as complete!")
    else:
        print(f"⚠️  Task {task_id} not found.")
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    if cursor.rowcount > 0:
        print(f"🗑️  Task {task_id} deleted.")
    else:
        print(f"⚠️  Task {task_id} not found.")
    conn.commit()
    conn.close()

def main():
    init_db()
    parser = argparse.ArgumentParser(description="Pure Python CLI Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('title', type=str, help='The title of the task')

    # List command
    parser_list = subparsers.add_parser('list', help='List all tasks')

    # Complete command
    parser_done = subparsers.add_parser('done', help='Mark a task as complete')
    parser_done.add_argument('id', type=int, help='The ID of the task to complete')

    # Delete command
    parser_del = subparsers.add_parser('delete', help='Delete a task')
    parser_del.add_argument('id', type=int, help='The ID of the task to delete')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.title)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'done':
        complete_task(args.id)
    elif args.command == 'delete':
        delete_task(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
