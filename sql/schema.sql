-- ============================================================
--  Smart Attendance System — Final Schema
--  Engine : InnoDB | Charset : utf8mb4 | Collation : unicode_ci
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_attendance
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_attendance;

-- ────────────────────────────────────────────────────────────
-- 1. professors
--
--  prof_id   : human-readable login key (PROF001, PROF002 …)
--              used by the admin/professor login form.
--              Kept separate from professor_id so the internal
--              PK / FK chain never needs to change even if a
--              prof_id is reassigned.
--  department: plain VARCHAR — no lookup table needed at this
--              scale; keep it consistent via the application.
-- ────────────────────────────────────────────────────────────
CREATE TABLE professors (
    professor_id   INT            NOT NULL AUTO_INCREMENT,
    prof_id        VARCHAR(20)    NOT NULL,
    full_name      VARCHAR(100)   NOT NULL,
    email          VARCHAR(100)   NOT NULL,
    phone          VARCHAR(15),
    department     VARCHAR(100),
    PRIMARY KEY (professor_id),
    UNIQUE KEY uq_prof_id         (prof_id),
    UNIQUE KEY uq_professor_email (email)
);

-- ────────────────────────────────────────────────────────────
-- 2. students
--
--  face_encoding : LONGBLOB — stores the 128-d numpy array
--                 serialised with pickle/numpy.tobytes().
--                 Loaded into memory by the capture service
--                 at startup; never queried by the web layer.
--  image_path    : relative path to the enrolled face photo,
--                 used for display in the dashboard.
--  is_active     : soft-delete flag. Inactive students are
--                 excluded from recognition and reports.
--  created_at    : audit trail; set once on INSERT.
-- ────────────────────────────────────────────────────────────
CREATE TABLE students (
    student_id     INT            NOT NULL AUTO_INCREMENT,
    full_name      VARCHAR(100)   NOT NULL,
    roll_number    VARCHAR(50)    NOT NULL,
    email          VARCHAR(100),
    phone          VARCHAR(15),
    department     VARCHAR(100),
    year           TINYINT        UNSIGNED,
    image_path     VARCHAR(255),
    face_encoding  LONGBLOB,
    is_active      TINYINT(1)     NOT NULL DEFAULT 1,
    created_at     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id),
    UNIQUE KEY uq_roll_number (roll_number),
    KEY idx_student_active (is_active)
);

-- ────────────────────────────────────────────────────────────
-- 3. subjects
--
--  professor_id lives on lecture_sessions, not here.
--  A subject is a catalogue entry; who teaches it and when
--  is a session-level concern.
-- ────────────────────────────────────────────────────────────
CREATE TABLE subjects (
    subject_id     INT            NOT NULL AUTO_INCREMENT,
    subject_name   VARCHAR(100)   NOT NULL,
    subject_code   VARCHAR(20)    NOT NULL,
    department     VARCHAR(100),
    credits        TINYINT        UNSIGNED NOT NULL DEFAULT 3,
    PRIMARY KEY (subject_id),
    UNIQUE KEY uq_subject_code (subject_code)
);

