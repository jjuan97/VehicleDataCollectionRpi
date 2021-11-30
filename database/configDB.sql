CREATE TABLE IF NOT EXISTS vehicledata (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	idTrip INTEGER,
	idVehicle TEXT,
	timestamp DATETIME,
	speed NUMBER,
	accX NUMBER,
	accY NUMBER,
	accZ NUMBER,
	velAngX NUMBER,
	velAngY NUMBER,
	velAngZ NUMBER,
	magX NUMBER,
	magY NUMBER,
	magZ NUMBER,
	latitude NUMBER,
	longitude NUMBER,
	breakPosition NUMBER,
	eventClass BOOLEAN
);

CREATE TABLE IF NOT EXISTS gpsTempData (
	id INTEGER PRIMARY KEY,
	latitude NUMBER,
	longitude NUMBER
);

INSERT INTO gpsTempData (id, latitude, longitude) VALUES(0,0,0) 
ON CONFLICT(id) DO 
UPDATE SET id=0, latitude=0, longitude=0;
