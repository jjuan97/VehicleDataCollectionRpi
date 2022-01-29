CREATE TABLE IF NOT EXISTS obddata (
	id INTEGER PRIMARY KEY,
	speed NUMBER,
	acc_pos NUMBER
);

INSERT OR REPLACE INTO obddata (id, speed, acc_pos)
	VALUES (0, 0.0, 0.0);
