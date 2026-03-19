-- ============================================================
--  Smart Attendance System — Sample Data
--  Covers all 8 tables in dependency order.
--  Month used: July 2025
-- ============================================================

USE smart_attendance;

-- ============================================================
-- 1. PROFESSORS  (3 professors, one per teaching assignment)
-- ============================================================

INSERT INTO professors (prof_id, full_name, email, phone, department) VALUES
('PROF001', 'Dr. Rajesh Sharma', 'rajesh.sharma@college.edu', '9800000001', 'Computer Engineering'),
('PROF002', 'Dr. Priya Mehta',   'priya.mehta@college.edu',   '9800000002', 'Computer Engineering'),
('PROF003', 'Dr. Ankit Verma',   'ankit.verma@college.edu',   '9800000003', 'Computer Engineering');

-- ============================================================
-- 2. STUDENTS  (10 active students, CE Year 2)
-- ============================================================

INSERT INTO students (full_name, roll_number, email, phone, department, year, image_path, face_encoding, is_active) VALUES
('Urvaksh Patel',    '101', 'urvaksh@gmail.com', '9000000001', 'Computer Engineering', 2, 'faces/101.jpg', NULL, 1),
('Rutvik Mainkar',   '102', 'rutvik@gmail.com',  '9000000002', 'Computer Engineering', 2, 'faces/102.jpg', NULL, 1),
('Rishit Shah',      '103', 'rishit@gmail.com',  '9000000003', 'Computer Engineering', 2, 'faces/103.jpg', NULL, 1),
('Soham Desai',      '104', 'soham@gmail.com',   '9000000004', 'Computer Engineering', 2, 'faces/104.jpg', NULL, 1),
('Manthan Joshi',    '105', 'manthan@gmail.com', '9000000005', 'Computer Engineering', 2, 'faces/105.jpg', NULL, 1),
('Harshad Kulkarni', '106', 'harshad@gmail.com', '9000000006', 'Computer Engineering', 2, 'faces/106.jpg', NULL, 1),
('Rehan Khan',       '107', 'rehan@gmail.com',   '9000000007', 'Computer Engineering', 2, 'faces/107.jpg', NULL, 1),
('Sunny Verma',      '108', 'sunny@gmail.com',   '9000000008', 'Computer Engineering', 2, 'faces/108.jpg', NULL, 1),
('Swastik Rao',      '109', 'swastik@gmail.com', '9000000009', 'Computer Engineering', 2, 'faces/109.jpg', NULL, 1),
('Aman Gupta',       '110', 'aman@gmail.com',    '9000000010', 'Computer Engineering', 2, 'faces/110.jpg', NULL, 1);

-- ============================================================
-- 3. SUBJECTS  (5 subjects; ML has no sessions yet)
-- ============================================================

INSERT INTO subjects (subject_name, subject_code, department, credits) VALUES
('Database Management Systems', 'CE301', 'Computer Engineering', 4),
('Python Programming',          'CE302', 'Computer Engineering', 3),
('Operating Systems',           'CE303', 'Computer Engineering', 4),
('Computer Networks',           'CE304', 'Computer Engineering', 3),
('Machine Learning',            'CE305', 'Computer Engineering', 4);

-- ============================================================
-- 4. ENROLLMENTS
--   DBMS (1)  — all 10 students
--   Python (2) — students 1–5 only
--   OS (3)    — all 10 students
--   CN (4)    — all 10 students
--   ML (5)    — all 10 students (sessions not started yet)
-- ============================================================

-- DBMS — all 10
INSERT INTO enrollments (student_id, subject_id, status) VALUES
(1,1,'active'),(2,1,'active'),(3,1,'active'),(4,1,'active'),(5,1,'active'),
(6,1,'active'),(7,1,'active'),(8,1,'active'),(9,1,'active'),(10,1,'active');

-- Python — first 5
INSERT INTO enrollments (student_id, subject_id, status) VALUES
(1,2,'active'),(2,2,'active'),(3,2,'active'),(4,2,'active'),(5,2,'active');

-- OS — all 10
INSERT INTO enrollments (student_id, subject_id, status) VALUES
(1,3,'active'),(2,3,'active'),(3,3,'active'),(4,3,'active'),(5,3,'active'),
(6,3,'active'),(7,3,'active'),(8,3,'active'),(9,3,'active'),(10,3,'active');

-- CN — all 10
INSERT INTO enrollments (student_id, subject_id, status) VALUES
(1,4,'active'),(2,4,'active'),(3,4,'active'),(4,4,'active'),(5,4,'active'),
(6,4,'active'),(7,4,'active'),(8,4,'active'),(9,4,'active'),(10,4,'active');

