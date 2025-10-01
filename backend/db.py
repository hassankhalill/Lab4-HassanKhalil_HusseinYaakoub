"""SQLite database layer for the School Management System.

This module encapsulates all CRUD operations for students, instructors, and
courses, as well as enrollment relationships. It uses a single SQLite database
file referenced by :data:`DBP` and exposes convenience functions for
initialization and data access.

The API is intentionally small and stringly-typed to keep the GUI layers
decoupled from the database driver specifics.
"""

import os
import shutil
import sqlite3
from typing import Optional


DBP = os.path.join(os.getcwd(), "school.db")


def set_dp(pth):
    """Set the database path.

    :param pth: Absolute or relative path to the SQLite database file.
    :type pth: str
    """

    global DBP
    DBP = pth


def _cn():
    """Create a new SQLite connection with foreign keys enabled.

    :return: Open connection to :data:`DBP`.
    :rtype: sqlite3.Connection
    """

    cn = sqlite3.connect(DBP)
    cn.execute("PRAGMA foreign_keys = ON;")

    return cn


def in_db():
    """Initialize database schema if it does not exist.

    Creates the ``students``, ``instructors``, ``courses``, and ``registrations``
    tables with appropriate constraints.
    """
    with _cn() as cn:

        cr = cn.cursor()
        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age >= 0),
                email TEXT NOT NULL
            );
            """
        )

        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS instructors (
                instructor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age >= 0),
                email TEXT NOT NULL
            );
            """
        )

        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                instructor_id TEXT,
                FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
            );
            """
        )
        cr.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
            );
            """
        )
        cn.commit()


# --- Students


def cr_st(st, nm, ag, em):
    """Create a student.

    :param st: Student ID (primary key).
    :type st: str
    :param nm: Student name.
    :type nm: str
    :param ag: Student age (non-negative).
    :type ag: int
    :param em: Student email.
    :type em: str
    """

    with _cn() as cn:

        cn.execute(
            "INSERT INTO students(student_id, name, age, email) VALUES (?,?,?,?)",
            (st, nm, ag, em),
        )


def ls_st():
    """List all students.

    :return: List of tuples ``(student_id, name, age, email)``.
    :rtype: list[tuple[str, str, int, str]]
    """

    with _cn() as cn:

        cur = cn.execute("SELECT student_id, name, age, email FROM students")
        return list(cur.fetchall())


def up_st(st, nm, ag, em):
    """Update a student by ID.

    :param st: Student ID to update.
    :type st: str
    :param nm: New name.
    :type nm: str
    :param ag: New age.
    :type ag: int
    :param em: New email.
    :type em: str
    """

    with _cn() as cn:

        cn.execute("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",(nm, ag, em, st))


def dl_st(st):
    """Delete a student by ID.

    :param st: Student ID to delete.
    :type st: str
    """

    with _cn() as cn:

        cn.execute("DELETE FROM students WHERE student_id=?", (st,))



def cr_in(in_, nm, ag, em):
    """Create an instructor.

    :param in_: Instructor ID (primary key).
    :type in_: str
    :param nm: Instructor name.
    :type nm: str
    :param ag: Instructor age (non-negative).
    :type ag: int
    :param em: Instructor email.
    :type em: str
    """

    with _cn() as cn:
        cn.execute("INSERT INTO instructors(instructor_id, name, age, email) VALUES (?,?,?,?)",(in_, nm, ag, em))


def ls_in():
    """List all instructors.

    :return: List of tuples ``(instructor_id, name, age, email)``.
    :rtype: list[tuple[str, str, int, str]]
    """

    with _cn() as cn:

        cur = cn.execute("SELECT instructor_id, name, age, email FROM instructors")

        return list(cur.fetchall())

def up_in(in_, nm, ag, em):
    """Update an instructor by ID.

    :param in_: Instructor ID to update.
    :type in_: str
    :param nm: New name.
    :type nm: str
    :param ag: New age.
    :type ag: int
    :param em: New email.
    :type em: str
    """

    with _cn() as cn:

        cn.execute( "UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",(nm, ag, em, in_))


def dl_in(in_):
    """Delete an instructor by ID.

    Also clears any course assignments for the instructor.

    :param in_: Instructor ID to delete.
    :type in_: str
    """

    with _cn() as cn:

        cn.execute("UPDATE courses SET instructor_id=NULL WHERE instructor_id=?",(in_,))
        cn.execute("DELETE FROM instructors WHERE instructor_id=?", (in_,))


def cr_cs(cs, cs_nm, in_: Optional[str]):
    """Create a course.

    :param cs: Course ID (primary key).
    :type cs: str
    :param cs_nm: Course name.
    :type cs_nm: str
    :param in_: Optional instructor ID to assign.
    :type in_: Optional[str]
    """
    with _cn() as cn:
        cn.execute(
            "INSERT INTO courses(course_id, course_name, instructor_id) VALUES (?,?,?)",
            (cs, cs_nm, in_),
        )


def ls_cs():
    """List all courses.

    :return: List of tuples ``(course_id, course_name, instructor_id_or_None)``.
    :rtype: list[tuple[str, str, str | None]]
    """

    with _cn() as cn:

        cur = cn.execute("SELECT course_id, course_name, instructor_id FROM courses")
        return list(cur.fetchall())


def up_cs(cs, cs_nm, in_: Optional[str]):
    """Update a course by ID.

    :param cs: Course ID to update.
    :type cs: str
    :param cs_nm: New course name.
    :type cs_nm: str
    :param in_: New instructor ID or ``None`` to clear.
    :type in_: Optional[str]
    """

    with _cn() as cn:

        cn.execute("UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?",(cs_nm, in_, cs))


def dl_cs(cs):
    """Delete a course by ID.

    :param cs: Course ID to delete.
    :type cs: str
    """

    with _cn() as cn:

        cn.execute("DELETE FROM courses WHERE course_id=?", (cs,))


def en_st(st , cs):
    """Enroll a student into a course.

    No-op if the pair already exists.

    :param st: Student ID.
    :type st: str
    :param cs: Course ID.
    :type cs: str
    """

    with _cn() as cn:
        cn.execute("INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?,?)",(st, cs))


def un_st(st, cs):
    """Unenroll a student from a course.

    :param st: Student ID.
    :type st: str
    :param cs: Course ID.
    :type cs: str
    """

    with _cn() as cn:
        cn.execute("DELETE FROM registrations WHERE student_id=? AND course_id=?",(st, cs))


def ls_st_cs(st):
    """List course IDs a student is registered in.

    :param st: Student ID.
    :type st: str
    :return: List of course IDs.
    :rtype: list[str]
    """
    with _cn() as cn:

        cur = cn.execute("SELECT course_id FROM registrations WHERE student_id=?",(st,))

        return [row[0] for row in cur.fetchall()]


def ls_cs_st(cs):
    """List student IDs enrolled in a course.

    :param cs: Course ID.
    :type cs: str
    :return: List of student IDs.
    :rtype: list[str]
    """

    with _cn() as cn:

        cur = cn.execute("SELECT student_id FROM registrations WHERE course_id=?",(cs,))
        return [row[0] for row in cur.fetchall()]


def bk_db(pth):
    """Backup the database file to a given path.

    Initializes schema first if the database file is missing.

    :param pth: Destination file path to write the copy to.
    :type pth: str
    """

    if not os.path.exists(DBP):
        in_db()

    shutil.copyfile(DBP, pth)