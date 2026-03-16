from src.database.connection import get_connection


def start_session(subject_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
            INSERT INTO lecture_sessions (subject_id, session_date, start_time)
            VALUES (%s, CURDATE(), CURTIME()) \
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
                VALUES (%s, %s, 'Present') \
                """
        cursor.execute(query, (session_id, student_id))
        connection.commit()
        print(f"Attendance marked for student {student_id}")
    except Exception as e:
        print(f"Could not mark attendance for student {student_id}: {e}")
    finally:
        cursor.close()
        connection.close()


def end_session(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Adding the UPDATE query to actually close out the session in the DB
    try:
        query = """
                UPDATE lecture_sessions
                SET end_time = CURTIME()
                WHERE session_id = %s \
                """
        cursor.execute(query, (session_id,))
        connection.commit()
        print(f"Session {session_id} ended successfully in the database.")
    except Exception as e:
        print(f"Error ending session {session_id}: {e}")
    finally:
        cursor.close()
        connection.close()


def get_student_attendance(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Added dictionary=True for easier frontend parsing

    # Replaced 'attendance_records' and 'attendance_sessions' with the actual tables
    query = """
            SELECT ls.session_date as date, al.status
            FROM attendance_logs al
                JOIN lecture_sessions ls \
            ON al.session_id = ls.session_id
            WHERE al.student_id = %s \
            """

    cursor.execute(query, (student_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results