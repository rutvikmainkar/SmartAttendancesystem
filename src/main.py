from src.services.attendance_service import start_session, record_attendance, end_session
from src.services.report_service import generate_monthly_report
from datetime import datetime


if __name__ == "__main__":

    subject_id = 1

    session_id = start_session(subject_id)

    record_attendance(session_id, 1)
    record_attendance(session_id, 2)
    record_attendance(session_id, 3)

    end_session(session_id)

    today = datetime.today()
    generate_monthly_report(subject_id, today.year, today.month)