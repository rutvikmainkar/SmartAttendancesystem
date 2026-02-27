from attendance_service import start_session, record_attendance, end_session
from report_service import generate_monthly_report
from datetime import datetime


if __name__ == "__main__":

    subject_id = 1  # Change as needed

    # 1️⃣ Start session
    session_id = start_session(subject_id)

    # 2️⃣ Simulate attendance (replace with camera later)
    record_attendance(session_id, 1)
    record_attendance(session_id, 2)
    record_attendance(session_id, 3)

    # 3️⃣ End session
    end_session(session_id)

    # 4️⃣ Generate monthly report
    today = datetime.today()
    generate_monthly_report(subject_id, today.year, today.month)