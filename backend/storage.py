"""In-memory repository and import/export utilities.

This module defines the :class:`Repository` aggregate that holds students,
instructors, and courses and provides JSON/CSV serialization helpers that are
validated via the :mod:`validation` module. Relations are rebuilt deterministically
from snapshots produced by the serializers.
"""

from .models import Student, Instructor, Course
import csv
import json
from .validation import validate_age, validate_email, validate_non_empty





class Repository:
    """Aggregate container for domain objects.

    Attributes are simple lists: ``students``, ``instructors``, ``courses``.
    """

    def __init__(self):
        self.students = []
        self.instructors = []
        self.courses = []

    def student_by_id(self, sid):
        """Find a student by ID.

        :param sid: Student ID to look up.
        :type sid: str
        :return: Matching :class:`Student` or ``None``.
        :rtype: Student | None
        """

        for s in self.students:

            if s.st_id == sid:

                return s
        return None

    def instructor_by_id(self, iid):
        """Find an instructor by ID.

        :param iid: Instructor ID.
        :type iid: str
        :return: Matching :class:`Instructor` or ``None``.
        :rtype: Instructor | None
        """

        for i in self.instructors:

            if i.in_id == iid:
                return i
            
        return None

    def course_by_id(self, cid):
        """Find a course by ID.

        :param cid: Course ID.
        :type cid: str
        :return: Matching :class:`Course` or ``None``.
        :rtype: Course | None
        """

        for c in self.courses:
            
            if c.crs_id==cid:
                return c
            
        return None
    

    def rebuild_relations(self, snap):
        """Rebuild object relations from a snapshot dict.

        Clears existing relationships on objects in this repository and
        reconstructs instructor assignments and enrollments using identifiers
        present in ``snap``.

        :param snap: Snapshot dictionary (from JSON/CSV loaders).
        :type snap: dict
        """
        id_to_student = {s.st_id: s for s in self.students}
        id_to_course = {c.crs_id: c for c in self.courses}
        id_to_instructor = {i.in_id: i for i in self.instructors}

        for c in self.courses:

            c.enr_st.clear()

        for s in self.students:

            s.reg_cs.clear()

        for i in self.instructors:

            i.asg_cs.clear()

        for c_rec in snap.get("courses", []):

            cid = c_rec["course_id"]
            ins_id = c_rec.get("instructor_id")
            c = id_to_course.get(cid)

            if not c:
                continue

            c.ins = id_to_instructor.get(ins_id) if ins_id else None

            if c.ins:
                c.ins.assign_course(c)

        for c_rec in snap.get("courses", []):

            cid = c_rec["course_id"]
            c = id_to_course.get(cid)

            if not c:
                continue

            for sid in c_rec.get("enrolled_student_ids", []):

                s = id_to_student.get(sid)

                if s:
                    c.add_student(s)
                    s.register_course(c)


def _st_to_dc(s):
    """Convert a :class:`Student` to a serializable dict."""

    return {
        "student_id": s.st_id,
        "name": s.nm,
        "age": s.ag,
        "email": s._em,
        "registered_course_ids": [c.crs_id for c in s.reg_cs],
    }


def _in_to_dc(i):
    """Convert an :class:`Instructor` to a serializable dict."""

    return {
        "instructor_id": i.in_id,
        "name": i.nm,
        "age": i.ag,
        "email": i._em,
        "assigned_course_ids": [c.crs_id for c in i.asg_cs],
    }


def _cs_to_dc(c):
    """Convert a :class:`Course` to a serializable dict."""
    return {
        "course_id": c.crs_id,
        "course_name": c.crs_nm,
        "instructor_id": c.ins.in_id if c.ins else None,
        "enrolled_student_ids": [s.st_id for s in c.enr_st],
    }


