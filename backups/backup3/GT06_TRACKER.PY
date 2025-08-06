import socket
import datetime

HOST = '200.58.98.187'
PORT = 5003

LOG_FILE = "datosChino.txt"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def handle_login(data):
    imei = data[4:-2].hex()
    log(f"[LOGIN] IMEI: {imei}")
    # ACK de login según protocolo GT06
    serial = data[-4:-2]  # serial no. (2 bytes antes de 0D0A)
    ack = b'\x78\x78\x05\x01' + serial + b'\x00\x00\x0D\x0A'
    # checksum (los dos 00s deberían reemplazarse si se quiere calcular correctamente)
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
                    log(f"Datos recibidos: {data.hex()}")

                    if data.startswith(b'\x78\x78'):
                        tipo_paquete = data[3]

                        if tipo_paquete == 0x01:  # Login
                            respuesta = handle_login(data)
                            conn.sendall(respuesta)
                        elif tipo_paquete == 0x12:  # Posicion
                            parse_position(data)
                        else:
                            log(f"[WARNING] Tipo de paquete no reconocido: 0x{tipo_paquete:02X}")
                    else:
                        log("[ERROR] Paquete no comienza con cabecera 7878")

if __name__ == "__main__":
    main()
