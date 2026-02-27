import calendar
from datetime import datetime
import pandas as pd
from database import get_connection

THRESHOLD = 75


def get_month_date_range(year, month):
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day).strftime('%Y-%m-%d')
    return start_date, end_date


def generate_monthly_report(subject_id, year, month):
    start_date, end_date = get_month_date_range(year, month)

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT 
        s.roll_number AS `Roll No`,
        s.full_name AS `Name`,
        COUNT(DISTINCT ls.session_id) AS `Total Lec`,
        COALESCE(SUM(CASE WHEN al.status = 'Present' THEN 1 ELSE 0 END), 0) AS `Present`,
        COUNT(DISTINCT ls.session_id) - 
        COALESCE(SUM(CASE WHEN al.status = 'Present' THEN 1 ELSE 0 END), 0) AS `Absent`,
        ROUND(
            (
                COALESCE(SUM(CASE WHEN al.status = 'Present' THEN 1 ELSE 0 END), 0)
                / NULLIF(COUNT(DISTINCT ls.session_id), 0)
            ) * 100,
        2) AS `Percentage`
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN lecture_sessions ls ON e.subject_id = ls.subject_id
    LEFT JOIN attendance_logs al 
        ON s.student_id = al.student_id 
        AND ls.session_id = al.session_id
    WHERE e.subject_id = %s
    AND ls.session_date BETWEEN %s AND %s
    GROUP BY s.student_id, s.roll_number, s.full_name;
    """

    cursor.execute(query, (subject_id, start_date, end_date))
    rows = cursor.fetchall()

    if not rows:
        print("No attendance data found for this month.")
        return

    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    df["Status"] = df["Percentage"].apply(
        lambda x: "Defaulter" if x < THRESHOLD else "OK"
    )

    df.rename(columns={"Percentage": "% Attendance"}, inplace=True)

    file_name = f"Subject_{subject_id}_{year}_{month}_Report.xlsx"
    df.to_excel(file_name, index=False)

    print(f"Monthly report generated: {file_name}")

    cursor.close()
    connection.close()