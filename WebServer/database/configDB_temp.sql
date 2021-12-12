CREATE TABLE IF NOT EXISTS gpslocation (
	id INTEGER,
	latitude NUMBER,
	longitude NUMBER
);

INSERT OR REPLACE INTO gpslocation (id, latitude, longitude)
	VALUES (0, 1.0, 1.0);
