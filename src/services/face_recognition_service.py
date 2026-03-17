import cv2
import os
import face_recognition
import numpy as np
from datetime import datetime
import time

from src.database.connection import get_connection
from src.services.attendance_service import record_attendance

# Pointing to the static images folder you set up earlier
DATASET = os.path.join(os.getcwd(), "frontend", "static", "images")


def run_smart_camera(session_id):
    """
    Opens the webcam, recognizes faces, and automatically logs attendance
    into the MySQL database for the given session_id.
    """
    known_encodings = []
    known_roll_numbers = []
    student_paths = {}
    attendance_marked = set()
    unknown_shown = False

    print("\n[INFO] Loading face dataset from database & file system...")

    # 1. Fetch mapping of roll_number -> (student_id, full_name) from DB
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id, roll_number, full_name FROM students")
    students_db = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create a quick lookup dictionary: {'101': (1, 'Urvaksh Patel')}
    student_map = {str(s['roll_number']): (s['student_id'], s['full_name']) for s in students_db}

    # 2. Load Images from File System
    if not os.path.exists(DATASET):
        os.makedirs(DATASET)
        print(f"[WARNING] Created {DATASET}. Please add folders named by roll number.")
        return False

    for roll_number in os.listdir(DATASET):
        student_folder = os.path.join(DATASET, roll_number)

        # Skip if it's not a directory or not in our database
        if not os.path.isdir(student_folder) or roll_number not in student_map:
            continue

        student_paths[roll_number] = student_folder

        for img_name in os.listdir(student_folder):
            # Ignore hidden files like .DS_Store
            if img_name.startswith('.'):
                continue

            path = os.path.join(student_folder, img_name)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_roll_numbers.append(roll_number)

    print(f"[INFO] Dataset loaded: {len(known_roll_numbers)} encodings found.")
    print("[INFO] Starting Camera. Press 'Q' to stop.")

    # 3. Start Camera Loop
    cap = cv2.VideoCapture(0)

    PAUSE_TIME = 900  # 15 minutes
    start_time = time.time()
    paused = False

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)

            for face_encoding, (top, right, bottom, left) in zip(encodings, locations):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_dist = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_dist) == 0:
                    continue

                best_match = np.argmin(face_dist)

                if matches[best_match]:
                    matched_roll = known_roll_numbers[best_match]
                    student_id, full_name = student_map[matched_roll]

                    # Draw Box (Green)
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, full_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # Mark DB Attendance exactly once per session
                    if matched_roll not in attendance_marked:
                        attendance_marked.add(matched_roll)
                        print(f"[SUCCESS] Recognized {full_name} (Roll: {matched_roll})")
                        record_attendance(session_id, student_id)

                        # Save updated face if slightly different (threshold > 0.45)
                        if face_dist[best_match] > 0.45:
                            folder = student_paths[matched_roll]
                            filename = f"update_{datetime.now().strftime('%H%M%S')}.jpg"
                            cv2.imwrite(os.path.join(folder, filename), frame[top:bottom, left:right])
                            print(f"[UPDATE] New face angle saved for {full_name}")

                else:
                    if not unknown_shown:
                        print("[WARNING] Unknown person detected")
                        unknown_shown = True

                    # Draw Box (Red)
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "UNKNOWN", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("Smart Attendance Camera", frame)

            # Auto-Pause Logic
            if time.time() - start_time > PAUSE_TIME:
                paused = True
                print("\n[PAUSED] 15 minutes completed. Press 'C' to Continue or 'Q' to Stop.")

        key = cv2.waitKey(1) & 0xFF

        if paused:
            if key == ord('c'):
                paused = False
                start_time = time.time()
                print("\n[RESUMED] Attendance Camera Continued")
            elif key == ord('q'):
                break
        else:
            if key == ord('q'):
                break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n[STOPPED] Camera Feed Closed.")
    return True