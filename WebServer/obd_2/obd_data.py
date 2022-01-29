import obd
from obd import OBDStatus

class OBDData:
	
	connection = obd.Async('/dev/rfcomm0', 9600) # auto-connects to USB or RF port

	speed_conn = connection.watch(obd.commands.SPEED)
	acc_pos_conn = connection.watch(obd.commands.THROTTLE_POS)
	
	speed_conn.start()
	acc_pos_conn.start()
	valor = 2
	
	def __init__(self):
		pass
        
	def get_data(self):
		speed = self.speed_conn.query(obd.commands.SPEED)
		acc_pos = self.acc_pos_conn.query(obd.commands.THROTTLE_POS)
		
		if not speed.is_null() and not acc_pos.is_null():
			return (speed.value.magnitude, acc_pos.value.magnitude)
		else:
			return None
			
	def set_valor(self, x):
		self.valor = x
	
	def get_valor(self):
		return self.valor
			
	def stop_conn(self):
		self.speed_conn.stop()
		self.acc_pos_conn.stop()

def print_data(d):
	for i in range(20):		
		if d == None:
			print("No se encuentran datos")
		else:
			speed, accel_pos = d
		print(f"Velocidad actual: {speed}, Posición del pedal: {accel_pos}")

def main():
	"""Terminal app
	"""
	obd_obj = OBDData()
	print(obd_obj.get_valor())
	obd_obj.set_valor(8)
	print(obd_obj.get_valor())
	
	print_data(obd_obj.get_data())

if __name__ == "__main__":
    main()
