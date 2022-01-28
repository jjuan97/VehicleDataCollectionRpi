CREATE TABLE IF NOT EXISTS obddata (
	id INTEGER,
	speed NUMBER,
	acc_pos NUMBER
);

INSERT OR REPLACE INTO temporalData (id, speed, acc_pos)
	VALUES (0, 0.0, 0.0);