-- ML — all 10 (enrolled, no sessions yet)
INSERT INTO enrollments (student_id, subject_id, status) VALUES
(1,5,'active'),(2,5,'active'),(3,5,'active'),(4,5,'active'),(5,5,'active'),
(6,5,'active'),(7,5,'active'),(8,5,'active'),(9,5,'active'),(10,5,'active');

-- ============================================================
-- 5. LECTURE SESSIONS
--   DBMS  → 3 sessions (Dr. Rajesh Sharma,  prof_id=1)
--   Python → 2 sessions (Dr. Priya Mehta,   prof_id=2)
--   OS    → 2 sessions (Dr. Ankit Verma,    prof_id=3)
--   CN    → 2 sessions (Dr. Ankit Verma,    prof_id=3)
--   ML    → 0 sessions (not started)
--
--   session_id assignment (AUTO_INCREMENT order):
--     1 = DBMS  Jul-01   5 = Python Jul-03
--     2 = DBMS  Jul-03   6 = OS     Jul-02
--     3 = DBMS  Jul-05   7 = OS     Jul-04
--     4 = Python Jul-01  8 = CN     Jul-02
--                        9 = CN     Jul-04
-- ============================================================

INSERT INTO lecture_sessions (subject_id, professor_id, session_date, start_time, end_time, room_location, is_cancelled) VALUES
(1, 1, '2025-07-01', '09:00:00', '10:00:00', 'Room A101', 0),  -- session 1
(1, 1, '2025-07-03', '09:00:00', '10:00:00', 'Room A101', 0),  -- session 2
(1, 1, '2025-07-05', '09:00:00', '10:00:00', 'Room A101', 0),  -- session 3
(2, 2, '2025-07-01', '11:00:00', '12:00:00', 'Lab B202',  0),  -- session 4
(2, 2, '2025-07-03', '11:00:00', '12:00:00', 'Lab B202',  0),  -- session 5
(3, 3, '2025-07-02', '10:00:00', '11:00:00', 'Room C301', 0),  -- session 6
(3, 3, '2025-07-04', '10:00:00', '11:00:00', 'Room C301', 0),  -- session 7
(4, 3, '2025-07-02', '13:00:00', '14:00:00', 'Room C302', 0),  -- session 8
(4, 3, '2025-07-04', '13:00:00', '14:00:00', 'Room C302', 0);  -- session 9

-- ============================================================
-- 6. ACTIVE SESSION CONFIG
--   All past sessions are closed (is_active = 0).
--   One row per session that was ever "started" via dashboard.
--   Session 9 is the most recent — closed normally.
--   In production the capture service polls for is_active=1;
--   none are live here since all sessions are in the past.
-- ============================================================

INSERT INTO active_session_config (session_id, activated_at, expires_at, is_active) VALUES
(1, '2025-07-01 08:58:00', '2025-07-01 10:30:00', 0),
(2, '2025-07-03 08:57:00', '2025-07-03 10:30:00', 0),
(3, '2025-07-05 08:59:00', '2025-07-05 10:30:00', 0),
(4, '2025-07-01 10:58:00', '2025-07-01 12:30:00', 0),
(5, '2025-07-03 10:56:00', '2025-07-03 12:30:00', 0),
(6, '2025-07-02 09:58:00', '2025-07-02 11:30:00', 0),
(7, '2025-07-04 09:57:00', '2025-07-04 11:30:00', 0),
(8, '2025-07-02 12:58:00', '2025-07-02 14:30:00', 0),
(9, '2025-07-04 12:59:00', '2025-07-04 14:30:00', 0);

-- ============================================================
-- 7. ATTENDANCE LOGS
--   Status key  → P = Present  L = Late  A = Absent
--   Late counts as attended in the defaulter calculation.
--
--   Attendance summary per student per subject (Jul 2025):
--
--   DBMS  (3 sessions):
--     S1=3/3  S2=2/3  S3=2/3  S4=2/3  S5=3/3
--     S6=2/3  S7=2/3  S8=3/3  S9=2/3  S10=3/3
--
--   Python (2 sessions, students 1–5 only):
--     S1=2/2  S2=1/2  S3=1/2  S4=2/2  S5=2/2
--
--   OS    (2 sessions):
--     S1=2/2  S2=1/2  S3=2/2  S4=2/2  S5=1/2
--     S6=2/2  S7=1/2  S8=1/2  S9=2/2  S10=2/2
--
--   CN    (2 sessions):
--     S1=2/2  S2=2/2  S3=1/2  S4=2/2  S5=2/2
--     S6=1/2  S7=0/2  S8=2/2  S9=2/2  S10=1/2
-- ============================================================

