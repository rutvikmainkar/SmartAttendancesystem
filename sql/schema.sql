-- ============================================
-- SMART ATTENDANCE SYSTEM DATABASE SCHEMA
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS smart_attendance;
USE smart_attendance;

-- ============================================
-- STUDENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    department VARCHAR(100),
    year INT,
    image_path VARCHAR(255),
    face_encoding LONGBLOB
);

-- ============================================
-- PROFESSORS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS professors (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE
);

-- ============================================
-- SUBJECTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    professor_id INT,
    FOREIGN KEY (professor_id) 
        REFERENCES professors(professor_id)
        ON DELETE SET NULL
);

-- ============================================
-- ENROLLMENTS TABLE (Many-to-Many)
-- ============================================

CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,

    UNIQUE(student_id, subject_id),

    FOREIGN KEY (student_id) 
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    FOREIGN KEY (subject_id) 
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE
);

-- ============================================
-- LECTURE SESSIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS lecture_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,

    FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE
);

-- ============================================
-- ATTENDANCE LOGS TABLE (Final Attendance)
-- ============================================

CREATE TABLE IF NOT EXISTS attendance_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('Present','Late','Absent','EarlyExit') DEFAULT 'Present',

    UNIQUE(session_id, student_id),

    FOREIGN KEY (session_id)
        REFERENCES lecture_sessions(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);

-- ============================================
-- OPTIONAL FUTURE: SLOT TRACKING TABLE
-- (For Three-Slot Logic Upgrade)
-- ============================================

CREATE TABLE IF NOT EXISTS attendance_slot_logs (
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    slot_number INT NOT NULL,
    detected BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (session_id, student_id, slot_number),

    FOREIGN KEY (session_id)
        REFERENCES lecture_sessions(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);
