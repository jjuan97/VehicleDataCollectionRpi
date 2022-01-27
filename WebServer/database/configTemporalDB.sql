CREATE TABLE IF NOT EXISTS temporalData (
	id INTEGER,
	latitude NUMBER,
	longitude NUMBER,
	speed NUMBER,
	acc_pos NUMBER
);

INSERT OR REPLACE INTO temporalData (id, latitude, longitude, speed, acc_pos)
	VALUES (0, 1.0, 1.0, 0, 0);
