import cv2
import os
import face_recognition
import numpy as np
from datetime import datetime
import time
import pickle

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

    # Count total images to detect changes (cache invalidation)
    total_images_count = sum(
        len([f for f in os.listdir(os.path.join(DATASET, d)) if not f.startswith('.')])
        for d in os.listdir(DATASET) if os.path.isdir(os.path.join(DATASET, d))
    )

    CACHE_FILE = os.path.join(DATASET, "encodings_cache.pkl")
    cache_loaded = False

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
                if data.get("image_count") == total_images_count:
                    known_encodings = data["encodings"]
                    known_roll_numbers = data["roll_numbers"]
                    cache_loaded = True
                    print("\n[INFO] Fast Startup: Math skipped, loaded from cache!")
        except Exception:
            pass

    for roll_number in os.listdir(DATASET):
        student_folder = os.path.join(DATASET, roll_number)

        # Skip if it's not a directory or not in our database
        if not os.path.isdir(student_folder) or roll_number not in student_map:
            continue

        student_paths[roll_number] = student_folder

        # Only run heavy math if cache missed or was outdated
        if not cache_loaded:
            for img_name in os.listdir(student_folder):
                # Ignore hidden files like .DS_Store
                if img_name.startswith('.'):
                    continue

                path = os.path.join(student_folder, img_name)
                image = face_recognition.load_image_file(path)
                # Build robust encoding by applying jitters
                encodings = face_recognition.face_encodings(image, num_jitters=5, model="large")

                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_roll_numbers.append(roll_number)

    # Save to cache if we just computed them
    if not cache_loaded and len(known_encodings) > 0:
        try:
            with open(CACHE_FILE, "wb") as f:
                pickle.dump({
                    "encodings": known_encodings,
                    "roll_numbers": known_roll_numbers,
                    "image_count": total_images_count
                }, f)
        except Exception:
            pass

    print(f"[INFO] Dataset loaded: {len(known_roll_numbers)} encodings found.")
    print("[INFO] Starting Camera. Press 'Q' to stop.")

    # 3. Start Camera Loop
    # Use CAP_DSHOW on Windows for instant camera initialization
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    PAUSE_TIME = 900  # 15 minutes
    start_time = time.time()
    paused = False

    # Optimization flags & variables
    frame_count = 0
    locations = []
    encodings = []
    face_names = []

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # --- OPTIMIZATION: Resize and Skip Frames ---
            # Process exactly 1 out of every 5 frames to maximize smoothness
            if frame_count % 5 == 0:
                # Shrink frame to 0.4x (catches smaller background faces without huge CPU lag)
                small_frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                locations = face_recognition.face_locations(rgb_small_frame)
                encodings = face_recognition.face_encodings(rgb_small_frame, locations)

                face_names = []
                for face_encoding in encodings:
                    # Lower tolerance for strict matching (default 0.6)
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
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
                                if face_dist[best_match] > 0.4:
                                    folder = student_paths[matched_roll]
                                    filename = f"update_{datetime.now().strftime('%H%M%S')}.jpg"

                                    # Scale coordinates back up (1 / 0.4 = 2.5) to crop from the original HD frame
                                    top, right, bottom, left = locations[encodings.index(face_encoding)]
                                    top, right, bottom, left = int(top * 2.5), int(right * 2.5), int(bottom * 2.5), int(left * 2.5)

                                    cv2.imwrite(os.path.join(folder, filename), frame[top:bottom, left:right])
                                    print(f"[UPDATE] New face angle saved for {name}")

                    if matched_roll:
                        face_names.append(f"{name} ({matched_roll})")
                    else:
                        face_names.append(name)

            # (Math throttling replaces the old boolean toggle)

            # --- PREMIUM HUD & UI EFFECTS ---
            # 1. Top status banner with alpha blend
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 55), (20, 20, 20), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # System text on banner
            cv2.putText(frame, f"SMART ATTENDANCE SYSTEM | SESSION: {session_id}", (15, 35), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Live timestamp on banner
            live_time = datetime.now().strftime('%b %d | %H:%M:%S')
            cv2.putText(frame, live_time, (frame.shape[1] - 220, 35), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (200, 255, 200), 1)

            # Footer hints
            cv2.putText(frame, "Press 'Q' to Stop Camera", (15, frame.shape[0] - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

            for (top, right, bottom, left), name in zip(locations, face_names):
                # Scale back up face locations (1 / 0.4 = 2.5 multiplier)
                top = int(top * 2.5)
                right = int(right * 2.5)
                bottom = int(bottom * 2.5)
                left = int(left * 2.5)

                if name == "UNKNOWN":
                    if not unknown_shown:
                        print("[WARNING] Unknown person detected")
                        unknown_shown = True
                    color = (0, 0, 255)  # Red Alert
                    status_text = "ACCESS DENIED"
                else:
                    color = (0, 255, 0)  # Green Success
                    status_text = "LOGGED"

                # Sci-Fi Corner Brackets
                L = min(30, int((right - left) * 0.25))  # Bracket arm length
                t = 2  # Thickness
                
                # Top-Left
                cv2.line(frame, (left, top), (left + L, top), color, t)
                cv2.line(frame, (left, top), (left, top + L), color, t)
                # Top-Right
                cv2.line(frame, (right, top), (right - L, top), color, t)
                cv2.line(frame, (right, top), (right, top + L), color, t)
                # Bottom-Left
                cv2.line(frame, (left, bottom), (left + L, bottom), color, t)
                cv2.line(frame, (left, bottom), (left, bottom - L), color, t)
                # Bottom-Right
                cv2.line(frame, (right, bottom), (right - L, bottom), color, t)
                cv2.line(frame, (right, bottom), (right, bottom - L), color, t)

                # Solid Nameplate Background
                cv2.rectangle(frame, (left, bottom), (right, bottom + 35), color, cv2.FILLED)
                
                # Name & Status Labels
                cv2.putText(frame, name, (left + 5, bottom + 25), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 0, 0), 1)
                cv2.putText(frame, status_text, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 0.55, color, 1)

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
    print("\n[STOPPED] Teacher closed the attendance camera.")
    return True