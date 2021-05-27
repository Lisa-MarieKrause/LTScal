DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS lesson;
DROP VIEW IF EXISTS invoice;

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

CREATE TABLE weatherForecast (
  startTime DATETIME PRIMARY KEY,
  temperature DECIMAL,
  precipitationProbability DECIMAL,
  precipitationIntensity DECIMAL,
  windSpeed DECIMAL,
  cloudCover DECIMAL,
  weatherCode INTEGER,
  Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW invoice AS

WITH inv_temp AS (
   SELECT
      member.id AS member_id,
      IIF(kid_status, lastname_parent || ", " || surname_parent, lastname || ", " || surname) AS name,
      IIF(kid_status, lastname || ", " || surname, "") AS name2,
      street,
      zip_code,
      city,
      CAST(strftime("%m", date) AS INTEGER) AS inv_month,
      schedule.date AS date,
      schedule.price AS price,
      schedule.coach AS coach,
      schedule.name AS description
     FROM schedule
     JOIN lesson ON schedule.id = lesson.schedule_id
     JOIN member ON lesson.participant_id = member.id
     ),
    inv_stage AS (
    SELECT *,
    (CAST(member_id AS TEXT) || "-" || CAST(inv_month AS TEXT)) AS inv_id,
    MAX(date) OVER (PARTITION BY inv_month ORDER BY member_id ) AS last_date
    FROM inv_temp
    )
 SELECT *, DATE(last_date,"+1 months","weekday 1") AS inv_due_date
 FROM inv_stage
/* invoice(member_id,name,name2,street,zip_code,city,inv_month,date,price,coach,description,inv_id,last_date,inv_due_date) */;
