USE smart_attendance;

-- ============================================
-- INSERT PROFESSORS
-- ============================================

INSERT INTO professors (full_name, email) VALUES
('Dr. Rajesh Sharma', 'rajesh.sharma@college.edu'),
('Dr. Priya Mehta', 'priya.mehta@college.edu');

-- ============================================
-- INSERT SUBJECTS
-- ============================================

INSERT INTO subjects (subject_name, professor_id) VALUES
('Database Management Systems', 1),
('Python Programming', 2),
('Operating Systems', 1),
('Computer Networks', 2),
('Machine Learning', 1);

-- ============================================
-- INSERT STUDENTS
-- ============================================

INSERT INTO students (full_name, roll_number, email, phone, department, year, image_path) VALUES
('Urvaksh Patel', '101', 'urvaksh@gmail.com', '9000000001', 'Computer Engineering', 2, NULL),
('Rutvik Mainkar', '102', 'rutvik@gmail.com', '9000000002', 'Computer Engineering', 2, NULL),
('Rishit Shah', '103', 'rishit@gmail.com', '9000000003', 'Computer Engineering', 2, NULL),
('Soham Desai', '104', 'soham@gmail.com', '9000000004', 'Computer Engineering', 2, NULL),
('Manthan Joshi', '105', 'manthan@gmail.com', '9000000005', 'Computer Engineering', 2, NULL),
('Harshad Kulkarni', '106', 'harshad@gmail.com', '9000000006', 'Computer Engineering', 2, NULL),
('Rehan Khan', '107', 'rehan@gmail.com', '9000000007', 'Computer Engineering', 2, NULL),
('Sunny Verma', '108', 'sunny@gmail.com', '9000000008', 'Computer Engineering', 2, NULL),
('Swastik Rao', '109', 'swastik@gmail.com', '9000000009', 'Computer Engineering', 2, NULL),
('Aman Gupta', '110', 'aman@gmail.com', '9000000010', 'Computer Engineering', 2, NULL);

-- ============================================
-- ENROLL ALL STUDENTS INTO DBMS (subject_id = 1)
-- ============================================

INSERT INTO enrollments (student_id, subject_id)
SELECT student_id, 1 FROM students;

-- ============================================
-- ENROLL FIRST 5 STUDENTS INTO PYTHON (subject_id = 2)
-- ============================================

INSERT INTO enrollments (student_id, subject_id)
SELECT student_id, 2 FROM students WHERE student_id <= 5;
