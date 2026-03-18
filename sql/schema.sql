-- ============================================================
--  Smart Attendance System — Optimized Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_attendance
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE smart_attendance;

-- ────────────────────────────────────────────────────────────
-- 1. professors
--    Added: phone, department (parity with students table)
-- ────────────────────────────────────────────────────────────
CREATE TABLE professors (
    professor_id   INT            NOT NULL AUTO_INCREMENT,
    full_name      VARCHAR(100)   NOT NULL,
    email          VARCHAR(100)   NOT NULL,
    phone          VARCHAR(15),
    department     VARCHAR(100),
    PRIMARY KEY (professor_id),
    UNIQUE KEY uq_professor_email (email)
);

-- ────────────────────────────────────────────────────────────
-- 2. students
--    Added: is_active (soft delete), created_at (audit trail)
--    Removed nothing — face_encoding + image_path kept for
--    biometric recognition pipeline
-- ────────────────────────────────────────────────────────────
CREATE TABLE students (
    student_id     INT            NOT NULL AUTO_INCREMENT,
    full_name      VARCHAR(100)   NOT NULL,
    roll_number    VARCHAR(50)    NOT NULL,
    email          VARCHAR(100),
    phone          VARCHAR(15),
    department     VARCHAR(100),
    year           INT,
    image_path     VARCHAR(255),
    face_encoding  LONGBLOB,
    is_active      TINYINT(1)     NOT NULL DEFAULT 1,
    created_at     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id),
    UNIQUE KEY uq_roll_number (roll_number)
);

-- ────────────────────────────────────────────────────────────
-- 3. subjects
--    CHANGED: removed professor_id (a subject isn't owned by
--    one professor — that link belongs on lecture_sessions so
--    multiple professors/batches can teach the same subject)
--    Added: subject_code (unique identifier), department,
--    credits (useful for academic reporting)
-- ────────────────────────────────────────────────────────────
CREATE TABLE subjects (
    subject_id     INT            NOT NULL AUTO_INCREMENT,
    subject_name   VARCHAR(100)   NOT NULL,
    subject_code   VARCHAR(20)    NOT NULL,
    department     VARCHAR(100),
    credits        INT            DEFAULT 3,
    PRIMARY KEY (subject_id),
    UNIQUE KEY uq_subject_code (subject_code)
);

-- ────────────────────────────────────────────────────────────
-- 4. enrollments
--    Added: status enum (active / dropped / completed),
--    enrolled_at timestamp for audit / semester tracking
-- ────────────────────────────────────────────────────────────
CREATE TABLE enrollments (
    enrollment_id  INT            NOT NULL AUTO_INCREMENT,
    student_id     INT            NOT NULL,
    subject_id     INT            NOT NULL,
    status         ENUM('active','dropped','completed')
                                  NOT NULL DEFAULT 'active',
    enrolled_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (enrollment_id),
    UNIQUE KEY uq_student_subject (student_id, subject_id),
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id)
        REFERENCES students (student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_subject FOREIGN KEY (subject_id)
        REFERENCES subjects (subject_id) ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 5. lecture_sessions
--    CHANGED: added professor_id here (correct placement —
--    the professor teaching a session can vary per batch)
--    Added: end_time (duration calc, overlap detection),
--    room_location, is_cancelled flag
-- ────────────────────────────────────────────────────────────
CREATE TABLE lecture_sessions (
    session_id     INT            NOT NULL AUTO_INCREMENT,
    subject_id     INT            NOT NULL,
    professor_id   INT,
    session_date   DATE           NOT NULL,
    start_time     TIME           NOT NULL,
    end_time       TIME           NOT NULL,
    room_location  VARCHAR(100),
    is_cancelled   TINYINT(1)     NOT NULL DEFAULT 0,
    PRIMARY KEY (session_id),
    KEY idx_session_date (session_date),
    KEY idx_session_subject (subject_id),
    CONSTRAINT fk_session_subject FOREIGN KEY (subject_id)
        REFERENCES subjects (subject_id) ON DELETE CASCADE,
    CONSTRAINT fk_session_professor FOREIGN KEY (professor_id)
    REFERENCES professors (professor_id) ON DELETE SET NULL
);

-- ────────────────────────────────────────────────────────────
-- 6. attendance_logs
--    Added: marked_at timestamp (exact clock-in time —
--    essential for distinguishing Present vs Late),
--    marked_by enum (face_recognition / manual / imported),
--    remarks for edge-case notes (medical, proxy flagged etc.)
-- ────────────────────────────────────────────────────────────
CREATE TABLE attendance_logs (
    log_id         INT            NOT NULL AUTO_INCREMENT,
    session_id     INT            NOT NULL,
    student_id     INT            NOT NULL,
    status         ENUM('Present','Late','Absent','EarlyExit')
                                  DEFAULT 'Absent',
    marked_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    marked_by      ENUM('face_recognition','manual','imported')
                                  NOT NULL DEFAULT 'face_recognition',
    remarks        TEXT,
    PRIMARY KEY (log_id),
    UNIQUE KEY uq_session_student (session_id, student_id),
    KEY idx_log_student (student_id),
    KEY idx_log_session (session_id),
    CONSTRAINT fk_log_session FOREIGN KEY (session_id)
        REFERENCES lecture_sessions (session_id) ON DELETE CASCADE,
    CONSTRAINT fk_log_student FOREIGN KEY (student_id)
        REFERENCES students (student_id) ON DELETE CASCADE
);

