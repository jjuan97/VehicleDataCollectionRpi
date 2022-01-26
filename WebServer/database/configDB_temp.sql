CREATE TABLE IF NOT EXISTS gpslocation (
	id INTEGER,
	latitude NUMBER,
	longitude NUMBER,
	speed NUMBER,
	acc_pos NUMBER
);

INSERT OR REPLACE INTO gpslocation (id, latitude, longitude, speed, acc_pos)
	VALUES (0, 1.0, 1.0, 0, 0);
