"""
╔══════════════════════════════════════════════════════════════╗
║        STUDENT ATTENDANCE MANAGEMENT SYSTEM  v2.0           ║
║        Python + SQLite  |  Colorful Terminal Edition         ║
╚══════════════════════════════════════════════════════════════╝
"""

import sqlite3
import datetime
import os
import csv
import hashlib
import getpass

# ─────────────────────────────────────────────
#  COLORS  (works on Windows 10+, Mac, Linux)
# ─────────────────────────────────────────────

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    # Text colors
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    # Background colors
    BG_BLUE = "\033[44m"
    BG_GREEN= "\033[42m"
    BG_RED  = "\033[41m"

def clr(text, *codes):
    return "".join(codes) + str(text) + C.RESET

# Enable colors on Windows
if os.name == "nt":
    os.system("color")

# ─────────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────────

def init_db():
    conn   = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            roll_no TEXT    NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            date       TEXT    NOT NULL,
            status     TEXT    NOT NULL CHECK(status IN ('Present','Absent')),
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(student_id, subject_id, date)
        )
    """)

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("attendance.db")

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def banner(title, subtitle=""):
    clear()
    width = 62
    print()
    print(clr("╔" + "═" * (width-2) + "╗", C.CYAN, C.BOLD))
    pad = (width - 2 - len(title)) // 2
    print(clr("║" + " " * pad + title + " " * (width-2-pad-len(title)) + "║", C.CYAN, C.BOLD))
    if subtitle:
        pad2 = (width - 2 - len(subtitle)) // 2
        print(clr("║" + " " * pad2 + subtitle + " " * (width-2-pad2-len(subtitle)) + "║", C.CYAN))
    print(clr("╚" + "═" * (width-2) + "╝", C.CYAN, C.BOLD))
    print()

def divider(char="─", width=62, color=C.GRAY):
    print(clr(char * width, color))

def success(msg): print(clr(f"  ✅  {msg}", C.GREEN, C.BOLD))
def error(msg):   print(clr(f"  ❌  {msg}", C.RED,   C.BOLD))
def warn(msg):    print(clr(f"  ⚠️   {msg}", C.YELLOW,C.BOLD))
def info(msg):    print(clr(f"  ℹ️   {msg}", C.CYAN))
def pause():      input(clr("\n  Press Enter to continue...", C.GRAY))

def menu_item(num, icon, label):
    print(f"  {clr(num, C.YELLOW, C.BOLD)}  {icon}  {clr(label, C.WHITE)}")

# ══════════════════════════════════════════════
#  LOGIN / REGISTER SYSTEM
# ══════════════════════════════════════════════

def login():
    while True:
        banner("STUDENT ATTENDANCE SYSTEM  v2.0", "🔐  Login to Continue")
        print(f"  {clr('1', C.YELLOW, C.BOLD)}  🔑  Login")
        print(f"  {clr('2', C.YELLOW, C.BOLD)}  📝  Register New Account")
        print(f"  {clr('0', C.YELLOW, C.BOLD)}  🚪  Exit")
        print()
        choice = input(clr("  Your choice: ", C.CYAN)).strip()

        if choice == "1":
            if do_login():
                return True
        elif choice == "2":
            do_register()
        elif choice == "0":
            clear()
            print(clr("\n  👋  Goodbye!\n", C.CYAN, C.BOLD))
            return False
        else:
            warn("Invalid choice.")
            pause()

def do_login():
    print()
    username = input(clr("  Username : ", C.CYAN)).strip()
    password = getpass.getpass(clr("  Password : ", C.CYAN))

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        success(f"Welcome back, {clr(username, C.CYAN, C.BOLD)}!")
        pause()
        return True
    else:
        error("Wrong username or password. Try again.")
        pause()
        return False

def do_register():
    print()
    username = input(clr("  Choose username : ", C.CYAN)).strip()
    if not username:
        error("Username cannot be empty.")
        pause()
        return

    password = getpass.getpass(clr("  Choose password : ", C.CYAN))
    confirm  = getpass.getpass(clr("  Confirm password: ", C.CYAN))

    if password != confirm:
        error("Passwords do not match!")
        pause()
        return

    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        success(f"Account '{username}' created! You can now log in.")
    except sqlite3.IntegrityError:
        error(f"Username '{username}' already taken. Choose another.")
    finally:
        conn.close()
    pause()

# ══════════════════════════════════════════════
#  SUBJECT MANAGEMENT
# ══════════════════════════════════════════════

def manage_subjects():
    while True:
        banner("SUBJECT MANAGEMENT", "📚  Add or View Subjects")
        menu_item("1", "➕", "Add Subject")
        menu_item("2", "📋", "View All Subjects")
        menu_item("3", "🗑️ ", "Remove Subject")
        menu_item("0", "🔙", "Back to Main Menu")
        print()
        choice = input(clr("  Your choice: ", C.CYAN)).strip()

        if choice == "1":
            name = input(clr("  Subject name: ", C.CYAN)).strip()
            if not name:
                error("Subject name cannot be empty.")
                pause()
                continue
            conn   = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
                conn.commit()
                success(f"Subject '{name}' added!")
            except sqlite3.IntegrityError:
                warn(f"Subject '{name}' already exists.")
            finally:
                conn.close()
            pause()

        elif choice == "2":
            _print_subjects()
            pause()

        elif choice == "3":
            _print_subjects()
            sid = input(clr("\n  Enter subject ID to remove: ", C.CYAN)).strip()
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM subjects WHERE id=?", (sid,))
            row = cursor.fetchone()
            if row:
                confirm = input(clr(f"  Remove '{row[0]}' and ALL its attendance? (yes/no): ", C.YELLOW)).strip().lower()
                if confirm == "yes":
                    cursor.execute("DELETE FROM attendance WHERE subject_id=?", (sid,))
                    cursor.execute("DELETE FROM subjects WHERE id=?", (sid,))
                    conn.commit()
                    success(f"Subject '{row[0]}' removed.")
                else:
                    info("Cancelled.")
            else:
                error("Subject not found.")
            conn.close()
            pause()

        elif choice == "0":
            break

def _print_subjects():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    print()
    if rows:
        print(clr(f"  {'ID':<6} {'Subject Name'}", C.CYAN, C.BOLD))
        divider()
        for sid, name in rows:
            print(f"  {clr(str(sid)+'.',C.YELLOW):<15} {clr(name, C.WHITE)}")
    else:
        warn("No subjects found. Add subjects first.")
    return rows

def get_subjects():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ══════════════════════════════════════════════
#  STUDENT MANAGEMENT
# ══════════════════════════════════════════════

def add_student():
    banner("ADD NEW STUDENT", "👤  Register a Student")
    name    = input(clr("  Student name   : ", C.CYAN)).strip()
    roll_no = input(clr("  Roll number    : ", C.CYAN)).strip()

    if not name or not roll_no:
        error("Name and roll number cannot be empty!")
        pause(); return

    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (name, roll_no) VALUES (?, ?)", (name, roll_no))
        conn.commit()
        success(f"Student '{name}' (Roll: {roll_no}) added successfully!")
    except sqlite3.IntegrityError:
        error(f"Roll number '{roll_no}' already exists!")
    finally:
        conn.close()
    pause()

def remove_student():
    banner("REMOVE STUDENT", "🗑️   Delete a Student Record")
    _print_students()
    roll = input(clr("\n  Enter roll number to remove: ", C.CYAN)).strip()

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students WHERE roll_no=?", (roll,))
    row = cursor.fetchone()

    if not row:
        error(f"No student with roll '{roll}' found.")
        conn.close(); pause(); return

    sid, sname = row
    confirm = input(clr(f"  Remove '{sname}' and all attendance records? (yes/no): ", C.YELLOW)).strip().lower()
    if confirm == "yes":
        cursor.execute("DELETE FROM attendance WHERE student_id=?", (sid,))
        cursor.execute("DELETE FROM students WHERE id=?", (sid,))
        conn.commit()
        success(f"'{sname}' removed successfully.")
    else:
        info("Cancelled. No changes made.")
    conn.close()
    pause()

def edit_student():
    banner("EDIT STUDENT", "✏️   Modify Student Details")
    _print_students()
    roll = input(clr("\n  Enter roll number to edit: ", C.CYAN)).strip()

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no FROM students WHERE roll_no=?", (roll,))
    row = cursor.fetchone()

    if not row:
        error(f"No student with roll '{roll}' found.")
        conn.close(); pause(); return

    sid, old_name, old_roll = row
    print(clr(f"\n  Current Name   : {old_name}", C.WHITE))
    print(clr(f"  Current Roll   : {old_roll}", C.WHITE))
    print(clr("  (Press Enter to keep existing value)", C.GRAY))
    print()

    new_name = input(clr("  New name   : ", C.CYAN)).strip() or old_name
    new_roll = input(clr("  New roll   : ", C.CYAN)).strip() or old_roll

    try:
        cursor.execute(
            "UPDATE students SET name=?, roll_no=? WHERE id=?",
            (new_name, new_roll, sid)
        )
        conn.commit()
        success(f"Student updated: '{new_name}' / Roll: {new_roll}")
    except sqlite3.IntegrityError:
        error(f"Roll number '{new_roll}' already taken by another student.")
    finally:
        conn.close()
    pause()

def search_student():
    banner("SEARCH STUDENT", "🔍  Find by Name or Roll Number")
    keyword = input(clr("  Enter name or roll number to search: ", C.CYAN)).strip().lower()

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT roll_no, name FROM students
        WHERE LOWER(name) LIKE ? OR LOWER(roll_no) LIKE ?
        ORDER BY roll_no
    """, (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()

    print()
    if rows:
        print(clr(f"  {'Roll No':<14} {'Name'}", C.CYAN, C.BOLD))
        divider()
        for roll, name in rows:
            print(f"  {clr(roll, C.YELLOW):<23} {clr(name, C.WHITE)}")
        print()
        info(f"{len(rows)} result(s) found.")
    else:
        warn(f"No students found matching '{keyword}'.")
    pause()

def _print_students():
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT roll_no, name FROM students ORDER BY roll_no")
    rows = cursor.fetchall()
    conn.close()
    print()
    if rows:
        print(clr(f"  {'Roll No':<14} {'Name'}", C.CYAN, C.BOLD))
        divider()
        for roll, name in rows:
            print(f"  {clr(roll, C.YELLOW):<23} {clr(name, C.WHITE)}")
    else:
        warn("No students registered yet.")
    return rows

# ══════════════════════════════════════════════
#  MARK ATTENDANCE
# ══════════════════════════════════════════════

def mark_attendance():
    banner("MARK ATTENDANCE", "📅  Record Today's Attendance")

    subjects = get_subjects()
    if not subjects:
        warn("No subjects found! Please add subjects first.")
        pause(); return

    print(clr("  Select Subject:\n", C.CYAN, C.BOLD))
    for sid, sname in subjects:
        print(f"  {clr(str(sid), C.YELLOW, C.BOLD)}  📖  {clr(sname, C.WHITE)}")
    print()

    try:
        sub_id = int(input(clr("  Subject ID: ", C.CYAN)).strip())
        subject = next((s for s in subjects if s[0] == sub_id), None)
        if not subject:
            raise ValueError
    except ValueError:
        error("Invalid subject ID."); pause(); return

    today = datetime.date.today().strftime("%Y-%m-%d")
    date_input = input(clr(f"  Date [Enter for today {today}]: ", C.CYAN)).strip()
    date = date_input if date_input else today

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        error("Invalid date format. Use YYYY-MM-DD."); pause(); return

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no FROM students ORDER BY roll_no")
    students = cursor.fetchall()

    if not students:
        warn("No students found. Add students first.")
        conn.close(); pause(); return

    print()
    print(clr(f"  📖 Subject : {subject[1]}", C.MAGENTA, C.BOLD))
    print(clr(f"  📅 Date    : {date}", C.MAGENTA))
    print(clr("  Type  P = Present  |  A = Absent", C.GRAY))
    print()
    print(clr(f"  {'Roll No':<14} {'Name':<26} Status", C.CYAN, C.BOLD))
    divider()

    records = []
    for sid, name, roll in students:
        cursor.execute(
            "SELECT status FROM attendance WHERE student_id=? AND subject_id=? AND date=?",
            (sid, sub_id, date)
        )
        existing = cursor.fetchone()
        if existing:
            icon = clr("✅ Already: " + existing[0], C.GRAY)
            print(f"  {clr(roll, C.YELLOW):<23} {name:<26} {icon}")
            continue

        while True:
            raw = input(f"  {clr(roll, C.YELLOW):<23} {name:<26} ").strip().upper()
            if raw in ("P", "A"):
                status = "Present" if raw == "P" else "Absent"
                records.append((sid, sub_id, date, status))
                break
            print(clr("  ⚠  Enter P or A", C.RED))

    if records:
        cursor.executemany(
            "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (?,?,?,?)",
            records
        )
        conn.commit()
        success(f"Attendance saved for {len(records)} student(s).")
    else:
        info("All students already marked for this subject/date.")

    conn.close()
    pause()

# ══════════════════════════════════════════════
#  VIEW ATTENDANCE
# ══════════════════════════════════════════════

def view_attendance():
    banner("VIEW ATTENDANCE RECORDS", "📋  Browse Attendance Data")
    print(clr("  Filter by:\n", C.CYAN))
    menu_item("1", "📅", "By Date")
    menu_item("2", "👤", "By Student")
    menu_item("3", "📖", "By Subject")
    print()
    choice = input(clr("  Your choice: ", C.CYAN)).strip()

    conn   = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        today = datetime.date.today().strftime("%Y-%m-%d")
        date  = input(clr(f"  Enter date [default {today}]: ", C.CYAN)).strip() or today
        subjects = get_subjects()
        print(clr("\n  Select subject (or press Enter for ALL):", C.CYAN))
        for sid, sname in subjects:
            print(f"  {clr(str(sid), C.YELLOW)}  {sname}")
        sub_input = input(clr("\n  Subject ID (or Enter for all): ", C.CYAN)).strip()

        if sub_input:
            cursor.execute("""
                SELECT s.roll_no, s.name, sub.name, a.status
                FROM attendance a
                JOIN students s   ON s.id   = a.student_id
                JOIN subjects sub ON sub.id = a.subject_id
                WHERE a.date=? AND a.subject_id=?
                ORDER BY s.roll_no
            """, (date, sub_input))
        else:
            cursor.execute("""
                SELECT s.roll_no, s.name, sub.name, a.status
                FROM attendance a
                JOIN students s   ON s.id   = a.student_id
                JOIN subjects sub ON sub.id = a.subject_id
                WHERE a.date=?
                ORDER BY sub.name, s.roll_no
            """, (date,))

        rows = cursor.fetchall()
        print()
        print(clr(f"  Attendance on {date}:\n", C.MAGENTA, C.BOLD))
        if rows:
            print(clr(f"  {'Roll':<12} {'Name':<24} {'Subject':<18} Status", C.CYAN, C.BOLD))
            divider()
            for roll, name, sub, status in rows:
                icon = clr("✅ Present", C.GREEN) if status=="Present" else clr("❌ Absent", C.RED)
                print(f"  {clr(roll,C.YELLOW):<21} {name:<24} {clr(sub,C.MAGENTA):<27} {icon}")
        else:
            warn("No records for this date/subject.")

    elif choice == "2":
        _print_students()
        roll = input(clr("\n  Enter roll number: ", C.CYAN)).strip()
        cursor.execute("""
            SELECT a.date, sub.name, a.status
            FROM attendance a
            JOIN students s   ON s.id   = a.student_id
            JOIN subjects sub ON sub.id = a.subject_id
            WHERE s.roll_no=?
            ORDER BY a.date DESC, sub.name
        """, (roll,))
        rows = cursor.fetchall()
        cursor.execute("SELECT name FROM students WHERE roll_no=?", (roll,))
        stu = cursor.fetchone()
        print()
        if stu and rows:
            print(clr(f"  Records for {stu[0]} (Roll: {roll}):\n", C.MAGENTA, C.BOLD))
            print(clr(f"  {'Date':<14} {'Subject':<20} Status", C.CYAN, C.BOLD))
            divider()
            for date, sub, status in rows:
                icon = clr("✅ Present", C.GREEN) if status=="Present" else clr("❌ Absent", C.RED)
                print(f"  {clr(date,C.YELLOW):<23} {clr(sub,C.MAGENTA):<29} {icon}")
        else:
            warn("No records found.")

    elif choice == "3":
        subjects = get_subjects()
        _print_subjects()
        sub_id = input(clr("\n  Enter subject ID: ", C.CYAN)).strip()
        cursor.execute("""
            SELECT s.roll_no, s.name, a.date, a.status
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            WHERE a.subject_id=?
            ORDER BY a.date DESC, s.roll_no
        """, (sub_id,))
        rows = cursor.fetchall()
        print()
        if rows:
            print(clr(f"  {'Roll':<12} {'Name':<24} {'Date':<14} Status", C.CYAN, C.BOLD))
            divider()
            for roll, name, date, status in rows:
                icon = clr("✅ Present", C.GREEN) if status=="Present" else clr("❌ Absent", C.RED)
                print(f"  {clr(roll,C.YELLOW):<21} {name:<24} {clr(date,C.GRAY):<23} {icon}")
        else:
            warn("No records for this subject.")
    else:
        warn("Invalid option.")

    conn.close()
    pause()

# ══════════════════════════════════════════════
#  REPORT + LEAVE CALCULATOR
# ══════════════════════════════════════════════

def generate_report():
    banner("ATTENDANCE REPORT", "📊  Stats + Leave Calculator")

    subjects = get_subjects()
    print(clr("  Filter by subject (or Enter for ALL subjects):\n", C.CYAN))
    for sid, sname in subjects:
        print(f"  {clr(str(sid), C.YELLOW)}  {sname}")
    sub_input = input(clr("\n  Subject ID (or Enter for all): ", C.CYAN)).strip()

    try:
        req_pct = float(input(clr("  Required attendance % [default 75]: ", C.CYAN)).strip() or 75)
    except ValueError:
        req_pct = 75.0

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no FROM students ORDER BY roll_no")
    students = cursor.fetchall()

    if not students:
        warn("No students found.")
        conn.close(); pause(); return

    print()
    print(clr(f"  📊  REPORT  (Minimum required: {req_pct}%)\n", C.CYAN, C.BOLD))
    print(clr(f"  {'Roll':<10} {'Name':<22} {'Sub':<16} {'P':<5} {'Tot':<6} {'%':<8} {'Can Miss':<12} Status", C.CYAN, C.BOLD))
    divider("─", 90)

    safe_count = 0
    low_count  = 0

    for sid, name, roll in students:
        if sub_input:
            sub_filter = "AND a.subject_id=?"
            params_total   = (sid, sub_input)
            params_present = (sid, sub_input)
            cursor.execute(f"SELECT COUNT(*) FROM attendance a WHERE a.student_id=? {sub_filter}", params_total)
            total = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM attendance a WHERE a.student_id=? AND a.status='Present' {sub_filter}", params_present)
            present = cursor.fetchone()[0]
            sub_label = next((s[1] for s in subjects if str(s[0])==sub_input), "?")
        else:
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (sid,))
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'", (sid,))
            present = cursor.fetchone()[0]
            sub_label = "All"

        if total == 0:
            print(f"  {clr(roll,C.YELLOW):<19} {name:<22} {clr(sub_label,C.MAGENTA):<25} {clr('No records',C.GRAY)}")
            continue

        pct = (present / total) * 100

        if pct >= req_pct:
            can_miss = int((present * 100 - req_pct * total) / req_pct)
            leave_info = clr(f"{can_miss} days", C.GREEN)
            status_txt = clr("✅ SAFE", C.GREEN, C.BOLD)
            safe_count += 1
        else:
            if req_pct < 100:
                needs = int((req_pct * total - 100 * present) / (100 - req_pct)) + 1
            else:
                needs = "∞"
            leave_info = clr(f"Need +{needs}", C.RED)
            status_txt = clr("⚠  LOW ", C.RED, C.BOLD)
            low_count += 1

        pct_color = C.GREEN if pct >= req_pct else C.RED
        print(f"  {clr(roll,C.YELLOW):<19} {name:<22} {clr(sub_label,C.MAGENTA):<25} {str(present):<5} {str(total):<6} {clr(f'{pct:.1f}%',pct_color):<17} {leave_info:<21} {status_txt}")

    divider("─", 90)
    print(f"\n  {clr('Summary:', C.CYAN, C.BOLD)}  "
          f"{clr(f'{safe_count} students SAFE ✅', C.GREEN)}  |  "
          f"{clr(f'{low_count} students LOW ⚠', C.RED)}")
    conn.close()
    pause()

