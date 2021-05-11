DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS lesson;

CREATE TABLE schedule (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date DATETIME NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  repetition_id INTEGER,
  court_count INTEGER,
  name TEXT,
  coach TEXT,
  max_participants INTEGER,
  act_participants INTEGER,
  details TEXT,
  color TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE member (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lastname_kid TEXT,
  surname_kid TEXT,
  lastname_parent TEXT,
  surname_parent TEXT,
  gender TEXT,
  birthdate DATETIME,
  zip_code TEXT,
  city TEXT,
  street TEXT,
  tel_number1 TEXT,
  tel_number2 TEXT,
  email_address1 TEXT,
  email_address2 TEXT,
  active BOOLEAN,
  notes TEXT
);

CREATE TABLE lesson (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  schedule_id INTEGER NOT NULL,
  participant_id INTEGER NOT NULL,
  cancelled_at DATETIME,
  cancellation_id INTEGER,
  FOREIGN KEY (schedule_id) REFERENCES schedule (id),
  FOREIGN KEY (participant_id) REFERENCES member (id)
);

