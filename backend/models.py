"""Domain models for people and courses.

Defines :class:`Person`, :class:`Student`, :class:`Instructor`, and
:class:`Course` with minimal relationships used by the repository and UI
layers. These are simple in-memory structures detached from persistence.
"""


class Person:
    """Base class for people entities.

    :param nm: Person name.
    :type nm: str
    :param ag: Age (non-negative integer).
    :type ag: int
    :param _em: Email address.
    :type _em: str
    """
    def __init__(self, nm, ag, _em):
        self.nm = nm
        self.ag = ag
        self._em = _em

    def introduce(self):
        """Return a short introduction string.

        :return: Introduction sentence.
        :rtype: str
        """
        return f"Hi, I'm {self.nm}, {self.ag} years old."



class Student(Person):
    """Student model extending :class:`Person`.

    :param nm: Student name.
    :type nm: str
    :param ag: Age.
    :type ag: int
    :param _em: Email.
    :type _em: str
    :param st_id: Student identifier.
    :type st_id: str
    :param reg_cs: Initially registered courses, defaults to ``None``.
    :type reg_cs: list[Course] | None
    """

    def __init__(self, nm, ag, _em, st_id, reg_cs = None):

        super().__init__(nm, ag, _em)

        self.st_id = st_id
        self.reg_cs = reg_cs if reg_cs is not None else []

    def register_course(self, crs):
        """Register this student to a course if not already registered.

        :param crs: Course to register in.
        :type crs: Course
        """

        if crs not in self.reg_cs:
            self.reg_cs.append(crs)


class Instructor(Person):
    """Instructor model extending :class:`Person`.

    :param nm: Instructor name.
    :type nm: str
    :param ag: Age.
    :type ag: int
    :param _em: Email.
    :type _em: str
    :param in_id: Instructor identifier.
    :type in_id: str
    :param asg_cs: Initially assigned courses, defaults to ``None``.
    :type asg_cs: list[Course] | None
    """
    def __init__(self, nm, ag, _em, in_id, asg_cs = None):

        super().__init__(nm, ag, _em)
        self.in_id = in_id

        self.asg_cs = asg_cs if asg_cs is not None else []

    def assign_course(self, crs):
        """Assign this instructor to teach a course if not already assigned.

        :param crs: Course to assign.
        :type crs: Course
        """
        if crs not in self.asg_cs:
            self.asg_cs.append(crs)

class Course: 
    """Course model linking to instructor and enrolled students.

    :param crs_id: Course identifier.
    :type crs_id: str
    :param crs_nm: Course name.
    :type crs_nm: str
    :param ins: Optional instructor assigned to the course.
    :type ins: Instructor | None
    :param enr_st: Initially enrolled students, defaults to ``None``.
    :type enr_st: list[Student] | None
    """

    def __init__(self, crs_id, crs_nm, ins = None, enr_st = None):

        self.crs_id = crs_id
        self.crs_nm = crs_nm
        self.ins = ins
        self.enr_st = enr_st if enr_st is not None else []

    def add_student(self, stu):
        """Enroll a student in the course if not already present.

        :param stu: Student to enroll.
        :type stu: Student
        """

        if stu not in self.enr_st:
            self.enr_st.append(stu)