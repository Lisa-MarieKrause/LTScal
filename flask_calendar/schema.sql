DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS lesson;

CREATE TABLE schedule (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date DATETIME NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  repetition_id TEXT,
  series_id INTEGER,
  repetition_end_date DATETIME,
  TC1 BOOLEAN,
  TC2 BOOLEAN,
  TC3 BOOLEAN,
  TC4 BOOLEAN,
  name TEXT,
  coach TEXT,
  max_participants INTEGER,
  act_participants INTEGER,
  price DECIMAL,
  details TEXT,
  color TEXT,
  created_at DATETIME,
  cancelled_at DATETIME
);

CREATE TABLE member (
  id INTEGER PRIMARY KEY,
  lastname TEXT,
  surname TEXT,
  title TEXT,
  active_status BOOLEAN,
  gender TEXT,
  birthdate DATETIME,
  kid_status BOOLEAN,
  lastname_parent TEXT,
  surname_parent TEXT,
  title_parent TEXT,
  greeting TEXT,
  street TEXT,
  zip_code TEXT,
  city TEXT,
  tel_number1 TEXT,
  tel_number2 TEXT,
  email_address1 TEXT,
  email_address2 TEXT,
  notes TEXT,
  entered_at DATETIME,
  updated_at DATETIME
);

CREATE TABLE lesson (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  schedule_id INTEGER NOT NULL,
  participant_id INTEGER NOT NULL,
  cancelled_at DATETIME,
  cancellation_id INTEGER,
  cancellation_text TEXT,
  FOREIGN KEY (schedule_id) REFERENCES schedule (id),
  FOREIGN KEY (participant_id) REFERENCES member (id)
);

