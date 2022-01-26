import obd
import time
import tqdm

connection = obd.OBD('/dev/rfcomm0', 9600) # auto-connects to USB or RF port

def read_data():
	res_accel_pos = connection.query(obd.commands.THROTTLE_POS)
	res_speed = connection.query(obd.commands.SPEED)
	
	speed = res_speed.value
	accel_pos = res_accel_pos.value
	
	return (str(speed), str(accel_pos))

def print_data():
	for i in trange(10):
		speed, accel_pos = read_data()
		t = time.time()
		print(f"Velocidad actual: {speed}, Posición del pedal: {accel_pos}, tiempo: {t}")
	
def calculate_time(num : int = 10):
	start = time.time()
	for i in range(num):
		speed, accel_pos = read_data()
	end = time.time()
	t = end-start
	print(f"Tiempo total en realizar {num} iteraciones = {t} s")

def main():
	"""Terminal app
	"""
	option = str(input("Ver datos actuales (presione A), Ver el rendimiento (presione B): ")).upper()
	if option == "A":
		print_data()
		
	elif option == "B":
		iterations = int(input("Numero de iteraciones: "))
		calculate_time(iterations)
		
	else:
		print("Opción invalida")

if __name__ == "__main__":
    main()
