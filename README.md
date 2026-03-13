# Smart Attendance System

A Python-based attendance tracking system that records lecture sessions, logs student attendance, and generates monthly attendance reports.

## Features

* Start and end lecture sessions
* Record student attendance
* Store attendance data in a MySQL database
* Generate monthly attendance reports in Excel format
* Organized project structure using a `src` architecture

## Project Structure

```
SmartAttendanceSystem
│
├── src
│   ├── main.py
│   │
│   ├── services
│   │   ├── attendance_service.py
│   │   └── report_service.py
│   │
│   └── database
│       └── database.py
│
├── sql
│   ├── schema.sql
│   └── sample_data.sql
│
├── data
│   └── images
│
├── reports
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Tech Stack

* Python 3.10
* MySQL
* Pandas
* NumPy
* python-dotenv

## Database Setup

1. Create a MySQL database.

2. Run the schema file:

```
sql/schema.sql
```

3. Insert sample data:

```
sql/sample_data.sql
```

## Environment Variables

Create a `.env` file in the project root.

Example:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=attendance_db
```

## Install Dependencies

Create a virtual environment and install requirements.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Project

From the project root:

```
python -m src.main
```

## Output

The system will:

1. Start a lecture session
2. Record attendance
3. End the session
4. Generate a monthly report

Reports are saved in:

```
reports/
```

Example output:

```
reports/Subject_1_2026_3_Report.xlsx
```

## Future Improvements

* Face recognition-based attendance using OpenCV
* Real-time camera integration
* Web dashboard for attendance visualization
* Student registration module
* REST API for attendance management

## Author

Rutvik Mainkar
