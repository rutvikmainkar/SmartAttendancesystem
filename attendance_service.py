from database import get_connection
from datetime import datetime


def start_session(subject_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO lecture_sessions (subject_id, session_date, start_time)
    VALUES (%s, CURDATE(), CURTIME())
    """
    cursor.execute(query, (subject_id,))
    connection.commit()

    session_id = cursor.lastrowid

    cursor.close()
    connection.close()

    print(f"Session started. Session ID: {session_id}")
    return session_id


def record_attendance(session_id, student_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO attendance_logs (session_id, student_id, status)
        VALUES (%s, %s, 'Present')
        """
        cursor.execute(query, (session_id, student_id))
        connection.commit()
        print(f"Attendance marked for student {student_id}")
    except Exception as e:
        print(f"Could not mark attendance for student {student_id}: {e}")

    cursor.close()
    connection.close()


def end_session(session_id):
    print(f"Session {session_id} ended.")