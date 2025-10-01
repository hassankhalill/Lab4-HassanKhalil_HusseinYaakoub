import sys
import os
# Add the parent directory to Python path so we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tkinter as tk
from tkinter import ttk, messagebox
from backend.models import Student, Instructor, Course
from backend.storage import Repository, save_to_json, save_to_csv, load_from_json
from backend.validation import validate_age, validate_email, validate_non_empty
import backend.db as db



students = []
instructors = []
courses = []

def add_student():
    """
    Create a Student from the entry fields, add it to memory, and persist to the DB.

    :raises Exception: If any field is invalid or DB insertion fails.
    :return: None
    """
    try:
        # Validate input using backend validation
        name = validate_non_empty(entry_student_name.get(), "name")
        age = validate_age(int(entry_student_age.get()))
        email = validate_email(entry_student_email.get())
        student_id = validate_non_empty(entry_student_id.get(), "student_id")
        
        # Create student instance
        s = Student(name, age, email, student_id)
        students.append(s)

        # Add to database using backend db functions
        db.cr_st(s.st_id, s.nm, s.ag, s._em)
        refresh_table()
        refresh_dropdowns()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_instructor():
    """
    Create an Instructor from the entry fields, add it to memory, and persist to the DB.

    :raises Exception: If any field is invalid or DB insertion fails.
    :return: None
    """
    try:
        # Validate input using backend validation
        name = validate_non_empty(entry_instructor_name.get(), "name")
        age = validate_age(int(entry_instructor_age.get()))
        email = validate_email(entry_instructor_email.get())
        instructor_id = validate_non_empty(entry_instructor_id.get(), "instructor_id")
        
        # Create instructor instance
        i = Instructor(name, age, email, instructor_id)
        instructors.append(i)

        # Add to database using backend db functions
        db.cr_in(i.in_id, i.nm, i.ag, i._em)
        refresh_table()
        refresh_dropdowns()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_course():
    """
    Create a Course from the entry fields, add it to memory, and persist to the DB.

    :raises Exception: If any field is invalid or DB insertion fails.
    :return: None
    """
    try:
        # Validate input using backend validation
        course_id = validate_non_empty(entry_course_id.get(), "course_id")
        course_name = validate_non_empty(entry_course_name.get(), "course_name")
        
        # Create course instance
        c = Course(course_id, course_name)
        courses.append(c)

        # Add to database using backend db functions
        db.cr_cs(c.crs_id, c.crs_nm, None)
        refresh_table()
        refresh_dropdowns()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def register_student_to_course():
    """
    Register the selected student to the selected course (memory + DB).

    :raises Exception: If selections are invalid or DB insertion fails.
    :return: None
    """
    try:
        sid = student_dropdown.get()
        cid = course_dropdown.get()

        student = next(s for s in students if s.st_id == sid)
        course = next(c for c in courses if c.crs_id == cid)
        student.register_course(course)

        course.add_student(student)
        db.en_st(sid, cid)  # Enroll student using backend db function
        refresh_table()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def assign_instructor_to_course():
    """
    Assign the selected instructor to the selected course (memory + DB).

    :raises Exception: If selections are invalid or DB update fails.
    :return: None
    """
    try:
        iid = instructor_dropdown.get()
        cid = course_dropdown2.get()

        instructor = next(i for i in instructors if i.in_id == iid)
        course = next(c for c in courses if c.crs_id == cid)
        instructor.assign_course(course)

        course.ins = instructor  # Use correct attribute name
        db.up_cs(cid, course.crs_nm, iid)  # Update course with instructor using backend db function
        refresh_table()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def search_records():
    """
    Search students, instructors, and courses by name or ID and display matches.

    :return: None
    """
    query = search_entry.get().lower()

    for row in tree.get_children():
        tree.delete(row)

    for s in students:
        if query in s.nm.lower() or query in s.st_id.lower():
            tree.insert("", "end", values=("Student", s.nm, s.st_id))

    for i in instructors:
        if query in i.nm.lower() or query in i.in_id.lower():
            tree.insert("", "end", values=("Instructor", i.nm, i.in_id))

    for c in courses:
        if query in c.crs_nm.lower() or query in c.crs_id.lower():
            tree.insert("", "end", values=("Course", c.crs_nm, c.crs_id))

