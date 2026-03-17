import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime

# --- NEW IMPORTS ADDED HERE ---
from src.database.connection import get_connection
from src.services.attendance_service import start_session, end_session, record_attendance
from src.services.report_service import generate_monthly_report
from src.services.face_recognition_service import run_smart_camera

# ------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

# --- INITIALIZE GLOBALS ---
# Note: Using globals works for a local mini-project, but in a production
# environment, you would want to store this in a user session or the database!
current_session_id = None
current_subject_id = None


# --------------------------

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ---------------- DASHBOARD STATS API ----------------
@app.route("/dashboard-stats")
def dashboard_stats():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # total students
    cursor.execute("SELECT COUNT(*) as count FROM students")
    students = cursor.fetchone()["count"]

    # total subjects
    cursor.execute("SELECT COUNT(*) as count FROM subjects")
    subjects = cursor.fetchone()["count"]

    # sessions today
    cursor.execute("""
                   SELECT COUNT(*) as count
                   FROM lecture_sessions
                   WHERE DATE (start_time) = CURDATE()
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

    query = """
            SELECT subject_id, subject_name
            FROM subjects \
            """

    cursor.execute(query)
    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(subjects)


# ---------------- START SESSION ----------------
@app.route("/start-session", methods=["POST"])
def start_lecture_session():
    global current_session_id
    global current_subject_id

    if current_session_id:
        return jsonify({"message": "Session already running!"})

    data = request.json
    subject_id = data["subject_id"]

    current_subject_id = subject_id
    current_session_id = start_session(subject_id)

    return jsonify({
        "message": "Session started",
        "session_id": current_session_id
    })


# ---------------- END SESSION ----------------
@app.route("/end-session", methods=["POST"])
def end_lecture_session():
    global current_session_id
    global current_subject_id

    if not current_session_id:
        return jsonify({"message": "No active session"})

    end_session(current_session_id)

    # Clear the global state once the session ends
    current_session_id = None
    current_subject_id = None

    return jsonify({"message": "Session ended"})


# ---------------- GET STUDENTS ----------------
@app.route("/students")
def get_students():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
            SELECT student_id, full_name, roll_number
            FROM students \
            """

    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(students)


# ---------------- MARK ATTENDANCE ----------------
@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():
    global current_session_id

    if not current_session_id:
        return jsonify({"message": "Start session first!"})

    student_id = request.json["student_id"]

    record_attendance(current_session_id, student_id)

    return jsonify({"message": "Attendance recorded"})

# ---------------- START AUTO CAMERA ----------------
@app.route("/start-camera", methods=["POST"])
def start_camera():
    global current_session_id

    if not current_session_id:
        return jsonify({"message": "Error: Please start a session on the Dashboard first!"}), 400

    # This will open the local OpenCV window
    success = run_smart_camera(current_session_id)

    if success:
        return jsonify({"message": "Camera closed. Attendance captured successfully!"})
    else:
        return jsonify({"message": "Error running camera. Check dataset folder."}), 500


# ---------------- GENERATE REPORT ----------------
@app.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.json
    subject_id = data["subject_id"]

    today = datetime.today()

    # Generating the report and optionally returning the file name to the frontend
    generate_monthly_report(
        subject_id,
        today.year,
        today.month
    )

    return jsonify({"message": "Report generated! Check the Reports tab."})


# ---------------- REPORTS PAGE ----------------
@app.route("/reports")
def reports_page():
    reports_folder = os.path.join(BASE_DIR, "reports")
    files = os.listdir(reports_folder) if os.path.exists(reports_folder) else []

    return render_template("reports.html", files=files)


# ----------------
# ----------------
@app.route("/download/<filename>")
def download_file(filename):
    reports_folder = os.path.join(BASE_DIR, "reports")

    return send_from_directory(
        reports_folder,
        filename,
        as_attachment=True
    )


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)