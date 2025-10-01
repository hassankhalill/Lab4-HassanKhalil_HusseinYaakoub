"""PyQt5 UI layer for the School Management System.

This module defines the :class:`QtSchlApp` widget which provides CRUD operations
for Students, Instructors, and Courses backed by a database layer (``dbm``).
It also supports JSON import/export, CSV export, live search filtering,
entity assignment (instructors to courses) and enrollment (students to courses).
"""

from PyQt5 import QtWidgets
from .validation import validate_age, validate_email, validate_non_empty
from .storage import Repository, save_to_json, save_to_csv, load_from_json
from .models import Student, Instructor, Course
from . import db as dbm


class QtSchlApp(QtWidgets.QWidget):
    """Main application widget for managing school entities.

    Provides GUI forms and tables to create, read, update, delete and relate
    Students, Instructors and Courses. Supports JSON import/export, CSV
    export, live filtering, enrollments and instructor assignment.
    """

    def __init__(self):
        """Initialize the application widget.

        Initializes the database, builds the UI, and loads the initial view.

        :raises Exception: Propagates any database initialization errors.
        """
        super().__init__()
        self.setWindowTitle("School Management System")
        dbm.in_db()
        self.repo = Repository()
        self._bld_ui()
        self.rf_vw()

    def _bld_ui(self):
        """Build and lay out all UI components.

        Creates stacked entity forms, search bar, data tables, and
        action buttons (CRUD, import/export).
        """
        lay = QtWidgets.QVBoxLayout(self)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Entity:"))
        self.ent_cmb = QtWidgets.QComboBox()
        self.ent_cmb.addItems(["Students", "Instructors", "Courses"])
        self.ent_cmb.currentIndexChanged.connect(self.on_ent_chg)
        top.addWidget(self.ent_cmb)
        top.addStretch(1)
        lay.addLayout(top)

        self.frm_stk = QtWidgets.QStackedWidget()
        lay.addWidget(self.frm_stk)

        # --- Student form
        s_tab = QtWidgets.QWidget()
        s_frm = QtWidgets.QFormLayout(s_tab)
        self.s_id = QtWidgets.QLineEdit()
        self.s_nm = QtWidgets.QLineEdit()
        self.s_ag = QtWidgets.QLineEdit()
        self.s_em = QtWidgets.QLineEdit()
        self.s_cs = QtWidgets.QComboBox()
        s_frm.addRow("Student ID", self.s_id)
        s_frm.addRow("Name", self.s_nm)
        s_frm.addRow("Age", self.s_ag)
        s_frm.addRow("Email", self.s_em)
        s_frm.addRow("Register to Course", self.s_cs)
        s_btns = QtWidgets.QHBoxLayout()
        s_add = QtWidgets.QPushButton("Add/Update Student")
        s_reg = QtWidgets.QPushButton("Register to Selected Course")
        s_add.clicked.connect(self.ad_up_st)
        s_reg.clicked.connect(self.reg_st_cs)
        s_btns.addWidget(s_add)
        s_btns.addWidget(s_reg)
        s_frm.addRow(s_btns)
        self.frm_stk.addWidget(s_tab)

        # --- Instructor form
        i_tab = QtWidgets.QWidget()
        i_frm = QtWidgets.QFormLayout(i_tab)
        self.i_id = QtWidgets.QLineEdit()
        self.i_nm = QtWidgets.QLineEdit()
        self.i_ag = QtWidgets.QLineEdit()
        self.i_em = QtWidgets.QLineEdit()
        self.i_cs = QtWidgets.QComboBox()
        i_frm.addRow("Instructor ID", self.i_id)
        i_frm.addRow("Name", self.i_nm)
        i_frm.addRow("Age", self.i_ag)
        i_frm.addRow("Email", self.i_em)
        i_frm.addRow("Assign to Course", self.i_cs)
        i_btns = QtWidgets.QHBoxLayout()
        i_add = QtWidgets.QPushButton("Add/Update Instructor")
        i_asg = QtWidgets.QPushButton("Assign Instructor")
        i_add.clicked.connect(self.ad_up_in)
        i_asg.clicked.connect(self.asg_in_cs)
        i_btns.addWidget(i_add)
        i_btns.addWidget(i_asg)
        i_frm.addRow(i_btns)
        self.frm_stk.addWidget(i_tab)

        # --- Course form
        c_tab = QtWidgets.QWidget()
        c_frm = QtWidgets.QFormLayout(c_tab)
        self.c_id = QtWidgets.QLineEdit()
        self.c_nm = QtWidgets.QLineEdit()
        self.c_ins = QtWidgets.QComboBox()
        c_frm.addRow("Course ID", self.c_id)
        c_frm.addRow("Course Name", self.c_nm)
        c_frm.addRow("Instructor", self.c_ins)
        c_add = QtWidgets.QPushButton("Add/Update Course")
        c_add.clicked.connect(self.ad_up_cs)
        c_frm.addRow(c_add)
        self.frm_stk.addWidget(c_tab)

        # --- Search bar
        sr_box = QtWidgets.QHBoxLayout()
        sr_box.addWidget(QtWidgets.QLabel("Search:"))
        self.srch = QtWidgets.QLineEdit()
        sr_btn = QtWidgets.QPushButton("Apply")
        sr_btn.clicked.connect(self.rf_vw)
        sr_box.addWidget(self.srch)
        sr_box.addWidget(sr_btn)
        lay.addLayout(sr_box)

        # --- Tables
        self.tbl_st = QtWidgets.QTableWidget(0, 5)
        self.tbl_st.setHorizontalHeaderLabels(["student_id", "name", "age", "email", "courses"])
        self.tbl_in = QtWidgets.QTableWidget(0, 5)
        self.tbl_in.setHorizontalHeaderLabels(["instructor_id", "name", "age", "email", "courses"])
        self.tbl_cs = QtWidgets.QTableWidget(0, 4)
        self.tbl_cs.setHorizontalHeaderLabels(["course_id", "course_name", "instructor", "students"])
        self.tbl_stk = QtWidgets.QStackedWidget()
        self.tbl_stk.addWidget(self.tbl_st)
        self.tbl_stk.addWidget(self.tbl_in)
        self.tbl_stk.addWidget(self.tbl_cs)
        lay.addWidget(self.tbl_stk)

        # --- Action buttons
        btns = QtWidgets.QHBoxLayout()
        self.btn_ed = QtWidgets.QPushButton("Edit Selected")
        self.btn_dl = QtWidgets.QPushButton("Delete Selected")
        self.btn_sv = QtWidgets.QPushButton("Save JSON")
        self.btn_ld = QtWidgets.QPushButton("Load JSON")
        self.btn_cv = QtWidgets.QPushButton("Export CSV")
        self.btn_ed.clicked.connect(self.ed_sel)
        self.btn_dl.clicked.connect(self.dl_sel)
        self.btn_sv.clicked.connect(self.sv_js)
        self.btn_ld.clicked.connect(self.ld_js)
        self.btn_cv.clicked.connect(self.ex_cv)
        for b in (self.btn_ed, self.btn_dl, self.btn_sv, self.btn_ld, self.btn_cv):
            btns.addWidget(b)
        lay.addLayout(btns)

    def on_ent_chg(self, idx):
        """Handle entity selection change.

        :param idx: Index of chosen entity (``0=Students``, ``1=Instructors``, ``2=Courses``).
        :type idx: int
        """
        self.frm_stk.setCurrentIndex(idx)
        self.tbl_stk.setCurrentIndex(idx)
        self.rf_vw()

    def ad_up_st(self):
        """Add or update a student from the student form fields.

        Validates entries; creates if new else updates existing.

        :raises ValueError: If validation fails (propagated via validators).
        """
        try:
            sid = validate_non_empty(self.s_id.text(), "student_id")
            nm = validate_non_empty(self.s_nm.text(), "name")
            ag = validate_age(int(self.s_ag.text()))
            em = validate_email(self.s_em.text())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return
        ids = {s[0] for s in dbm.ls_st()}
        if sid in ids:
            dbm.up_st(sid, nm, ag, em)
        else:
            dbm.cr_st(sid, nm, ag, em)
        self.rf_vw()

    def ad_up_in(self):
        """Add or update an instructor from the instructor form.

        :raises ValueError: If validation fails.
        """
        try:
            iid = validate_non_empty(self.i_id.text(), "instructor_id")
            nm = validate_non_empty(self.i_nm.text(), "name")
            ag = validate_age(int(self.i_ag.text()))
            em = validate_email(self.i_em.text())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return
        ids = {i[0] for i in dbm.ls_in()}
        if iid in ids:
            dbm.up_in(iid, nm, ag, em)
        else:
            dbm.cr_in(iid, nm, ag, em)
        self.rf_vw()

    def ad_up_cs(self):
        """Add or update a course from the course form.

        Optionally assigns an instructor.

        :raises ValueError: If required fields are empty/invalid.
        """
        try:
            cid = validate_non_empty(self.c_id.text(), "course_id")
            cnm = validate_non_empty(self.c_nm.text(), "course_name")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return
        ins_id = self.c_ins.currentText().strip() or None
        ids = {c[0] for c in dbm.ls_cs()}
        if cid in ids:
            dbm.up_cs(cid, cnm, ins_id)
        else:
            dbm.cr_cs(cid, cnm, ins_id)
        self.rf_vw()

    def reg_st_cs(self):
        """Enroll the student (by ID field) into the selected course.

        .. note::
           Shows a critical :class:`PyQt5.QtWidgets.QMessageBox` if inputs are missing.

        """
        sid = self.s_id.text().strip()
        cid = self.s_cs.currentText().strip()
        if not sid or not cid:
            QtWidgets.QMessageBox.critical(self, "Error", "Provide Student ID and select a course")
            return
        ids = {s[0] for s in dbm.ls_st()}
        cids = {c[0] for c in dbm.ls_cs()}
        if sid in ids and cid in cids:
            dbm.en_st(sid, cid)
        self.rf_vw()

    def asg_in_cs(self):
        """Assign the instructor (by ID field) to the chosen course.

        .. note::
           Shows a critical :class:`PyQt5.QtWidgets.QMessageBox` if inputs are missing.

        """
        iid = self.i_id.text().strip()
        cid = self.i_cs.currentText().strip()
        if not iid or not cid:
            QtWidgets.QMessageBox.critical(self, "Error", "Provide Instructor ID and select a course")
            return
        ids = {i[0] for i in dbm.ls_in()}
        cids = {c[0] for c in dbm.ls_cs()}
        if iid in ids and cid in cids:
            crs = {c[0]: c for c in dbm.ls_cs()}
            cnm = crs[cid][1]
            dbm.up_cs(cid, cnm, iid)
        self.rf_vw()

    def _act_tbl_row(self):
        """Return active table and currently selected row index.

        :return: ``(table_widget, row_index)`` or ``(None, -1)`` if none selected.
        :rtype: tuple[:class:`PyQt5.QtWidgets.QTableWidget` | None, int]
        """
        tbl = [self.tbl_st, self.tbl_in, self.tbl_cs][self.tbl_stk.currentIndex()]
        r = tbl.currentRow()
        return (tbl, r) if r >= 0 else (None, -1)

    def ed_sel(self):
        """Load the currently selected row into the corresponding form."""
        tbl, r = self._act_tbl_row()
        if not tbl or r < 0:
            return

        def _cell_txt(tb, rw, cl):
            """Internal helper to retrieve cell text safely.

            :param tb: Table widget.
            :type tb: :class:`PyQt5.QtWidgets.QTableWidget`
            :param rw: Row index.
            :type rw: int
            :param cl: Column index.
            :type cl: int
            :return: Cell text or empty string.
            :rtype: str
            """
            it = tb.item(rw, cl)
            return it.text() if it is not None else ""

        vals = [_cell_txt(tbl, r, c) for c in range(tbl.columnCount())]
        if tbl is self.tbl_st:
            self.s_id.setText(vals[0]); self.s_nm.setText(vals[1]); self.s_ag.setText(vals[2]); self.s_em.setText(vals[3])
        elif tbl is self.tbl_in:
            self.i_id.setText(vals[0]); self.i_nm.setText(vals[1]); self.i_ag.setText(vals[2]); self.i_em.setText(vals[3])
        else:
            self.c_id.setText(vals[0]); self.c_nm.setText(vals[1])
            idx = self.c_ins.findText(vals[2])
            self.c_ins.setCurrentIndex(idx if idx >= 0 else 0)

    def dl_sel(self) -> None:
        """Delete the selected entity (student, instructor, or course)."""
        tbl, r = self._act_tbl_row()
        if not tbl or r < 0:
            return
        if tbl is self.tbl_st:
            it = tbl.item(r, 0)
            sid = it.text() if it is not None else ""
            if sid:
                dbm.dl_st(sid)
        elif tbl is self.tbl_in:
            it = tbl.item(r, 0)
            iid = it.text() if it is not None else ""
            if iid:
                dbm.dl_in(iid)
        else:
            it = tbl.item(r, 0)
            cid = it.text() if it is not None else ""
            if cid:
                dbm.dl_cs(cid)
        self.rf_vw()

    def sv_js(self):
        """Persist all current DB content to a user-chosen JSON file.

        Prompts for a path and writes the file.

        :raises IOError: If writing fails (propagated by the save function).
        """
        pth, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save", filter="JSON (*.json)")
        if not pth:
            return
        if not pth.lower().endswith(".json"):
            pth += ".json"
        self._ld_db_rp()
        save_to_json(self.repo, pth)
        QtWidgets.QMessageBox.information(self, "Saved", "Data saved to JSON")

    def ld_js(self):
        """Load and merge entities from a JSON file into the database.

        Existing IDs are updated; new ones are inserted; relationships restored.

        :raises Exception: If parsing or merge fails.
        """
        pth, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load", filter="JSON (*.json)")
        if not pth:
            return
        try:
            rp, _snap = load_from_json(pth)
            self._im_rp_db(rp)
            QtWidgets.QMessageBox.information(self, "Loaded", "JSON imported into database (merge)")
            self.rf_vw()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def ex_cv(self):
        """Export current database snapshot to CSV.

        :raises IOError: If the file cannot be written.
        """
        pth, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export CSV", filter="CSV (*.csv)")
        if not pth:
            return
        if not pth.lower().endswith(".csv"):
            pth += ".csv"
        self._ld_db_rp()
        save_to_csv(self.repo, pth)
        QtWidgets.QMessageBox.information(self, "Exported", "CSV file written")

    def _ld_db_rp(self):
        """Populate :attr:`repo` from the database tables.

        Reconstructs object relationships (instructor assignment, enrollments).
        """
        rp = Repository()

        sts = {sid: (nm, ag, em) for sid, nm, ag, em in dbm.ls_st()}
        for sid, (nm, ag, em) in sts.items():
            rp.students.append(Student(nm, ag, em, sid))

        ins = {iid: (nm, ag, em) for iid, nm, ag, em in dbm.ls_in()}
        for iid, (nm, ag, em) in ins.items():
            rp.instructors.append(Instructor(nm, ag, em, iid))

        css = {cid: (cnm, ins_id) for cid, cnm, ins_id in dbm.ls_cs()}
        for cid, (cnm, ins_id) in css.items():
            rp.courses.append(Course(cid, cnm))

        id_to_s = {s.st_id: s for s in rp.students}
        id_to_i = {i.in_id: i for i in rp.instructors}
        id_to_c = {c.crs_id: c for c in rp.courses}

        for cid, (_, ins_id) in css.items():
            c = id_to_c[cid]
            if ins_id and ins_id in id_to_i:
                c.ins = id_to_i[ins_id]
                c.ins.assign_course(c)
            for sid in dbm.ls_cs_st(cid):
                if sid in id_to_s:
                    s = id_to_s[sid]
                    c.add_student(s)
                    s.register_course(c)

        self.repo = rp

    def _im_rp_db(self, rp):
        """Merge a :class:`Repository` object into the database.

        Existing IDs are updated; missing IDs are created; enrollments
        and instructor assignments are reapplied.

        :param rp: Repository to merge.
        :type rp: Repository
        """
        ex_st = {sid for sid, *_ in dbm.ls_st()}
        ex_in = {iid for iid, *_ in dbm.ls_in()}
        ex_cs = {cid for cid, *_ in dbm.ls_cs()}

        for s in rp.students:
            if s.st_id in ex_st:
                dbm.up_st(s.st_id, s.nm, s.ag, s._em)
            else:
                dbm.cr_st(s.st_id, s.nm, s.ag, s._em)

        for i in rp.instructors:
            if i.in_id in ex_in:
                dbm.up_in(i.in_id, i.nm, i.ag, i._em)
            else:
                dbm.cr_in(i.in_id, i.nm, i.ag, i._em)

        for c in rp.courses:
            ins_id = None
            if hasattr(c, 'ins') and c.ins is not None:
                ins_id = c.ins.in_id
            if c.crs_id in ex_cs:
                dbm.up_cs(c.crs_id, c.crs_nm, ins_id)
            else:
                dbm.cr_cs(c.crs_id, c.crs_nm, ins_id)

        for c in rp.courses:
            for s in getattr(c, 'enr_st', []) or []:
                dbm.en_st(s.st_id, c.crs_id)

    def rf_vw(self):
        """Refresh combo boxes and repopulate tables applying the search filter.

        Case-insensitive substring match across row values.
        """
        cs_ids = [c[0] for c in dbm.ls_cs()]
        in_ids = [i[0] for i in dbm.ls_in()]

        def set_cmb(cmb: QtWidgets.QComboBox, vals, inc_emp=False):
            """Repopulate a combo box.

            :param cmb: Combo box widget.
            :type cmb: :class:`PyQt5.QtWidgets.QComboBox`
            :param vals: Values to insert.
            :type vals: Iterable
            :param inc_emp: Whether to prepend an empty option, defaults to ``False``.
            :type inc_emp: bool, optional
            """
            cmb.clear()
            if inc_emp:
                cmb.addItem("")
            for v in vals:
                cmb.addItem(v)

        set_cmb(self.s_cs, cs_ids)
        set_cmb(self.i_cs, cs_ids)
        set_cmb(self.c_ins, in_ids, inc_emp=True)

        for tbl in (self.tbl_st, self.tbl_in, self.tbl_cs):
            tbl.setRowCount(0)

        term = self.srch.text().strip().lower()

        for sid, nm, ag, em in dbm.ls_st():
            crs_txt = ";".join(dbm.ls_st_cs(sid))
            row = (sid, nm, str(ag), em, crs_txt)
            if self._mt_row(row, term):
                self._ap_row(self.tbl_st, row)

        for iid, nm, ag, em in dbm.ls_in():
            crs_txt = ";".join([c[0] for c in dbm.ls_cs() if c[2] == iid])
            row = (iid, nm, str(ag), em, crs_txt)
            if self._mt_row(row, term):
                self._ap_row(self.tbl_in, row)

        for cid, cnm, ins_id in dbm.ls_cs():
            st_txt = ";".join(dbm.ls_cs_st(cid))
            row = (cid, cnm, ins_id or "", st_txt)
            if self._mt_row(row, term):
                self._ap_row(self.tbl_cs, row)

    @staticmethod
    def _ap_row(tbl, vals):
        """Append a row to a table.

        :param tbl: Target table.
        :type tbl: :class:`PyQt5.QtWidgets.QTableWidget`
        :param vals: Sequence of stringifiable values.
        :type vals: Sequence
        """
        r = tbl.rowCount()
        tbl.insertRow(r)
        for c, v in enumerate(vals):
            tbl.setItem(r, c, QtWidgets.QTableWidgetItem(v))

    @staticmethod
    def _mt_row(row, term):
        """Test if a row matches a search term.

        :param row: Row values.
        :type row: Sequence[str]
        :param term: Lowercased search term.
        :type term: str
        :return: ``True`` if term empty or found in any cell.
        :rtype: bool
        """
        if not term:
            return True
        return any(term in v.lower() for v in row)


def run():
    """Application entry point.

    Creates :class:`PyQt5.QtWidgets.QApplication`, shows main window, and starts the event loop.
    """
    app = QtWidgets.QApplication([])
    w = QtSchlApp()
    w.show()
    app.exec_()


if __name__ == "__main__":
    run()