# ══════════════════════════════════════════════
#  EXPORT TO CSV
# ══════════════════════════════════════════════

def export_csv():
    banner("EXPORT TO CSV", "💾  Save Report as Spreadsheet")

    conn   = get_connection()
    cursor = conn.cursor()

    print(clr("  Choose what to export:\n", C.CYAN))
    menu_item("1", "📊", "Full Attendance Report (with %)")
    menu_item("2", "📋", "All Raw Attendance Records")
    print()
    choice = input(clr("  Your choice: ", C.CYAN)).strip()

    filename = f"attendance_export_{datetime.date.today()}.csv"

    if choice == "1":
        cursor.execute("SELECT id, name, roll_no FROM students ORDER BY roll_no")
        students = cursor.fetchall()
        subjects = get_subjects()

        try:
            req_pct = float(input(clr("  Required attendance % [default 75]: ", C.CYAN)).strip() or 75)
        except ValueError:
            req_pct = 75.0

        rows = []
        for sid, name, roll in students:
            for subid, subname in subjects:
                cursor.execute(
                    "SELECT COUNT(*) FROM attendance WHERE student_id=? AND subject_id=?",
                    (sid, subid)
                )
                total = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM attendance WHERE student_id=? AND subject_id=? AND status='Present'",
                    (sid, subid)
                )
                present = cursor.fetchone()[0]
                if total == 0:
                    pct, can_miss, status = "N/A", "N/A", "No Records"
                else:
                    pct      = round((present / total) * 100, 2)
                    can_miss = max(int((present*100 - req_pct*total)/req_pct), 0) if pct >= req_pct else 0
                    needs    = (int((req_pct*total - 100*present)/(100-req_pct))+1) if pct < req_pct and req_pct < 100 else 0
                    status   = "SAFE" if pct >= req_pct else f"LOW - Need +{needs} classes"
                rows.append([roll, name, subname, present, total, f"{pct}%", can_miss, status])

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Subject", "Present", "Total Classes", "Attendance %", "Can Miss", "Status"])
            writer.writerows(rows)

    elif choice == "2":
        cursor.execute("""
            SELECT s.roll_no, s.name, sub.name, a.date, a.status
            FROM attendance a
            JOIN students s   ON s.id   = a.student_id
            JOIN subjects sub ON sub.id = a.subject_id
            ORDER BY a.date DESC, s.roll_no
        """)
        rows = cursor.fetchall()
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Subject", "Date", "Status"])
            writer.writerows(rows)
    else:
        warn("Invalid choice.")
        conn.close(); pause(); return

    conn.close()
    success(f"Exported successfully as  '{filename}'")
    info(f"You can open this file in Excel or Google Sheets!")
    pause()

