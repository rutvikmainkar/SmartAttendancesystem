USE smart_attendance;

-- ============================================
-- INSERT PROFESSORS
-- ============================================

INSERT INTO professors (full_name, email, phone, department) VALUES
('Dr. Rajesh Sharma', 'rajesh.sharma@college.edu', '9800000001', 'Computer Engineering'),
('Dr. Priya Mehta',   'priya.mehta@college.edu',   '9800000002', 'Computer Engineering');

-- ============================================
-- INSERT SUBJECTS (no professor_id here anymore)
-- ============================================

INSERT INTO subjects (subject_name, subject_code, department, credits) VALUES
('Database Management Systems', 'CE301', 'Computer Engineering', 4),
('Python Programming',          'CE302', 'Computer Engineering', 3),
('Operating Systems',           'CE303', 'Computer Engineering', 4),
('Computer Networks',           'CE304', 'Computer Engineering', 3),
('Machine Learning',            'CE305', 'Computer Engineering', 4);

-- ============================================
-- INSERT STUDENTS
-- ============================================

INSERT INTO students (full_name, roll_number, email, phone, department, year, image_path) VALUES
('Urvaksh Patel',    '101', 'urvaksh@gmail.com', '9000000001', 'Computer Engineering', 2, NULL),
('Rutvik Mainkar',   '102', 'rutvik@gmail.com',  '9000000002', 'Computer Engineering', 2, NULL),
('Rishit Shah',      '103', 'rishit@gmail.com',  '9000000003', 'Computer Engineering', 2, NULL),
('Soham Desai',      '104', 'soham@gmail.com',   '9000000004', 'Computer Engineering', 2, NULL),
('Manthan Joshi',    '105', 'manthan@gmail.com', '9000000005', 'Computer Engineering', 2, NULL),
('Harshad Kulkarni', '106', 'harshad@gmail.com', '9000000006', 'Computer Engineering', 2, NULL),
('Rehan Khan',       '107', 'rehan@gmail.com',   '9000000007', 'Computer Engineering', 2, NULL),
('Sunny Verma',      '108', 'sunny@gmail.com',   '9000000008', 'Computer Engineering', 2, NULL),
('Swastik Rao',      '109', 'swastik@gmail.com', '9000000009', 'Computer Engineering', 2, NULL),
('Aman Gupta',       '110', 'aman@gmail.com',    '9000000010', 'Computer Engineering', 2, NULL);

-- ============================================
-- ENROLL ALL 10 STUDENTS INTO DBMS (subject_id = 1)
-- ============================================

INSERT INTO enrollments (student_id, subject_id)
SELECT student_id, 1 FROM students;

-- ============================================
-- ENROLL FIRST 5 STUDENTS INTO PYTHON (subject_id = 2)
-- ============================================

INSERT INTO enrollments (student_id, subject_id)
SELECT student_id, 2 FROM students WHERE student_id <= 5;

-- ============================================
-- INSERT LECTURE SESSIONS
-- professor_id now lives here, not on subjects
-- ============================================

INSERT INTO lecture_sessions (subject_id, professor_id, session_date, start_time, end_time, room_location) VALUES
(1, 1, '2025-07-01', '09:00:00', '10:00:00', 'Room A101'),
(1, 1, '2025-07-03', '09:00:00', '10:00:00', 'Room A101'),
(1, 1, '2025-07-05', '09:00:00', '10:00:00', 'Room A101'),
(2, 2, '2025-07-01', '11:00:00', '12:00:00', 'Lab B202'),
(2, 2, '2025-07-03', '11:00:00', '12:00:00', 'Lab B202');

-- ============================================
-- INSERT ATTENDANCE LOGS
-- session 1 (DBMS Jul 1) — mixed statuses
-- ============================================

INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(1, 1,  'Present', 'face_recognition'),
(1, 2,  'Present', 'face_recognition'),
(1, 3,  'Late',    'face_recognition'),
(1, 4,  'Absent',  'manual'),
(1, 5,  'Present', 'face_recognition'),
(1, 6,  'Present', 'face_recognition'),
(1, 7,  'Absent',  'manual'),
(1, 8,  'Late',    'face_recognition'),
(1, 9,  'Present', 'face_recognition'),
(1, 10, 'Present', 'face_recognition');

-- session 2 (DBMS Jul 3)
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(2, 1,  'Present', 'face_recognition'),
(2, 2,  'Absent',  'manual'),
(2, 3,  'Present', 'face_recognition'),
(2, 4,  'Present', 'face_recognition'),
(2, 5,  'Late',    'face_recognition'),
(2, 6,  'Present', 'face_recognition'),
(2, 7,  'Present', 'face_recognition'),
(2, 8,  'Present', 'face_recognition'),
(2, 9,  'Absent',  'manual'),
(2, 10, 'Present', 'face_recognition');

-- session 4 (Python Jul 1) — only students 1–5 enrolled
INSERT INTO attendance_logs (session_id, student_id, status, marked_by) VALUES
(4, 1, 'Present', 'face_recognition'),
(4, 2, 'Present', 'face_recognition'),
(4, 3, 'Absent',  'manual'),
(4, 4, 'Late',    'face_recognition'),
(4, 5, 'Present', 'face_recognition');