def edit_record():
    """
    Edit the selected record (Student, Instructor, or Course) using a popup window.

    :return: None
    """
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a record to edit.")
        return

    item = tree.item(selected[0])
    typ, name, id_ = item["values"]

    popup = tk.Toplevel(root)
    popup.title(f"Edit {typ}")

    # Pre-fill fields
    tk.Label(popup, text="Name").grid(row=0, column=0)
    entry_name = tk.Entry(popup)
    entry_name.grid(row=0, column=1)

    tk.Label(popup, text="Age").grid(row=1, column=0)
    entry_age = tk.Entry(popup)
    entry_age.grid(row=1, column=1)

    tk.Label(popup, text="Email").grid(row=2, column=0)
    entry_email = tk.Entry(popup)
    entry_email.grid(row=2, column=1)

    # Pre-populate with current data
    obj = None
    if typ == "Student":
        obj = next(s for s in students if s.st_id == id_)
        entry_name.insert(0, obj.nm)
        entry_age.insert(0, obj.ag)
        entry_email.insert(0, obj._em)
    elif typ == "Instructor":
        obj = next(i for i in instructors if i.in_id == id_)
        entry_name.insert(0, obj.nm)
        entry_age.insert(0, obj.ag)
        entry_email.insert(0, obj._em)
    elif typ == "Course":
        obj = next(c for c in courses if c.crs_id == id_)
        entry_name.insert(0, obj.crs_nm)
        entry_age.insert(0, "")  
        entry_email.insert(0, "")  

    def save_changes():
        """
        Save the updated details of the selected record (Student, Instructor, or Course).

        This function updates both the in-memory object and the database entry 
        based on the modified values entered in the popup window. After saving, 
        the display table and dropdowns are refreshed, and a success message is shown.

        :global typ: A string indicating the type of record being edited 
                    (`"Student"`, `"Instructor"`, or `"Course"`).
        :global obj: The object instance (Student, Instructor, or Course) being edited.
        :global popup: The Tkinter popup window used for editing.
        :raises ValueError: If `new_age` cannot be converted to an integer (when editing Student or Instructor).
        :return: None
        :rtype: None
        """
        new_name = entry_name.get()
        new_age = entry_age.get()
        new_email = entry_email.get()

        if typ == "Student" and obj is not None:
            obj.nm, obj.ag, obj._em = new_name, int(new_age), new_email
            db.up_st(obj.st_id, obj.nm, obj.ag, obj._em)

        elif typ == "Instructor" and obj is not None:
            obj.nm, obj.ag, obj._em = new_name, int(new_age), new_email
            db.up_in(obj.in_id, obj.nm, obj.ag, obj._em)

        elif typ == "Course" and obj is not None:
            obj.crs_nm = new_name
            db.up_cs(obj.crs_id, obj.crs_nm, obj.ins.in_id if obj.ins else None)

        refresh_table()
        refresh_dropdowns()
        popup.destroy()
        messagebox.showinfo("Success", f"{typ} updated successfully!")

    tk.Button(popup, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)


def delete_record():
    """
    Delete the selected row (student/instructor/course) from memory and DB.

    :return: None
    """
    selected = tree.selection()
    if not selected:
        return
    
    item = tree.item(selected[0])
    typ, name, id_ = item["values"]

    if typ == "Student":
        students[:] = [s for s in students if s.st_id != id_]
        db.dl_st(id_)

    elif typ == "Instructor":
        instructors[:] = [i for i in instructors if i.in_id != id_]
        db.dl_in(id_)

    elif typ == "Course":
        courses[:] = [c for c in courses if c.crs_id != id_]
        db.dl_cs(id_)

    refresh_table()
    refresh_dropdowns()

def save_all():
    """
    Serialize current lists (students/instructors/courses) and save to JSON.

    :return: None
    """
    try:
        # Create a repository and populate it with current data
        repo = Repository()
        repo.students = students[:]
        repo.instructors = instructors[:]
        repo.courses = courses[:]
        
        # Save using backend storage function
        save_to_json(repo, "school.json")
        messagebox.showinfo("Saved", "Data saved to school.json")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_all():
    """
    Load and display JSON data from disk and merge with current data.

    :raises Exception: If the file cannot be read or parsed.
    :return: None
    """
    try:
        # Load using backend storage function
        repo, _ = load_from_json("school.json")
        messagebox.showinfo("Loaded", f"Data loaded from school.json")
        
        # Optionally merge loaded data with current lists
        # This is a simple demonstration - you might want more sophisticated merging
        students.extend(repo.students)
        instructors.extend(repo.instructors)  
        courses.extend(repo.courses)
        refresh_table()
        refresh_dropdowns()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def refresh_table():
    """
    Refresh the Treeview with the current students, instructors, and courses.

    :return: None
    """
    for row in tree.get_children():
        tree.delete(row)

    for s in students:
        tree.insert("", "end", values=("Student", s.nm, s.st_id))

    for i in instructors:
        tree.insert("", "end", values=("Instructor", i.nm, i.in_id))

    for c in courses:
        inst_name = c.ins.nm if c.ins else "None"
        tree.insert("", "end", values=("Course", c.crs_nm, f"{c.crs_id} ({inst_name})"))