# ══════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════

def main_menu():
    while True:
        banner("STUDENT ATTENDANCE SYSTEM  v2.0", "🎓  Main Menu")
        menu_item("1", "👤", "Add Student")
        menu_item("2", "🗑️ ", "Remove Student")
        menu_item("3", "✏️ ", "Edit Student")
        menu_item("4", "🔍", "Search Student")
        menu_item("5", "📋", "View All Students")
        print(clr("  " + "─" * 40, C.GRAY))
        menu_item("6", "📖", "Manage Subjects")
        print(clr("  " + "─" * 40, C.GRAY))
        menu_item("7", "📅", "Mark Attendance")
        menu_item("8", "👁️ ", "View Attendance Records")
        menu_item("9", "📊", "Generate Report + Leave Calculator")
        menu_item("E", "💾", "Export to CSV (Excel)")
        print(clr("  " + "─" * 40, C.GRAY))
        menu_item("0", "🚪", "Logout & Exit")
        print()
        choice = input(clr("  Your choice: ", C.CYAN)).strip().upper()

        actions = {
            "1": add_student,
            "2": remove_student,
            "3": edit_student,
            "4": search_student,
            "5": lambda: (banner("ALL STUDENTS","👥  Registered Students"), _print_students(), pause()),
            "6": manage_subjects,
            "7": mark_attendance,
            "8": view_attendance,
            "9": generate_report,
            "E": export_csv,
        }

        if choice in actions:
            actions[choice]()
        elif choice == "0":
            clear()
            print(clr("\n  👋  Logged out. Goodbye!\n", C.CYAN, C.BOLD))
            break
        else:
            warn("Invalid choice. Please try again.")
            pause()

# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    if login():
        main_menu()
