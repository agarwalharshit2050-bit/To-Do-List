# todo.py
# -----------------------------------------------
# Personal To-Do List Application (CLI, JSON persistence)
# Python 3.12 compatible, single-file, copy-paste ready
#
# Features:
# - Add tasks (title, description, category)
# - View tasks (all, by category, search)
# - Edit tasks (title, description, category)
# - Mark tasks completed/uncompleted
# - Delete tasks with confirmation
# - Categorization with quick-pick and custom categories
# - Persistent storage in tasks.json (created automatically)
# - Clean tabular display, input validation, friendly prompts
# - Optional: Export tasks to CSV (for sharing/reporting)
#
# How to run:
#   1) Save this file as "todo.py" in a folder.
#   2) Just run:  python todo.py
#   3) The app will create/maintain "tasks.json" in the same folder.
#
# Project structure (suggested):
# /todo_app
#  ├── todo.py
#  ├── tasks.json         (auto-created)
#  └── README.md          (you can write docs / paste PPT notes)
# -----------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import json
import csv
import os
from datetime import datetime

TASKS_FILE = "tasks.json"
DEFAULT_CATEGORIES = ["Work", "Personal", "Urgent"]

# ----------------------------
# Data model
# ----------------------------

@dataclass
class Task:
    id: int
    title: str
    description: str
    category: str
    completed: bool = False
    created_at: str = ""
    updated_at: str = ""

    def mark_completed(self) -> None:
        self.completed = True
        self.updated_at = now_iso()

    def mark_uncompleted(self) -> None:
        self.completed = False
        self.updated_at = now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Task":
        # Backward/robust loading defaults
        return Task(
            id=int(data.get("id", 0)),
            title=str(data.get("title", "")).strip(),
            description=str(data.get("description", "")).strip(),
            category=str(data.get("category", "Uncategorized")).strip() or "Uncategorized",
            completed=bool(data.get("completed", False)),
            created_at=str(data.get("created_at", now_iso())),
            updated_at=str(data.get("updated_at", now_iso())),
        )


# ----------------------------
# Utilities
# ----------------------------

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_tasks_file() -> None:
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_tasks() -> List[Task]:
    ensure_tasks_file()
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            if not isinstance(raw, list):
                return []
            return [Task.from_dict(item) for item in raw]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_tasks(tasks: List[Task]) -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)

