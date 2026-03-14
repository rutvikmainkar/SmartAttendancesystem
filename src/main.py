from src.services.attendance_service import start_session, record_attendance, end_session
from src.services.report_service import generate_monthly_report
from src.services.attendance_service import get_student_attendance

from datetime import datetime


if __name__ == "__main__":
    student_id = input("Enter student ID: ")

    records = get_student_attendance(student_id)

    for r in records:
        print(r)


    subject_id = 1

    session_id = start_session(subject_id)

    record_attendance(session_id, 1)
    record_attendance(session_id, 2)
    record_attendance(session_id, 3)

    end_session(session_id)

    today = datetime.today()
    generate_monthly_report(subject_id, today.year, today.month)