def save_to_json(rp, pth):
    """Write repository content to a JSON file.

    :param rp: Source repository.
    :type rp: Repository
    :param pth: Destination file path.
    :type pth: str
    :raises IOError: If the file cannot be written.
    """

    data = {
        "students": [_st_to_dc(s) for s in rp.students],
        "instructors": [_in_to_dc(i) for i in rp.instructors],
        "courses": [_cs_to_dc(c) for c in rp.courses],
    }

    with open(pth, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_from_json(pth):
    """Load repository content from a JSON file.

    Validates records using :mod:`validation` and reconstructs relationships.

    :param pth: JSON path to read from.
    :type pth: str
    :return: Tuple ``(repository, snapshot_dict)``.
    :rtype: tuple[Repository, dict]
    :raises Exception: If parsing or validation fails.
    """

    with open(pth, "r", encoding="utf-8") as f:
        data = json.load(f)

    rp = Repository()
    
    for s in data.get("students", []):

        validate_non_empty(s.get("student_id", ""), "student_id")
        validate_non_empty(s.get("name", ""), "name")
        validate_age(int(s.get("age", 0)))
        validate_email(s.get("email", ""))

        rp.students.append(Student( s["name"], int(s["age"]), s["email"], s["student_id"]))

    for i in data.get("instructors", []):

        validate_non_empty(i.get("instructor_id", ""), "instructor_id")
        validate_non_empty(i.get("name", ""), "name")
        validate_age(int(i.get("age", 0)))
        validate_email(i.get("email", ""))

        rp.instructors.append(Instructor( i["name"], int(i["age"]), i["email"], i["instructor_id"]))

    for c in data.get("courses", []):

        validate_non_empty(c.get("course_id", ""), "course_id")
        validate_non_empty(c.get("course_name", ""), "course_name")

        rp.courses.append(Course(c["course_id"], c["course_name"]))

    rp.rebuild_relations(data)
    return rp, data

def save_to_csv(rp, pth):
    """Export repository content to a CSV file.

    Produces a flat table with a ``type`` column and encoded ID lists.

    :param rp: Source repository.
    :type rp: Repository
    :param pth: Destination CSV path.
    :type pth: str
    :raises IOError: If the file cannot be written.
    """
    
    hdrs = [ "type","student_id","instructor_id","course_id","name","age","email","course_name","registered_course_ids","assigned_course_ids", "enrolled_student_ids"]
    
    with open(pth, "w", newline="", encoding="utf-8") as f:

        w = csv.writer(f)
        w.writerow(hdrs)

        for s in rp.students:
            w.writerow(
                [
                    "student",
                    s.st_id,
                    "",
                    "",
                    s.nm,
                    s.ag,
                    s._em,
                    "",
                    ";".join(c.crs_id for c in s.reg_cs),
                    "",
                    "",
                ]
            )
        for i in rp.instructors:
            w.writerow(
                [
                    "instructor",
                    "",
                    i.in_id,
                    "",
                    i.nm,
                    i.ag,
                    i._em,
                    "",
                    "",
                    ";".join(c.crs_id for c in i.asg_cs),
                    "",
                ]
            )
        for c in rp.courses:
            w.writerow(
                [
                    "course",
                    "",
                    c.ins.in_id if c.ins else "",
                    c.crs_id,
                    "",
                    "",
                    "",
                    c.crs_nm,
                    "",
                    "",
                    ";".join(s.st_id for s in c.enr_st),
                ]
            )


def load_from_csv(pth):
    """Load repository content from a CSV file.

    Validates input and rebuilds relations. Accepts rows with ``type`` equal to
    "student", "instructor", or "course".

    :param pth: CSV file path to read.
    :type pth: str
    :return: Tuple ``(repository, snapshot_dict)``.
    :rtype: tuple[Repository, dict]
    :raises Exception: If parsing or validation fails.
    """
    rp = Repository()
    snap = {"students": [], "instructors": [], "courses": []}

    def _spl(s: str):
        return [x for x in (s or "").split(";") if x]

    with open(pth, "r", encoding="utf-8") as f:

        r = csv.DictReader(f)

        for row in r:
            typ = (row.get("type") or "").strip().lower()
            if typ == "student":

                validate_non_empty(row.get("student_id", ""), "student_id")
                validate_non_empty(row.get("name", ""), "name")
                validate_age(int(row.get("age", "0")))
                validate_email(row.get("email", ""))

                rp.students.append(Student( row["name"], int(row["age"]), row["email"], row["student_id"]))

                snap["students"].append(
                    {
                        "student_id": row["student_id"],
                        "name": row["name"],
                        "age": int(row["age"]),
                        "email": row["email"],
                        "registered_course_ids": _spl(row.get("registered_course_ids", "")),
                    }
                )

            elif typ == "instructor":

                validate_non_empty(row.get("instructor_id", ""), "instructor_id")
                validate_non_empty(row.get("name", ""), "name")
                validate_age(int(row.get("age", "0")))
                validate_email(row.get("email", ""))

                rp.instructors.append(Instructor(row["name"], int(row["age"]),row["email"], row["instructor_id"]))
                snap["instructors"].append(
                    {
                        "instructor_id": row["instructor_id"],
                        "name": row["name"],
                        "age": int(row["age"]),
                        "email": row["email"],
                        "assigned_course_ids": _spl(row.get("assigned_course_ids", "")),
                    })
                
            elif typ == "course":

                validate_non_empty(row.get("course_id", ""), "course_id")
                validate_non_empty(row.get("course_name", ""), "course_name")

                rp.courses.append(Course(row["course_id"],row["course_name"]))  
                snap["courses"].append(
                    {
                        "course_id": row["course_id"],
                        "course_name": row["course_name"],
                        "instructor_id": row.get("instructor_id") or None,
                        "enrolled_student_ids": _spl(row.get("enrolled_student_ids", "")),
                    }
                )
    rp.rebuild_relations(snap)
    return rp, snap
                