def export_to_csv(tasks: List[Task], filename: str = "tasks_export.csv") -> None:
    fields = ["id", "title", "description", "category", "completed", "created_at", "updated_at"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for t in tasks:
            row = t.to_dict()
            row["completed"] = "Yes" if t.completed else "No"
            writer.writerow(row)

def next_task_id(tasks: List[Task]) -> int:
    return (max((t.id for t in tasks), default=0) + 1) if tasks else 1

def input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty. Please try again.")

def input_optional(prompt: str, current: Optional[str] = None) -> str:
    val = input(prompt).strip()
    return val if val else (current or "")

def input_choice(prompt: str, choices: List[str]) -> int:
    # Returns 1-based index
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            idx = int(val)
            if 1 <= idx <= len(choices):
                return idx
        print(f"Please enter a number between 1 and {len(choices)}.")

def input_int_in_range(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            v = int(s)
            if min_val <= v <= max_val:
                return v
        print(f"Enter a number between {min_val} and {max_val}.")

def confirm(prompt: str) -> bool:
    ans = input(f"{prompt} (y/n): ").strip().lower()
    return ans in ("y", "yes")

def print_divider(char: str = "─", width: int = 60) -> None:
    print(char * width)

def format_bool(b: bool) -> str:
    return "✔" if b else "✗"

def print_header(title: str) -> None:
    print_divider()
    print(title)
    print_divider()

def print_tasks_table(tasks: List[Task]) -> None:
    if not tasks:
        print("No tasks to display.")
        return
    # Columns: #, Title, Category, Completed, Updated
    headers = ["#", "Title", "Category", "Done", "Updated"]
    rows = []
    for idx, t in enumerate(tasks, start=1):
        rows.append([str(idx), t.title, t.category, format_bool(t.completed), t.updated_at])
    print_table(headers, rows)

def print_table(headers: List[str], rows: List[List[str]]) -> None:
    # Simple fixed-width table (no external libs)
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def line(sep_left="│", sep_mid="│", sep_right="│"):
        parts = []
        for i, h in enumerate(headers):
            parts.append(f" {h.ljust(col_widths[i])} ")
        print(sep_left + sep_mid.join(parts) + sep_right)

    def hrule(sep_left="┌", sep_mid="┬", sep_right="┐", fill="─"):
        parts = []
        for w in col_widths:
            parts.append(fill * (w + 2))
        print(sep_left + sep_mid.join(parts) + sep_right)

    def hrule_mid(sep_left="├", sep_mid="┼", sep_right="┤", fill="─"):
        parts = []
        for w in col_widths:
            parts.append(fill * (w + 2))
        print(sep_left + sep_mid.join(parts) + sep_right)

    def hrule_bottom(sep_left="└", sep_mid="┴", sep_right="┘", fill="─"):
        parts = []
        for w in col_widths:
            parts.append(fill * (w + 2))
        print(sep_left + sep_mid.join(parts) + sep_right)

    hrule()
    line()
    hrule_mid()
    for row in rows:
        parts = []
        for i, cell in enumerate(row):
            parts.append(f" {str(cell).ljust(col_widths[i])} ")
        print("│" + "│".join(parts) + "│")
    hrule_bottom()

def pause() -> None:
    input("\nPress Enter to continue...")

# ----------------------------
# Core actions
# ----------------------------

def choose_category(existing_categories: List[str]) -> str:
    print_header("Choose a category")
    cats = distinct_categories(existing_categories + DEFAULT_CATEGORIES)
    for i, c in enumerate(cats, start=1):
        print(f"{i}. {c}")
    print(f"{len(cats) + 1}. Create new category")
    choice = input_int_in_range(f"Select 1-{len(cats)+1}: ", 1, len(cats) + 1)
    if choice == len(cats) + 1:
        new_cat = input_nonempty("Enter new category name: ").strip()
        return new_cat
    return cats[choice - 1]

def distinct_categories(categories: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for c in categories:
        c = c.strip()
        if not c:
            continue
        if c not in seen:
            seen.add(c)
            ordered.append(c)
    return ordered

def add_task(tasks: List[Task]) -> None:
    print_header("Add a new task")
    title = input_nonempty("Title: ")
    description = input_nonempty("Description: ")
    user_categories = [t.category for t in tasks]
    category = choose_category(user_categories)
    task = Task(
        id=next_task_id(tasks),
        title=title,
        description=description,
        category=category,
        completed=False,
        created_at=now_iso(),
        updated_at=now_iso(),
    )
    tasks.append(task)
    save_tasks(tasks)
    print("\nTask added successfully.")

def view_tasks(tasks: List[Task]) -> None:
    print_header("All tasks")
    print_tasks_table(tasks)

def view_by_category(tasks: List[Task]) -> None:
    print_header("View tasks by category")
    cats = distinct_categories([t.category for t in tasks]) or ["Uncategorized"]
    for i, c in enumerate(cats, start=1):
        print(f"{i}. {c}")
    choice = input_int_in_range(f"Select 1-{len(cats)}: ", 1, len(cats))
    chosen = cats[choice - 1]
    filtered = [t for t in tasks if t.category == chosen]
    print_header(f"Category: {chosen}")
    print_tasks_table(filtered)

def search_tasks(tasks: List[Task]) -> None:
    print_header("Search tasks")
    query = input_nonempty("Enter keyword (title/description/category): ").lower()
    results = [t for t in tasks if query in t.title.lower() or query in t.description.lower() or query in t.category.lower()]
    print_header(f"Results for: {query}")
    print_tasks_table(results)

def select_task(tasks: List[Task], prompt: str = "Select task by #") -> Optional[Task]:
    if not tasks:
        print("No tasks available.")
        return None
    print_tasks_table(tasks)
    idx = input_int_in_range(f"{prompt} (1-{len(tasks)}): ", 1, len(tasks))
    return tasks[idx - 1]

def edit_task(tasks: List[Task]) -> None:
    print_header("Edit a task")
    task = select_task(tasks, "Choose a task to edit")
    if not task:
        return
    print("\nLeave a field empty to keep the current value.")
    new_title = input_optional(f"New title [{task.title}]: ", current=task.title).strip()
    new_desc = input_optional(f"New description [{task.description}]: ", current=task.description).strip()

    print("\nCategory options:")
    user_categories = [t.category for t in tasks]
    cats = distinct_categories(user_categories + DEFAULT_CATEGORIES)
    for i, c in enumerate(cats, start=1):
        print(f"{i}. {c}")
    print(f"{len(cats) + 1}. Keep current ({task.category})")
    print(f"{len(cats) + 2}. Create new category")

    cat_choice = input_int_in_range(f"Select 1-{len(cats)+2}: ", 1, len(cats) + 2)
    if cat_choice == len(cats) + 1:
        new_cat = task.category
    elif cat_choice == len(cats) + 2:
        new_cat = input_nonempty("Enter new category name: ").strip()
    else:
        new_cat = cats[cat_choice - 1]

    task.title = new_title or task.title
    task.description = new_desc or task.description
    task.category = new_cat or task.category
    task.updated_at = now_iso()
    save_tasks(tasks)
    print("\nTask updated successfully.")

def toggle_complete_task(tasks: List[Task]) -> None:
    print_header("Mark task completed/uncompleted")
    task = select_task(tasks, "Choose a task to toggle status")
    if not task:
        return
    if task.completed:
        task.mark_uncompleted()
        print(f"\nMarked as NOT completed: {task.title}")
    else:
        task.mark_completed()
        print(f"\nMarked as completed: {task.title}")
    save_tasks(tasks)

def delete_task(tasks: List[Task]) -> None:
    print_header("Delete a task")
    task = select_task(tasks, "Choose a task to delete")
    if not task:
        return
    print(f"\nYou are about to delete: '{task.title}' (Category: {task.category})")
    if confirm("Are you sure"):
        tasks.remove(task)
        save_tasks(tasks)
        print("Task deleted.")
    else:
        print("Deletion cancelled.")

def show_stats(tasks: List[Task]) -> None:
    print_header("Task stats")
    total = len(tasks)
    done = sum(1 for t in tasks if t.completed)
    pending = total - done
    cats = distinct_categories([t.category for t in tasks])
    print(f"Total tasks: {total}")
    print(f"Completed: {done}")
    print(f"Pending: {pending}")
    print("\nBy category:")
    if cats:
        for c in cats:
            c_total = sum(1 for t in tasks if t.category == c)
            c_done = sum(1 for t in tasks if t.category == c and t.completed)
            print(f"- {c}: {c_done}/{c_total} done")
    else:
        print("- None")

def export_tasks_menu(tasks: List[Task]) -> None:
    print_header("Export tasks to CSV")
    filename = input_optional("Filename [tasks_export.csv]: ", current="tasks_export.csv").strip() or "tasks_export.csv"
    export_to_csv(tasks, filename)
    print(f"\nExported to '{filename}' successfully.")

# ----------------------------
# Main menu / App loop
# ----------------------------

def main() -> None:
    tasks = load_tasks()
    while True:
        print_header("Personal To-Do List")
        print("1. Add task")
        print("2. View all tasks")
        print("3. View by category")
        print("4. Search tasks")
        print("5. Edit a task")
        print("6. Mark completed/uncompleted")
        print("7. Delete a task")
        print("8. Show stats")
        print("9. Export to CSV")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(tasks)
            pause()
        elif choice == "2":
            view_tasks(tasks)
            pause()
        elif choice == "3":
            view_by_category(tasks)
            pause()
        elif choice == "4":
            search_tasks(tasks)
            pause()
        elif choice == "5":
            edit_task(tasks)
            pause()
        elif choice == "6":
            toggle_complete_task(tasks)
            pause()
        elif choice == "7":
            delete_task(tasks)
            pause()
        elif choice == "8":
            show_stats(tasks)
            pause()
        elif choice == "9":
            export_tasks_menu(tasks)
            pause()
        elif choice == "0":
            print("\nSaving and exiting... Bye!")
            save_tasks(tasks)
            break
        else:
            print("Invalid choice. Please try again.")
            pause()

if __name__ == "__main__":
    main()

