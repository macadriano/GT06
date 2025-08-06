import socket
import struct
from datetime import datetime

# Configuración del servidor
HOST = '200.58.98.187'
PORT = 5003

# Helper para decodificar BCD a string
def bcd_to_str(bcd_bytes):
    return ''.join(f"{(byte & 0xF0) >> 4}{byte & 0x0F}" for byte in bcd_bytes)

def handle_login_packet(data):
    imei = bcd_to_str(data[4:-2])
    print(f"[LOGIN] IMEI: {imei}")
    response = bytearray()
    response.extend(b'\x78\x78')  # start bit
    response.append(0x05)          # length
    response.append(0x01)          # login response
    response.append(0x01)          # serial high
    response.append(0x00)          # serial low
    checksum = sum(response[2:]) & 0xFFFF
    response.extend(checksum.to_bytes(2, 'big'))
    response.extend(b'\x0D\x0A')
    return response

def handle_position_packet(data):
    print("[INFO] Paquete de posición recibido")
    try:
        date_bcd = data[4:10]
        year = 2000 + int(f"{date_bcd[0]:02x}")
        month = int(f"{date_bcd[1]:02x}")
        day = int(f"{date_bcd[2]:02x}")
        hour = int(f"{date_bcd[3]:02x}")
        minute = int(f"{date_bcd[4]:02x}")
        second = int(f"{date_bcd[5]:02x}")

        # GPS
        lat_raw = struct.unpack('>I', data[11:15])[0]
        lon_raw = struct.unpack('>I', data[15:19])[0]
        lat = lat_raw / 30000.0 / 60.0
        lon = lon_raw / 30000.0 / 60.0
        speed = data[19]
        course = ((data[20] & 0x03) << 8) | data[21]

        print(f"{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}, LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed}, COURSE: {course}")

        # Guardar en archivo
        with open("datosChino.txt", "a") as f:
            f.write(f"{datetime.now()} - IMEI: [pending extraction], LAT: {lat}, LON: {lon}, SPEED: {speed} km/h, COURSE: {course}\n")

    except Exception as e:
        print(f"Error al procesar paquete de posición: {e}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Escuchando en {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"[CONECTADO] {addr}")
        # Guardar en archivo
        with open("datosChino.txt", "a") as f:
            f.write(f"[CONECTADO] {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if len(data) < 5:
                    with open("datosChino.txt", "a") as f:
                        f.write("Paquete muy corto")

                    print("Paquete muy corto")
                    continue

                packet_type = data[3]

                if packet_type == 0x01:
                    response = handle_login_packet(data)
                    conn.sendall(response)
                    print("[ACK] Login enviado")
                    with open("datosChino.txt", "a") as f:
                        f.write("[ACK] Login enviado")
                elif packet_type == 0x12:
                    handle_position_packet(data)
                else:
                    with open("datosChino.txt", "a") as f:
                        f.write(f"[WARNING] Tipo de paquete no reconocido: 0x{packet_type:X}")
                    print(f"[WARNING] Tipo de paquete no reconocido: 0x{packet_type:X}")