-- ── Session 1  DBMS  Jul-01 ──────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(1,  1, 'Present', 'face_recognition'),
(1,  2, 'Present', 'face_recognition'),
(1,  3, 'Late',    'face_recognition'),
(1,  4, 'Absent',  'manual'),
(1,  5, 'Present', 'face_recognition'),
(1,  6, 'Present', 'face_recognition'),
(1,  7, 'Absent',  'manual'),
(1,  8, 'Late',    'face_recognition'),
(1,  9, 'Present', 'face_recognition'),
(1, 10, 'Present', 'face_recognition');

-- ── Session 2  DBMS  Jul-03 ──────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(2,  1, 'Present', 'face_recognition'),
(2,  2, 'Absent',  'manual'),
(2,  3, 'Present', 'face_recognition'),
(2,  4, 'Present', 'face_recognition'),
(2,  5, 'Late',    'face_recognition'),
(2,  6, 'Present', 'face_recognition'),
(2,  7, 'Present', 'face_recognition'),
(2,  8, 'Present', 'face_recognition'),
(2,  9, 'Absent',  'manual'),
(2, 10, 'Present', 'face_recognition');

-- ── Session 3  DBMS  Jul-05 ──────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(3,  1, 'Present', 'face_recognition'),
(3,  2, 'Present', 'face_recognition'),
(3,  3, 'Absent',  'manual'),
(3,  4, 'Present', 'face_recognition'),
(3,  5, 'Present', 'face_recognition'),
(3,  6, 'Absent',  'manual'),
(3,  7, 'Late',    'face_recognition'),
(3,  8, 'Present', 'face_recognition'),
(3,  9, 'Present', 'face_recognition'),
(3, 10, 'Present', 'face_recognition');

-- ── Session 4  Python  Jul-01 (students 1–5 only) ────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(4, 1, 'Present', 'face_recognition'),
(4, 2, 'Present', 'face_recognition'),
(4, 3, 'Absent',  'manual'),
(4, 4, 'Late',    'face_recognition'),
(4, 5, 'Present', 'face_recognition');

-- ── Session 5  Python  Jul-03 (students 1–5 only) ────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(5, 1, 'Present', 'face_recognition'),
(5, 2, 'Absent',  'manual'),
(5, 3, 'Present', 'face_recognition'),
(5, 4, 'Present', 'face_recognition'),
(5, 5, 'Present', 'face_recognition');

-- ── Session 6  OS  Jul-02 ────────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(6,  1, 'Present', 'face_recognition'),
(6,  2, 'Present', 'face_recognition'),
(6,  3, 'Present', 'face_recognition'),
(6,  4, 'Late',    'face_recognition'),
(6,  5, 'Absent',  'manual'),
(6,  6, 'Present', 'face_recognition'),
(6,  7, 'Present', 'face_recognition'),
(6,  8, 'Absent',  'manual'),
(6,  9, 'Present', 'face_recognition'),
(6, 10, 'Late',    'face_recognition');

-- ── Session 7  OS  Jul-04 ────────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(7,  1, 'Present', 'face_recognition'),
(7,  2, 'Absent',  'manual'),
(7,  3, 'Present', 'face_recognition'),
(7,  4, 'Present', 'face_recognition'),
(7,  5, 'Present', 'face_recognition'),
(7,  6, 'Present', 'face_recognition'),
(7,  7, 'Absent',  'manual'),
(7,  8, 'Present', 'face_recognition'),
(7,  9, 'Present', 'face_recognition'),
(7, 10, 'Present', 'face_recognition');

-- ── Session 8  CN  Jul-02 ────────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(8,  1, 'Present', 'face_recognition'),
(8,  2, 'Late',    'face_recognition'),
(8,  3, 'Present', 'face_recognition'),
(8,  4, 'Present', 'face_recognition'),
(8,  5, 'Present', 'face_recognition'),
(8,  6, 'Absent',  'manual'),
(8,  7, 'Absent',  'manual'),
(8,  8, 'Present', 'face_recognition'),
(8,  9, 'Late',    'face_recognition'),
(8, 10, 'Absent',  'manual');

