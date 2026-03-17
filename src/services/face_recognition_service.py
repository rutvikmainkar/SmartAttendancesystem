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

    # Optimization flags & variables
    process_this_frame = True
    locations = []
    encodings = []
    face_names = []

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            # --- OPTIMIZATION: Resize and Skip Frames ---
            if process_this_frame:
                # Shrink frame to 1/4 size for exponentially faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                locations = face_recognition.face_locations(rgb_small_frame)
                encodings = face_recognition.face_encodings(rgb_small_frame, locations)

                face_names = []
                for face_encoding in encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    face_dist = face_recognition.face_distance(known_encodings, face_encoding)

                    name = "UNKNOWN"
                    matched_roll = None

                    if len(face_dist) > 0:
                        best_match = np.argmin(face_dist)
                        if matches[best_match]:
                            matched_roll = known_roll_numbers[best_match]
                            student_id, name = student_map[matched_roll]

                            # Mark DB Attendance (Exactly once per session)
                            if matched_roll not in attendance_marked:
                                attendance_marked.add(matched_roll)
                                print(f"[SUCCESS] Recognized {name} (Roll: {matched_roll})")
                                record_attendance(session_id, student_id)

                                # Update face dataset if appearance slightly changed
                                if face_dist[best_match] > 0.45:
                                    folder = student_paths[matched_roll]
                                    filename = f"update_{datetime.now().strftime('%H%M%S')}.jpg"

                                    # Scale coordinates back up to 4x to crop from the original HD frame
                                    top, right, bottom, left = locations[encodings.index(face_encoding)]
                                    top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

                                    cv2.imwrite(os.path.join(folder, filename), frame[top:bottom, left:right])
                                    print(f"[UPDATE] New face angle saved for {name}")

                    face_names.append(name)

            # Toggle the flag to skip the next frame's processing math
            process_this_frame = not process_this_frame

            # --- DRAWING RESULTS ON THE FULL-SIZE HD FRAME ---
            for (top, right, bottom, left), name in zip(locations, face_names):
                # Scale back up face locations since we found them on a 1/4 size frame
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                if name == "UNKNOWN":
                    if not unknown_shown:
                        print("[WARNING] Unknown person detected")
                        unknown_shown = True
                    color = (0, 0, 255)  # Red for Unknown
                else:
                    color = (0, 255, 0)  # Green for Recognized

                # Draw Box and Label
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow("Smart Attendance Camera", frame)

            # Auto-Pause Logic (15 Minutes)
            if time.time() - start_time > PAUSE_TIME:
                paused = True
                print("\n[PAUSED] 15 minutes completed. Press 'C' to Continue or 'Q' to Stop.")

        # --- KEYBOARD CONTROLS ---
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