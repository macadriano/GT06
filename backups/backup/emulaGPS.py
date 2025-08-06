import socket
import time
import binascii

def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='big')

def build_login_packet(imei: str, serial: int = 1) -> bytes:
    imei_bcd = bytes.fromhex('0' + imei)  # IMEI simulado
    content = b'\x01' + b'\x00' + imei_bcd + serial.to_bytes(2, 'big')
    length = len(content)
    crc = crc16(content)
    return b'\x78\x78' + bytes([length]) + content + crc + b'\x0D\x0A'

def build_location_packet(lat, lon, speed, course, serial=2) -> bytes:
    now = time.gmtime()
    date_bytes = bytes([
        now.tm_year - 2000, now.tm_mon, now.tm_mday,
        now.tm_hour, now.tm_min, now.tm_sec
    ])

    lat_raw = int(lat * 1800000)
    lon_raw = int(lon * 1800000)
    lat_bytes = lat_raw.to_bytes(4, 'big', signed=True)
    lon_bytes = lon_raw.to_bytes(4, 'big', signed=True)
    speed_byte = bytes([speed])
    course_bytes = course.to_bytes(2, 'big')

    dummy_status = bytes([0, 0, 0, 0, 0, 0])
    content = b'\x12' + date_bytes + b'\x00' + lat_bytes + lon_bytes + speed_byte + course_bytes + dummy_status + serial.to_bytes(2, 'big')
    length = len(content)
    crc = crc16(content)
    return b'\x78\x78' + bytes([length]) + content + crc + b'\x0D\x0A'

def send_packet(sock, packet: bytes, description=""):
    print(f"\n--> Enviando {description}: {packet.hex()}")
    sock.sendall(packet)

def receive_response(sock):
    try:
        data = sock.recv(1024)
        if data:
            print("<-- Respuesta del servidor:", data.hex())
    except Exception as e:
        print("Error al recibir respuesta:", e)

def main():
    SERVER_IP = '200.58.98.187'  # Cambiar por IP real del servidor si aplica
    SERVER_PORT = 5003
    imei = '123456789012345'

    # Puntos simulados dentro de CABA
    puntos_movimiento = [
        (-34.603722, -58.381592),  # Obelisco
        (-34.6083, -58.3712),      # Casa Rosada
        (-34.6157, -58.4333),      # Parque Centenario
        (-34.5895, -58.3974),      # Palermo
        (-34.6405, -58.5185),      # Mataderos
    ]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Conectando a {SERVER_IP}:{SERVER_PORT}...")
        sock.connect((SERVER_IP, SERVER_PORT))

        # Enviar login
        login_packet = build_login_packet(imei)
        send_packet(sock, login_packet, "login")
        receive_response(sock)
        time.sleep(2)

        # Enviar cada punto como si se estuviera moviendo
        serial = 2
        for lat, lon in puntos_movimiento:
            packet = build_location_packet(lat, lon, speed=40, course=90, serial=serial)
            send_packet(sock, packet, f"posición {serial - 1}")
            receive_response(sock)
            serial += 1
            time.sleep(5)  # Esperar 5 segundos entre posiciones

if __name__ == '__main__':
    main()
