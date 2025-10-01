# School Management System
A compact Python example that demonstrates OOP design, two GUI front ends (Tkinter and PyQt5), JSON/CSV exporting, and an SQLite3-backed datastore.  
The application window is titled **“School Management System.”**


## Requirements
- Python ≥ 3.10  
- PyQt5 (for the Qt UI):  
  ```bash
  pip install PyQt5

## How to Run
Tkinter (default):
python main.py
# or
python main.py --tk

## PyQt5
main.py --qt

## Save & Export

Save to JSON: Click Save JSON in either GUI to dump a snapshot of the DB via storage.py.
Export to CSV: Use Export CSV (available in both GUIs) to generate a single CSV file with a type column (student / instructor / course).

Flattening details:
Students: registered_course_ids stored as semicolon-separated IDs
Instructors: assigned_course_ids stored as semicolon-separated IDs
Courses: instructor_id is a single value; enrolled_student_ids are semicolon-separated

## SQLite Mode
The app runs in DB-only mode: all CRUD operations immediately persist to SQLite.

## Database Location & Backup
Default database file: school.db in the current working directory.
To create a backup, call:

from db import backup_database
backup_database("path/to/backup.db")

## Notes
Validation: Inputs are checked by validation.py; errors are presented in dialog boxes.
Search: Case-insensitive substring matching across name, ID, and course fields.

