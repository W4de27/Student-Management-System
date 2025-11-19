"""
Student Management System - Professional CLI (Option A)
File: student_management_cli.py

Features:
- Clean, modular code structure
- Student class with JSON persistence (students.json)
- Add / View / Update / Delete / Search / Export CSV
- Friendly CLI with emojis/icons for actions and clear messages
- Robust input validation and confirmations
- Small animations without external libs
- Cross-platform clear screen

Usage:
$ python student_management_cli.py

Sample improvements compared to original:
- Fixed selection-index bugs when updating/deleting students
- Added partial name search and exact selection mapping
- Added export to CSV
- Improved error handling when reading/writing files
- Added helper utilities and consistent UX

Notes:
- This is a single-file CLI that creates/reads students.json in the same folder.
- No external dependencies required (works with Python 3.8+).

"""

import os
import sys
import json
import time
import csv
from typing import List, Dict, Tuple, Optional

# -----------------------------
# Constants & Utilities
# -----------------------------
ICON_ADD = "➕"
ICON_VIEW = "📋"
ICON_EDIT = "✏️"
ICON_DELETE = "🗑️"
ICON_SEARCH = "🔍"
ICON_OK = "✅"
ICON_ERROR = "❌"
ICON_LOADING = "⏳"
ICON_EXPORT = "📤"

DATA_FILENAME = "students.json"
CSV_FILENAME = "students.csv"


# -----------------------------
# Helper functions
# -----------------------------




def pause(message: str = "Press Enter to continue..."):
    input(f"\n{message}")
    time.sleep(0.5)


def animated_message(word: str, repeats: int = 3, delay: float = 0.4):
    for i in range(repeats):
        dots = '.' * ((i % 3) + 1)
        print(f"\r{ICON_LOADING} {word}{dots}   ", end='', flush=True)
        time.sleep(delay)
    print('\r' + ' ' * 40 + '\r', end='')


def safe_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# -----------------------------
# Data model
# -----------------------------
class Student:
    def __init__(self, name: str, age: int, grade: float):
        self.name = name.strip().title()
        self.age = int(age)
        self.grade = float(grade)

    def to_dict(self) -> Dict:
        return {"name": self.name, "age": self.age, "grade": self.grade}

    @staticmethod
    def from_dict(d: Dict) -> 'Student':
        return Student(d.get('name', ''), d.get('age', 0), d.get('grade', 0.0))


# -----------------------------
# Persistence
# -----------------------------

def get_data_path(filename: str = DATA_FILENAME) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


def load_students() -> List[Dict]:
    path = get_data_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        print(f"{ICON_ERROR} Warning: Could not read {DATA_FILENAME} (corrupt?). Starting with empty list.")
        pause()
        return []


def save_students(students: List[Dict]):
    path = get_data_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(students, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"{ICON_ERROR} Error saving data: {e}")
        pause()


def export_to_csv(students: List[Dict], filename: str = CSV_FILENAME):
    path = get_data_path(filename)
    try:
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'age', 'grade']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for s in students:
                writer.writerow({
                    'name': s.get('name', ''),
                    'age': s.get('age', ''),
                    'grade': s.get('grade', '')
                })
        print()
        print(f"{ICON_EXPORT} Exported {len(students)} students to {filename}")
        time.sleep(1)
    except IOError as e:
        print(f"{ICON_ERROR} Failed to export CSV: {e}")
        pause()


# -----------------------------
# Validations
# -----------------------------

def valid_name(name: str) -> bool:
    return bool(name and name.strip() and not name.strip().isdigit())

def valid_age(age: int) -> bool:
    return isinstance(age, int) and age > 0 and age < 150

def valid_grade(grade: float) -> bool:
    return isinstance(grade, (int, float)) and 0.0 <= float(grade) <= 20.0


# -----------------------------
# CRUD Operations
# -----------------------------

def add_student(students: List[Dict]):
    print()
    print(f"{ICON_ADD}  Add Student")
    print("=" * 40)

    name = input("Name: ").strip()
    if not valid_name(name):
        print(f"{ICON_ERROR} Invalid name.")
        pause()
        return

    age_input = input("Age: ")
    age = safe_int(age_input)
    if age is None or not valid_age(age):
        print(f"{ICON_ERROR} Invalid age. Must be positive integer.")
        pause()
        return

    grade_input = input("Grade (0 - 20): ")
    grade = safe_float(grade_input)
    if grade is None or not valid_grade(grade):
        print(f"{ICON_ERROR} Invalid grade. Must be a number between 0 and 20.")
        pause()
        return

    animated_message("Saving")
    s = Student(name, age, grade)
    students.append(s.to_dict())
    save_students(students)
    print(f"{ICON_OK} Student added: {s.name} — Age: {s.age}, Grade: {s.grade:.2f}")
    pause()


def display_students(students: List[Dict]):
    print()
    string = f"{ICON_VIEW}  Students List"
    print("=" * 52)
    print(f"{string:^52}")
    print("=" * 52)
    if not students:
        print("No students found.")
        pause()
        return

    # Show as table-like output
    for i, s in enumerate(students, 1):
        print(f"[{i}] {s.get('name', ''):20} | Age: {str(s.get('age', '')):3} | Grade: {float(s.get('grade', 0)):.2f}")
        time.sleep(0.2)
    print("=" * 52)
    avg = sum(float(s.get('grade', 0)) for s in students) / max(len(students), 1)
    print(f"Total: {len(students)} students — Average grade: {avg:.2f}")
    pause()


def find_students_by_name(students: List[Dict], query: str) -> List[Tuple[int, Dict]]:
    print()
    q = query.strip().lower()
    results = []
    for idx, s in enumerate(students):
        if q in s.get('name', '').lower():
            results.append((idx, s))
    return results