-- ── Session 9  CN  Jul-04 ────────────────────────────────────
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(9,  1, 'Present', 'face_recognition'),
(9,  2, 'Present', 'face_recognition'),
(9,  3, 'Absent',  'manual'),
(9,  4, 'Present', 'face_recognition'),
(9,  5, 'Present', 'face_recognition'),
(9,  6, 'Present', 'face_recognition'),
(9,  7, 'Absent',  'manual'),
(9,  8, 'Present', 'face_recognition'),
(9,  9, 'Present', 'face_recognition'),
(9, 10, 'Present', 'face_recognition');

-- ============================================================
-- 8. MONTHLY DEFAULTER SNAPSHOTS  (July 2025)
--   Threshold: attendance_pct < 75.00 → is_defaulter = 1
--   Late counts as attended.
--
--   Defaulters by subject:
--     DBMS  → S2, S3, S4, S6, S7, S9  (66.67% — 2/3)
--     Python → S2, S3                  (50.00% — 1/2)
--     OS    → S2, S5, S7, S8           (50.00% — 1/2)
--     CN    → S3, S6, S7, S10          (S7=0%, rest=50%)
-- ============================================================

-- ── DBMS (subject_id=1)  3 sessions held ─────────────────────
INSERT INTO monthly_defaulter_snapshots
    (student_id, subject_id, month, year, sessions_held, sessions_attended, attendance_pct, is_defaulter)
VALUES
(1,  1, 7, 2025, 3, 3, 100.00, 0),
(2,  1, 7, 2025, 3, 2,  66.67, 1),
(3,  1, 7, 2025, 3, 2,  66.67, 1),
(4,  1, 7, 2025, 3, 2,  66.67, 1),
(5,  1, 7, 2025, 3, 3, 100.00, 0),
(6,  1, 7, 2025, 3, 2,  66.67, 1),
(7,  1, 7, 2025, 3, 2,  66.67, 1),
(8,  1, 7, 2025, 3, 3, 100.00, 0),
(9,  1, 7, 2025, 3, 2,  66.67, 1),
(10, 1, 7, 2025, 3, 3, 100.00, 0);

-- ── Python (subject_id=2)  2 sessions held, students 1–5 ─────
INSERT INTO monthly_defaulter_snapshots
    (student_id, subject_id, month, year, sessions_held, sessions_attended, attendance_pct, is_defaulter)
VALUES
(1, 2, 7, 2025, 2, 2, 100.00, 0),
(2, 2, 7, 2025, 2, 1,  50.00, 1),
(3, 2, 7, 2025, 2, 1,  50.00, 1),
(4, 2, 7, 2025, 2, 2, 100.00, 0),
(5, 2, 7, 2025, 2, 2, 100.00, 0);

-- ── OS (subject_id=3)  2 sessions held ───────────────────────
INSERT INTO monthly_defaulter_snapshots
    (student_id, subject_id, month, year, sessions_held, sessions_attended, attendance_pct, is_defaulter)
VALUES
(1,  3, 7, 2025, 2, 2, 100.00, 0),
(2,  3, 7, 2025, 2, 1,  50.00, 1),
(3,  3, 7, 2025, 2, 2, 100.00, 0),
(4,  3, 7, 2025, 2, 2, 100.00, 0),
(5,  3, 7, 2025, 2, 1,  50.00, 1),
(6,  3, 7, 2025, 2, 2, 100.00, 0),
(7,  3, 7, 2025, 2, 1,  50.00, 1),
(8,  3, 7, 2025, 2, 1,  50.00, 1),
(9,  3, 7, 2025, 2, 2, 100.00, 0),
(10, 3, 7, 2025, 2, 2, 100.00, 0);

-- ── CN (subject_id=4)  2 sessions held ───────────────────────
INSERT INTO monthly_defaulter_snapshots
    (student_id, subject_id, month, year, sessions_held, sessions_attended, attendance_pct, is_defaulter)
VALUES
(1,  4, 7, 2025, 2, 2, 100.00, 0),
(2,  4, 7, 2025, 2, 2, 100.00, 0),
(3,  4, 7, 2025, 2, 1,  50.00, 1),
(4,  4, 7, 2025, 2, 2, 100.00, 0),
(5,  4, 7, 2025, 2, 2, 100.00, 0),
(6,  4, 7, 2025, 2, 1,  50.00, 1),
(7,  4, 7, 2025, 2, 0,   0.00, 1),
(8,  4, 7, 2025, 2, 2, 100.00, 0),
(9,  4, 7, 2025, 2, 2, 100.00, 0),
(10, 4, 7, 2025, 2, 1,  50.00, 1);