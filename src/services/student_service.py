from src.database.database import get_connection


def add_student(roll_number, full_name):
    """
    Add a new student to the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO students (roll_number, full_name)
    VALUES (%s, %s)
    """

    cursor.execute(query, (roll_number, full_name))
    connection.commit()

    cursor.close()
    connection.close()

    print(f"Student {full_name} added successfully")

def get_student_by_roll(roll_number):
        """
        Fetch a student using roll number.
        """

        connection = get_connection()
        cursor = connection.cursor()

        query = """
                SELECT student_id, roll_number, full_name
                FROM students
                WHERE roll_number = %s \
                """

        cursor.execute(query, (roll_number,))
        student = cursor.fetchone()

        cursor.close()
        connection.close()

        return student

def list_students():
    """
    Return all students in the system.
    """

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT student_id, roll_number, full_name
    FROM students
    """

    cursor.execute(query)
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return students