def choose_from_results(results: List[Tuple[int, Dict]]) -> Optional[int]:
    """Returns the actual index in students list based on user selection."""
    if not results:
        return None
    if len(results) == 1:
        return results[0][0]

    print("Select one of the results:")
    print("-" * 52)
    for i, (real_idx, s) in enumerate(results, 1):
        print(f"[{i}] {s.get('name', '')} — Age: {s.get('age', '')}, Grade: {float(s.get('grade', 0)):.2f}")
        time.sleep(0.2)
    print("-" * 52)

    print()
    choice = input(f"Enter number (1-{len(results)}) or 0 to cancel: ")
    c = safe_int(choice)
    if c is None or c < 0 or c > len(results):
        print(f"{ICON_ERROR} Invalid selection.")
        return None
    if c == 0:
        return None
    return results[c - 1][0]


def update_student(students: List[Dict]):
    print()
    string = f"{ICON_EDIT}  Update Student"
    print("=" * 52)
    print(f"{string:^52}")
    print("=" * 52)
    if not students:
        print("No students to update.")
        pause()
        return

    query = input("Search by name (partial allowed): ")
    results = find_students_by_name(students, query)
    if not results:
        print(f"{ICON_ERROR} No matches found.")
        pause()
        return

    real_index = choose_from_results(results)
    if real_index is None:
        animated_message("Cancelling")
        pause()
        return

    s = students[real_index]
    print()
    print("-" * 52)
    print(f"Selected: {s.get('name', '')} — Age: {s.get('age', '')}, Grade: {float(s.get('grade', 0)):.2f}")
    print("-" * 52)
    time.sleep(2)
    print()
    print("1) Update name")
    print("2) Update age")
    print("3) Update grade")
    print("0) Cancel")
    print()
    opt = input("Choose option: ")

    if opt == '1':
        new_name = input("New name: ").strip()
        if not valid_name(new_name):
            print(f"{ICON_ERROR} Invalid name.")
            pause()
            return
        s['name'] = new_name.title()

    elif opt == '2':
        new_age = safe_int(input("New age: "))
        if new_age is None or not valid_age(new_age):
            print(f"{ICON_ERROR} Invalid age.")
            pause()
            return
        s['age'] = new_age

    elif opt == '3':
        new_grade = safe_float(input("New grade (0-20): "))
        if new_grade is None or not valid_grade(new_grade):
            print(f"{ICON_ERROR} Invalid grade.")
            pause()
            return
        s['grade'] = float(new_grade)

    elif opt == '0':
        print("Cancelled.")
        pause()
        return

    else:
        print(f"{ICON_ERROR} Invalid choice.")
        pause()
        return

    animated_message("Updating")
    save_students(students)
    print(f"{ICON_OK} Student updated successfully.")
    pause()


def delete_student(students: List[Dict]):
    print()
    string = f"{ICON_DELETE}  Delete Student"
    print("=" * 52)
    print(f"{string:^52}")
    print("=" * 52)
    if not students:
        print("No students to delete.")
        pause()
        return

    query = input("Search by name (partial allowed): ")
    results = find_students_by_name(students, query)
    if not results:
        print(f"{ICON_ERROR} No matches found.")
        pause()
        return

    real_index = choose_from_results(results)
    if real_index is None:
        animated_message("Cancelling")
        pause()
        return

    print()
    s = students[real_index]
    print("You are about to delete:")
    time.sleep(1)
    print("-" * 52)
    print(f"{s.get('name', '')} — Age: {s.get('age', '')}, Grade: {float(s.get('grade', 0)):.2f}")
    print("-" * 52)
    print()
    time.sleep(2)
    confirm = input("Type 'delete' to confirm or anything else to cancel: ")
    if confirm.strip().upper() == 'DELETE':
        animated_message("Deleting")
        students.pop(real_index)
        save_students(students)
        print(f"{ICON_OK} Student deleted.")
    else:
        animated_message("Cancelling")
    pause()


# -----------------------------
# Main CLI
# -----------------------------

def main():
    students = load_students()
    while True:
        print("""
========================================
    Student Management System  —  CLI
========================================
        """)
        print(f"{ICON_ADD}  1) Add student")
        print(f"{ICON_VIEW}  2) View all students")
        print(f"{ICON_SEARCH}  3) Search student")
        print(f"{ICON_EDIT}   4) Update student")
        print(f"{ICON_DELETE}   5) Delete student")
        print(f"{ICON_EXPORT}  6) Export to CSV")
        print("    0) Exit")

        choice = input("\nEnter choice: ")
        if choice == '1':
            add_student(students)
        elif choice == '2':
            display_students(students)
        elif choice == '3':
            q = input("Name to search: ")
            results = find_students_by_name(students, q)
            print(f"{ICON_SEARCH}  Search results for '{q}':")
            print("-" * 52)
            if not results:
                print("No matches.")
            else:
                for i, (idx, s) in enumerate(results, 1):
                    print(f"[{i}] {s.get('name', '')} — Age: {s.get('age', '')}, Grade: {float(s.get('grade', 0)):.2f}")
                    time.sleep(0.2)
            pause()
        elif choice == '4':
            update_student(students)
        elif choice == '5':
            delete_student(students)
        elif choice == '6':
            export_to_csv(students)
            pause()
        elif choice == '0':
            for i in range(3):
                print("Exiting" + "." * (i + 1))
                time.sleep(1)
                os.system("cls" if os.name == "nt" else "clear")
            print("* Program closed successfully. Bye! * \n")
            break
        else:
            print(f"{ICON_ERROR} Invalid choice. Try again.")
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted — goodbye!')
        sys.exit(0)
