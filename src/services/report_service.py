from src.database.connection import get_connection


def add_student(roll_number, full_name, email=None, phone=None, department=None, year=None):
    """
    Add a new student to the database.
    All columns that exist in the schema are accepted as optional
    parameters so the function is future-proof without breaking
    any existing call sites that only pass roll_number + full_name.
    """
    connection = get_connection()
    cursor = connection.cursor()

    query = """
            INSERT INTO students (roll_number, full_name, email, phone, department, year)
            VALUES (%s, %s, %s, %s, %s, %s) \
            """
    cursor.execute(query, (roll_number, full_name, email, phone, department, year))
    connection.commit()

    cursor.close()
    connection.close()

    print(f"Student {full_name} added successfully.")


def get_student_by_roll(roll_number):
    """
    Fetch a student by roll number.
    Returns a dict or None if not found.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
            SELECT student_id, roll_number, full_name, email, phone, department, year
            FROM students
            WHERE roll_number = %s
              AND is_active = 1 \
            """
    cursor.execute(query, (roll_number,))
    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return student


def get_student_by_id(student_id):
    """
    Fetch a student by primary key.
    Useful for face-recognition pipeline where we resolve
    a student_id after matching the face encoding.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
            SELECT student_id, roll_number, full_name, email, phone, department, year, image_path
            FROM students
            WHERE student_id = %s
              AND is_active = 1 \
            """
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return student


def list_students(active_only=True):
    """
    Return all students. Pass active_only=False to include
    deactivated/graduated students.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT student_id, roll_number, full_name, department, year
        FROM students
        {}
        ORDER BY roll_number
    """.format("WHERE is_active = 1" if active_only else "")

    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students


def deactivate_student(student_id):
    """
    Soft-delete a student by setting is_active = 0.
    Their attendance history is preserved.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   UPDATE students
                   SET is_active = 0
                   WHERE student_id = %s
                   """, (student_id,))
    connection.commit()

    cursor.close()
    connection.close()

    print(f"Student {student_id} deactivated.")