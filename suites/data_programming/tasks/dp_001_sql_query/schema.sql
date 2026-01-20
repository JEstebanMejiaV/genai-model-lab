DROP TABLE IF EXISTS calls;

CREATE TABLE calls (
  call_date TEXT NOT NULL,
  program TEXT NOT NULL,
  amount REAL NOT NULL
);

INSERT INTO calls (call_date, program, amount) VALUES
('2012-01-05', 'corporativo', 10.0),
('2012-01-07', 'corporativo', 15.0),
('2012-02-01', 'prepago', 8.0),
('2012-02-11', 'prepago', 12.0),
('2011-12-31', 'prepago', 99.0),
('2012-03-10', 'premium', 100.0),
('2013-01-01', 'corporativo', 999.0);
