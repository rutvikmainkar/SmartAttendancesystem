from src.database.connection import get_connection
from datetime import datetime


def start_session(subject_id, professor_id=None, room_location=None):
    """
    Creates a new lecture session row in lecture_sessions.
    - professor_id and room_location are optional but supported
      by the schema so we pass them through when available.
    - end_time is left NULL here; it gets filled by end_session().
    """
    connection = get_connection()
    cursor = connection.cursor()

    query = """
            INSERT INTO lecture_sessions (subject_id, professor_id, session_date, start_time, room_location)
            VALUES (%s, %s, CURDATE(), CURTIME(), %s) \
            """
    cursor.execute(query, (subject_id, professor_id, room_location))
    connection.commit()

    session_id = cursor.lastrowid

    cursor.close()
    connection.close()

    print(f"Session started. Session ID: {session_id}")
    return session_id


def end_session(session_id):
    """
    Stamps end_time on the session row.
    Also auto-inserts 'Absent' logs for every enrolled student
    who has no attendance log yet for this session — so the
    report query always has a complete set of rows.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # 1. Close the session
        cursor.execute("""
                       UPDATE lecture_sessions
                       SET end_time = CURTIME()
                       WHERE session_id = %s
                       """, (session_id,))

        # 2. Get the subject_id for this session
        cursor.execute("""
                       SELECT subject_id
                       FROM lecture_sessions
                       WHERE session_id = %s
                       """, (session_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Session {session_id} not found.")
            return
        subject_id = row[0]

        # 3. Insert Absent for every enrolled student with no log yet
        cursor.execute("""
                       INSERT INTO attendance_logs (session_id, student_id, status, marked_by)
                       SELECT %s, e.student_id, 'Absent', 'manual'
                       FROM enrollments e
                       WHERE e.subject_id = %s
                         AND e.status = 'active'
                         AND e.student_id NOT IN (SELECT student_id
                                                  FROM attendance_logs
                                                  WHERE session_id = %s)
                       """, (session_id, subject_id, session_id))

        connection.commit()
        print(f"Session {session_id} ended. Absent logs auto-filled.")

    except Exception as e:
        print(f"Error ending session {session_id}: {e}")
    finally:
        cursor.close()
        connection.close()


def record_attendance(session_id, student_id, marked_by='face_recognition'):
    """
    Inserts a Present log for a student.
    - Uses INSERT ... ON DUPLICATE KEY UPDATE so calling this
      twice for the same student in the same session is safe
      (the UNIQUE KEY uq_session_student handles it gracefully).
    - marked_at is set automatically by the DB DEFAULT.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Determine status: Present if on time, Late if after start_time
        cursor.execute("""
                       SELECT start_time
                       FROM lecture_sessions
                       WHERE session_id = %s
                       """, (session_id,))
        session = cursor.fetchone()
        now = datetime.now().time()
        status = 'Late' if session and now > session[0] else 'Present'

        query = """
                INSERT INTO attendance_logs (session_id, student_id, status, marked_by)
                VALUES (%s, %s, %s, %s) ON DUPLICATE KEY \
                UPDATE \
                    status = \
                VALUES (status), marked_by = \
                VALUES (marked_by), marked_at = CURRENT_TIMESTAMP \
                """
        cursor.execute(query, (session_id, student_id, status, marked_by))
        connection.commit()
        print(f"Attendance marked [{status}] for student {student_id}")

    except Exception as e:
        print(f"Could not mark attendance for student {student_id}: {e}")
    finally:
        cursor.close()
        connection.close()


def get_student_attendance(student_id):
    """
    Returns all attendance logs for a student across all sessions,
    including subject name and date for display.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT sub.subject_name, \
                   ls.session_date AS date,
            ls.start_time,
            al.status,
            al.marked_at,
            al.marked_by
            FROM attendance_logs al
                JOIN lecture_sessions ls \
            ON al.session_id = ls.session_id
                JOIN subjects sub ON ls.subject_id = sub.subject_id
            WHERE al.student_id = %s
            ORDER BY ls.session_date DESC, ls.start_time DESC \
            """

    cursor.execute(query, (student_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results