-- ────────────────────────────────────────────────────────────
-- 4. enrollments
--
--  One row per student-subject pair.
--  status  : 'active'    — currently attending
--            'dropped'   — withdrew mid-semester
--            'completed' — semester finished
--  The defaulter query filters on status = 'active'.
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
    CONSTRAINT fk_enroll_student
        FOREIGN KEY (student_id) REFERENCES students (student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_enroll_subject
        FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
        ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 5. lecture_sessions
--
--  One row per scheduled class.
--  professor_id  : which professor is taking this specific
--                 session (can differ per batch / substitute).
--                 ON DELETE SET NULL — sessions survive even
--                 if a professor record is removed.
--  is_cancelled  : cancelled sessions are excluded from the
--                 denominator in attendance % calculations.
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
    KEY idx_session_date    (session_date),
    KEY idx_session_subject (subject_id),
    CONSTRAINT fk_session_subject
        FOREIGN KEY (subject_id)   REFERENCES subjects   (subject_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_session_professor
        FOREIGN KEY (professor_id) REFERENCES professors (professor_id)
        ON DELETE SET NULL
);

-- ────────────────────────────────────────────────────────────
-- 6. active_session_config
--
--  Single-row "what session is live right now" signal for the
--  face-recognition capture service.
--
--  Flow:
--    Professor clicks "Start session" on the dashboard
--    → Flask inserts / updates one row here.
--    Capture service polls this table every N seconds.
--    If a row exists with is_active=1 AND NOW() < expires_at
--    → write attendance_logs against that session_id.
--    Professor clicks "End session" OR expires_at passes
--    → is_active flips to 0; capture service stops marking.
--
--  session_id    : FK to the lecture_sessions row being run.
--  activated_at  : when the professor started the session.
--  expires_at    : hard cutoff (e.g. activated_at + 90 min).
--                 Prevents a forgotten open session from
--                 marking attendance indefinitely.
--  is_active     : 1 = live, 0 = closed.
--                 Index on this column — polled frequently.
--
--  Only one session should be active at a time per camera /
--  room. Enforce this in the application layer before INSERT.
-- ────────────────────────────────────────────────────────────
CREATE TABLE active_session_config (
    config_id      INT            NOT NULL AUTO_INCREMENT,
    session_id     INT            NOT NULL,
    activated_at   TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at     TIMESTAMP      NOT NULL,
    is_active      TINYINT(1)     NOT NULL DEFAULT 1,
    PRIMARY KEY (config_id),
    KEY idx_asc_active     (is_active),
    KEY idx_asc_session    (session_id),
    CONSTRAINT fk_asc_session
        FOREIGN KEY (session_id) REFERENCES lecture_sessions (session_id)
        ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 7. attendance_logs
--
--  One row per student per session — enforced by the unique
--  key on (session_id, student_id).
--
--  status    : 'Present'   — recognised within the window
--              'Late'      — recognised after a grace period
--              'Absent'    — not seen / manually entered
--              'EarlyExit' — left before session ended
--
--  marked_by : 'face_recognition' — written by capture daemon
--              'manual'           — professor override
--              'imported'         — bulk CSV import
--
--  marked_at : exact timestamp of the recognition event.
--              Present vs Late distinction is computed here:
--              if marked_at > session.start_time + grace → Late.
--
--  remarks   : free-text field for edge cases — proxy flag,
--              medical leave note, manual override reason.
-- ────────────────────────────────────────────────────────────
CREATE TABLE attendance_logs (
    log_id         INT            NOT NULL AUTO_INCREMENT,
    session_id     INT            NOT NULL,
    student_id     INT            NOT NULL,
    status         ENUM('Present','Late','Absent','EarlyExit')
                                  NOT NULL DEFAULT 'Absent',
    marked_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    marked_by      ENUM('face_recognition','manual','imported')
                                  NOT NULL DEFAULT 'face_recognition',
    remarks        TEXT,
    PRIMARY KEY (log_id),
    UNIQUE KEY uq_session_student (session_id, student_id),
    KEY idx_log_student (student_id),
    KEY idx_log_session (session_id),
    CONSTRAINT fk_log_session
        FOREIGN KEY (session_id)  REFERENCES lecture_sessions (session_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_log_student
        FOREIGN KEY (student_id)  REFERENCES students (student_id)
        ON DELETE CASCADE
);

-- ────────────────────────────────────────────────────────────
-- 8. monthly_defaulter_snapshots
--
--  Frozen month-end calculation — one row per student per
--  subject per month.  Generated by the report service and
--  stored so historical defaulter lists are always queryable
--  without recalculating.
--
--  sessions_held     : non-cancelled sessions in that month
--                     for the subject.
--  sessions_attended : sessions where status IN
--                     ('Present','Late') for that student.
--  attendance_pct    : pre-computed percentage, 2 d.p.
--  is_defaulter      : 1 if attendance_pct < 75.00
--
--  The unique key on (student_id, subject_id, month, year)
--  prevents duplicate snapshots if the job is re-run.
--  Use INSERT … ON DUPLICATE KEY UPDATE to allow reruns
--  that refresh stale data within the same month.
-- ────────────────────────────────────────────────────────────
CREATE TABLE monthly_defaulter_snapshots (
    snapshot_id       INT              NOT NULL AUTO_INCREMENT,
    student_id        INT              NOT NULL,
    subject_id        INT              NOT NULL,
    month             TINYINT UNSIGNED NOT NULL,   -- 1–12
    year              YEAR             NOT NULL,
    sessions_held     SMALLINT         NOT NULL DEFAULT 0,
    sessions_attended SMALLINT         NOT NULL DEFAULT 0,
    attendance_pct    DECIMAL(5,2)     NOT NULL DEFAULT 0.00,
    is_defaulter      TINYINT(1)       NOT NULL DEFAULT 0,
    generated_at      TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (snapshot_id),
    UNIQUE KEY uq_snapshot (student_id, subject_id, month, year),
    KEY idx_snap_defaulter (is_defaulter),
    KEY idx_snap_month_year (year, month),
    CONSTRAINT fk_snap_student
        FOREIGN KEY (student_id) REFERENCES students (student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_snap_subject
        FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
        ON DELETE CASCADE
);