import threading
import time
import serial
from queue import Queue
import modules

# 시리얼 포트 설정
serial_port = '/dev/ttyACM0'  # 아두이노 시리얼 포트
baud_rate = 9600  # 보드레이트

# 센서 값을 전달하기 위한 큐
queue = Queue()

def serial_reader():
    """시리얼 데이터를 읽어서 큐에 전달하는 스레드"""
    ser = serial.Serial(serial_port, baud_rate)
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            parts = line.split(',')

            # 시리얼 데이터 출력
            print('Serial_토양습도: ', int(parts[0]))
            print('Serial_물탱크수위: ', int(parts[0]))
            print('Serial_조도: ', int(parts[0]))
            print('Serial_온도: ', int(parts[0]))
            print('Serial_습도: ', int(parts[0]))

            # 큐에 데이터 넣기
            queue.put(('soil_moisture_value', int(parts[0])))	# 첫 번째 값: 토양 습도
            queue.put(('water_tank_value', int(parts[1])))	# 두 번째 값: 물탱크 거리
            queue.put(('lux_value', int(parts[2])))	# 세 번째 값: 조도
            queue.put(('temp_value', int(parts[3])))	# 네 번째 값: 온도
            queue.put(('humidity_value', int(parts[4])))	# 다섯 번째 값: 습도

        time.sleep(1)  # 시리얼 데이터를 읽는 주기 (1초)

def start_threads():
    """멀티스레드 실행"""
    # 시리얼 읽기 스레드
    serial_thread = threading.Thread(target=serial_reader, daemon=True)

    # 토양 습도 제어 스레드
    soil_moisture_thread = threading.Thread(target=modules.monitor_and_control_soil_moisture, args=(queue,), daemon=True)

    # 물탱크 수위 기록 스레드
    water_tank_thread = threading.Thread(target=modules.monitor_and_log_water_tank_level, args=(queue,), daemon=True)

	# 일조량 제어 스레드
    light_thread = threading.Thread(target=modules.monitor_and_control_light, args=(queue,), daemon=True)
	
	# 온습도 기록 스레드
    temperature_humidity_thread = threading.Thread(target=modules.monitor_and_log_temperature_humidity, args=(queue,), daemon=True)
	
	# 카메라 촬영 스레드
    capture_photos_thred = threading.Thread(tartget=modules.capture_photos_from_webcam, daemon=True)

	# 텔레그램 봇 인터페이스 스레드
    load_telegram_thred = threading.Thread(tartget=modules.load_telegram, daemon=True)

	# 사용자 인터페이스 스레드
    telegram_userinterface = threading.Thread(tartget=modules.main, daemon=True)

    # 스레드 시작
    serial_thread.start()
    soil_moisture_thread.start()
    water_tank_thread.start()
    light_thread.start()
    temperature_humidity_thread.start()
    capture_photos_thred.start()
    load_telegram_thred.start()
    telegram_userinterface.start()

    # 메인 스레드는 계속 실행되어야 함
    serial_thread.join()
    soil_moisture_thread.join()
    water_tank_thread.join()
    light_thread.join()
    temperature_humidity_thread.join()
    capture_photos_thred.join()
    load_telegram_thred.join()
    telegram_userinterface.join()

if __name__ == "__main__":
    try:
        print("**Smart Plant Pot Program Start**")
        start_threads()
    except KeyboardInterrupt:
        print("main.py: Program interrupted.")
