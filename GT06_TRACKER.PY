import socket
import datetime

HOST = '200.58.98.187'
PORT = 5003

LOG_FILE = "datosChino.txt"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def handle_login(data):
    imei = data[4:-6].hex()
    log(f"[LOGIN] IMEI: {imei}")
    serial = data[-6:-4]  # serial no.
    log(serial.hex())
    ack = b'\x78\x78\x05\x01' + serial
    checksum = sum(ack[2:]) & 0xFFFF
    ack += checksum.to_bytes(2, 'big') + b'\x0D\x0A'
    log_sent(ack)
    return ack

def parse_position(data):
    try:
        lat_raw = data[13:17]
        lon_raw = data[17:21]
        lat = int.from_bytes(lat_raw, byteorder='big') / 1800000.0
        lon = int.from_bytes(lon_raw, byteorder='big') / 1800000.0
        speed = data[21]
        course = ((data[22] & 0x03) << 8) | data[23]

        log(f"[POSICION] LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}")

    except Exception as e:
        log(f"[ERROR] Error parseando datos de posicion: {e}")

def main():
    log(f"Servidor iniciado en {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                log(f"Conexion entrante desde {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    log(f"[RECIBIDO] {data.hex()}")

                    if data.startswith(b'\x78\x78'):
                        tipo_paquete = data[3]

                        if tipo_paquete == 0x01:  # Login
                            respuesta = handle_login(data)
                            conn.sendall(respuesta)
                        elif tipo_paquete == 0x12:  # Posición
                            parse_position(data)
                        elif tipo_paquete == 0x13:  # Estado del terminal
                            log(f"[STATUS] Paquete de estado recibido (0x13)")
                        else:
                            log(f"[WARNING] Tipo de paquete no reconocido: 0x{tipo_paquete:02X}")
                    else:
                        log("[ERROR] Paquete no comienza con cabecera 7878")

if __name__ == "__main__":
    main()
