class VehicleData:

    latitude = 0
    longitude = 0.0

    @staticmethod
    def setGpsData(_lat, _long):
        VehicleData.latitude = _lat
        VehicleData.longitude = _long