def refresh_dropdowns():
    """
    Update the Combobox options for students, instructors, and courses.

    :return: None
    """
    student_dropdown["values"] = [s.st_id for s in students]
    instructor_dropdown["values"] = [i.in_id for i in instructors]
    course_dropdown["values"] = [c.crs_id for c in courses]
    course_dropdown2["values"] = [c.crs_id for c in courses]

def preload_data():
    """
    Load data from the database into the in-memory lists at startup.

    :return: None
    """
    # Initialize database first
    db.in_db()
    
    # Load students from database
    for st_id, name, age, email in db.ls_st():
        students.append(Student(name, age, email, st_id))

    # Load instructors from database
    for in_id, name, age, email in db.ls_in():
        instructors.append(Instructor(name, age, email, in_id))

    # Load courses from database
    for crs_id, name, instructor_id in db.ls_cs():
        instr = next((i for i in instructors if i.in_id == instructor_id), None)
        course = Course(crs_id, name, instr)
        courses.append(course)
        
        # Load student enrollments for this course
        for st_id in db.ls_cs_st(crs_id):
            student = next((s for s in students if s.st_id == st_id), None)
            if student:
                course.add_student(student)
                student.register_course(course)

if __name__ == "__main__":
    print("Script started")
    root = tk.Tk()
    root.title("School Management System")

    tk.Label(root, text="Student Name").grid(row=0, column=0)
    entry_student_name = tk.Entry(root); entry_student_name.grid(row=0, column=1)

    tk.Label(root, text="Age").grid(row=1, column=0)
    entry_student_age = tk.Entry(root); entry_student_age.grid(row=1, column=1)

    tk.Label(root, text="Email").grid(row=2, column=0)
    entry_student_email = tk.Entry(root); entry_student_email.grid(row=2, column=1)

    tk.Label(root, text="Student ID").grid(row=3, column=0)
    entry_student_id = tk.Entry(root); entry_student_id.grid(row=3, column=1)

    tk.Button(root, text="Add Student", command=add_student).grid(row=4, column=0, columnspan=2)

    tk.Label(root, text="Instructor Name").grid(row=0, column=2)
    entry_instructor_name = tk.Entry(root); entry_instructor_name.grid(row=0, column=3)

    tk.Label(root, text="Age").grid(row=1, column=2)
    entry_instructor_age = tk.Entry(root); entry_instructor_age.grid(row=1, column=3)

    tk.Label(root, text="Email").grid(row=2, column=2)
    entry_instructor_email = tk.Entry(root); entry_instructor_email.grid(row=2, column=3)

    tk.Label(root, text="Instructor ID").grid(row=3, column=2)
    entry_instructor_id = tk.Entry(root); entry_instructor_id.grid(row=3, column=3)

    tk.Button(root, text="Add Instructor", command=add_instructor).grid(row=4, column=2, columnspan=2)

    tk.Label(root, text="Course Name").grid(row=0, column=4)
    entry_course_name = tk.Entry(root); entry_course_name.grid(row=0, column=5)

    tk.Label(root, text="Course ID").grid(row=1, column=4)
    entry_course_id = tk.Entry(root); entry_course_id.grid(row=1, column=5)

    tk.Button(root, text="Add Course", command=add_course).grid(row=2, column=4, columnspan=2)

    student_dropdown = ttk.Combobox(root, values=[])
    course_dropdown = ttk.Combobox(root, values=[])
    tk.Button(root, text="Register Student to Course", command=register_student_to_course).grid(row=5, column=0)
    student_dropdown.grid(row=5, column=1)
    course_dropdown.grid(row=5, column=2)

    instructor_dropdown = ttk.Combobox(root, values=[])
    course_dropdown2 = ttk.Combobox(root, values=[])
    tk.Button(root, text="Assign Instructor to Course", command=assign_instructor_to_course).grid(row=6, column=0)
    instructor_dropdown.grid(row=6, column=1)
    course_dropdown2.grid(row=6, column=2)

    tk.Label(root, text="Search").grid(row=7, column=0)
    search_entry = tk.Entry(root); search_entry.grid(row=7, column=1)
    tk.Button(root, text="Search", command=search_records).grid(row=7, column=2)

    cols = ("Type", "Name", "ID")
    tree = ttk.Treeview(root, columns=cols, show="headings")
    for col in cols: tree.heading(col, text=col)
    tree.grid(row=8, column=0, columnspan=6)

    tk.Button(root, text="Edit", command=edit_record).grid(row=9, column=0)
    tk.Button(root, text="Delete", command=delete_record).grid(row=9, column=1)
    tk.Button(root, text="Save Data", command=save_all).grid(row=10, column=0)
    tk.Button(root, text="Load Data", command=load_all).grid(row=10, column=1)

    # Load existing data from database
    preload_data()
    refresh_table()
    refresh_dropdowns()

    root.mainloop()
