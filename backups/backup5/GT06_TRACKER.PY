import socket
import binascii
import datetime
import struct

HOST = '200.58.98.187'
PORT = 5003

LOG_FILE = 'datosChino.txt'

def log_event(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def parse_imei(payload):
    imei_bcd = payload[2:10]  # 8 bytes
    imei = ''.join(f"{(b & 0xF0) >> 4}{b & 0x0F}" for b in imei_bcd).lstrip('0')
    return imei

def parse_position(payload):
    imei = payload[2:10]
    imei_str = ''.join(f"{(b >> 4)}{(b & 0x0F)}" for b in imei).lstrip('0')
    
    date = payload[10:16]
    dt = f"20{date[0]:02X}-{date[1]:02X}-{date[2]:02X} {date[3]:02X}:{date[4]:02X}:{date[5]:02X}"

    lat_raw = int.from_bytes(payload[20:24], 'big') / 30000 / 60
    lon_raw = int.from_bytes(payload[24:28], 'big') / 30000 / 60
    speed = payload[28]
    course = int.from_bytes(payload[30:32], 'big') & 0x03FF

    return imei_str, dt, lat_raw, lon_raw, speed, course

def send_ack_login(conn, serial):
    ack = b'\x78\x78\x05\x01' + serial + b'\x00\x00\x0D\x0A'
    checksum = 0
    for b in ack[2:-4]:
        checksum ^= b
    ack = ack[:6] + struct.pack('>H', checksum) + ack[8:]
    conn.sendall(ack)
    log_event("[INFO] ACK de login enviado")

def handle_client(conn, addr):
    log_event(f"Conexion entrante desde {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        hexdata = binascii.hexlify(data).decode().upper()
        log_event(f"Datos recibidos: {hexdata}")

        if len(data) < 5:
            continue

        package_type = data[3]

        if package_type == 0x01:
            log_event("[INFO] Paquete de LOGIN recibido")
            send_ack_login(conn, data[-4:-2])
            imei = parse_imei(data)
            log_event(f"[INFO] IMEI: {imei}")

        elif package_type == 0x12:
            log_event("[INFO] Paquete de POSICION recibido")
            try:
                imei, timestamp, lat, lon, speed, course = parse_position(data)
                log_event(f"ID: {imei}, LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}")
            except Exception as e:
                log_event(f"[ERROR] Fallo al decodificar posicion: {str(e)}")
        else:
            log_event(f"[WARNING] Tipo de paquete no reconocido: 0x{package_type:02X}")

    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        log_event(f"Servidor iniciado en {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == '__main__':
    start_server()
