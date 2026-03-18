import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime

from src.database.connection import get_connection
from src.services.attendance_service import start_session, end_session, record_attendance
from src.services.report_service import generate_monthly_report
from src.services.face_recognition_service import run_smart_camera

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

# Global session state.
# Fine for a local single-user app; for multi-user move this to Flask session.
current_session_id = None
current_subject_id = None


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ---------------- DASHBOARD STATS ----------------
@app.route("/dashboard-stats")
def dashboard_stats():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS count FROM students WHERE is_active = 1")
    students = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM subjects")
    subjects = cursor.fetchone()["count"]

    # Fixed: column is session_date (DATE), not start_time (TIME)
    cursor.execute("""
                   SELECT COUNT(*) AS count
                   FROM lecture_sessions
                   WHERE session_date = CURDATE()
                     AND is_cancelled = 0
                   """)
    sessions = cursor.fetchone()["count"]

    cursor.close()
    connection.close()

    return jsonify({
        "students": students,
        "subjects": subjects,
        "sessions": sessions
    })


# ---------------- ATTENDANCE PAGE ----------------
@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html")


# ---------------- GET SUBJECTS ----------------
@app.route("/subjects")
def get_subjects():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT subject_id, subject_name, subject_code FROM subjects ORDER BY subject_name")
    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(subjects)


# ---------------- START SESSION ----------------
@app.route("/start-session", methods=["POST"])
def start_lecture_session():
    global current_session_id, current_subject_id

    if current_session_id:
        return jsonify({"message": "A session is already running!"}), 400

    data = request.json or {}
    subject_id = data.get("subject_id")

    if not subject_id:
        return jsonify({"message": "subject_id is required"}), 400

    professor_id = data.get("professor_id")  # optional
    room_location = data.get("room_location")  # optional

    current_subject_id = subject_id
    current_session_id = start_session(subject_id, professor_id, room_location)

    return jsonify({
        "message": "Session started",
        "session_id": current_session_id
    })


# ---------------- END SESSION ----------------
@app.route("/end-session", methods=["POST"])
def end_lecture_session():
    global current_session_id, current_subject_id

    if not current_session_id:
        return jsonify({"message": "No active session to end"}), 400

    end_session(current_session_id)

    current_session_id = None
    current_subject_id = None

    return jsonify({"message": "Session ended successfully"})


# ---------------- GET STUDENTS ----------------
@app.route("/students")
def get_students():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
                   SELECT student_id, full_name, roll_number, department, year
                   FROM students
                   WHERE is_active = 1
                   ORDER BY roll_number
                   """)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(students)


# ---------------- MARK ATTENDANCE ----------------
@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():
    global current_session_id

    if not current_session_id:
        return jsonify({"message": "Start a session first!"}), 400

    data = request.json or {}
    student_id = data.get("student_id")

    if not student_id:
        return jsonify({"message": "student_id is required"}), 400

    record_attendance(current_session_id, student_id, marked_by='manual')

    return jsonify({"message": "Attendance recorded"})


# ---------------- START AUTO CAMERA ----------------
@app.route("/start-camera", methods=["POST"])
def start_camera():
    global current_session_id

    if not current_session_id:
        return jsonify({"message": "Please start a session first!"}), 400

    success = run_smart_camera(current_session_id)

    if success:
        return jsonify({"message": "Camera closed. Attendance captured successfully!"})
    else:
        return jsonify({"message": "Error running camera. Check dataset folder."}), 500


# ---------------- GENERATE REPORT ----------------
@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.json or {}
    subject_id = data.get("subject_id")

    if not subject_id:
        return jsonify({"message": "subject_id is required"}), 400

    today = datetime.today()
    file_path = generate_monthly_report(subject_id, today.year, today.month)

    if not file_path:
        return jsonify({"message": "No data found for this subject this month."}), 404

    return jsonify({"message": "Report generated! Check the Reports tab."})


# ---------------- REPORTS PAGE ----------------
@app.route("/reports")
def reports_page():
    reports_folder = os.path.join(BASE_DIR, "reports")
    files = sorted(os.listdir(reports_folder)) if os.path.exists(reports_folder) else []
    return render_template("reports.html", files=files)


# ---------------- DOWNLOAD REPORT ----------------
@app.route("/download/<filename>")
def download_file(filename):
    reports_folder = os.path.join(BASE_DIR, "reports")
    return send_from_directory(reports_folder, filename, as_attachment=True)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)