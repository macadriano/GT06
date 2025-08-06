import socket
import datetime

HOST = '200.58.98.187'
PORT = 5003

LOG_FILE = "datosChino.txt"

def crc16(data):
    """
    Calcula el CRC16 para el protocolo GT06
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')  # GT06 usa little-endian para CRC

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def handle_login(data):
    # Estructura del paquete de login: 7878 + length + 01 + IMEI(8) + serial(2) + error_check(2) + CRC16(2) + 0D0A
    if len(data) < 21:  # Longitud mínima del paquete de login
        log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
        return None
        
    imei = data[4:12].hex()  # IMEI está en bytes 4-11
    log(f"[LOGIN] IMEI: {imei}")
    
    serial = data[12:14]  # Serial está en bytes 12-13
    log(f"[LOGIN] Serial: {serial.hex()}")
    
    # Construir ACK: 7878 + 05 + 01 + serial + CRC16 + 0D0A
    ack = b'\x78\x78\x05\x01' + serial
    checksum = crc16(ack[2:])
    ack += checksum + b'\x0D\x0A'
    
    log_sent(ack)
    return ack

def parse_position(data):
    try:
        # Estructura del paquete de posición: 7878 + length + 12 + date(6) + quantity(1) + lat(4) + lon(4) + speed(1) + course(2) + status(1) + mcc(2) + mnc(1) + lac(2) + cell_id(3) + serial(2) + error_check(2) + CRC16(2) + 0D0A
        if len(data) < 35:  # Longitud mínima del paquete de posición
            log(f"[ERROR] Paquete de posición demasiado corto: {len(data)} bytes")
            return
            
        # Extraer campos según la nueva estructura
        date_bytes = data[4:10]  # Fecha/hora en BCD
        quantity = data[10]      # Cantidad de posiciones
        lat_raw = data[11:15]    # Latitud
        lon_raw = data[15:19]    # Longitud
        speed = data[19]         # Velocidad
        course = int.from_bytes(data[20:22], byteorder='big')  # Rumbo
        status = data[22]        # Estado del GPS
        
        # Validar que las coordenadas no sean cero (GPS sin señal)
        if lat_raw == b'\x00\x00\x00\x00' or lon_raw == b'\x00\x00\x00\x00':
            log("[WARNING] Coordenadas GPS en cero - posible falta de señal")
            return
            
        # Convertir coordenadas
        lat_val = int.from_bytes(lat_raw, byteorder='big')
        lon_val = int.from_bytes(lon_raw, byteorder='big')
        
        # Manejar signo de coordenadas
        lat = (lat_val & 0x7FFFFFFF) / 1800000.0
        lon = (lon_val & 0x7FFFFFFF) / 1800000.0
        
        if lat_val & 0x80000000:  # Bit 31 = 1 significa latitud sur
            lat = -lat
        if lon_val & 0x80000000:  # Bit 31 = 1 significa longitud oeste
            lon = -lon
        
        # Validar rangos de coordenadas
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            log(f"[ERROR] Coordenadas fuera de rango: LAT={lat}, LON={lon}")
            return
            
        # Extraer información adicional
        mcc = int.from_bytes(data[24:26], byteorder='big')
        mnc = data[26]
        lac = int.from_bytes(data[27:29], byteorder='big')
        cell_id = int.from_bytes(data[29:32], byteorder='big')
        serial = int.from_bytes(data[32:34], byteorder='big')

        log(f"[POSICION] LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}°")
        log(f"[INFO] MCC: {mcc}, MNC: {mnc}, LAC: {lac}, CellID: {cell_id}, Serial: {serial}")

    except IndexError as e:
        log(f"[ERROR] Error de índice al parsear posición: {e}")
    except ValueError as e:
        log(f"[ERROR] Error de valor al parsear posición: {e}")
    except Exception as e:
        log(f"[ERROR] Error inesperado parseando datos de posicion: {e}")

def main():
    log(f"Servidor iniciado en {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"Conexion entrante desde {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        log(f"[RECIBIDO] {data.hex()}")

                        # Validar longitud mínima del paquete
                        if len(data) < 8:
                            log("[ERROR] Paquete demasiado corto")
                            continue

                        if data.startswith(b'\x78\x78'):
                            # Validar que el paquete tenga la longitud correcta
                            if len(data) >= 4:
                                packet_length = data[2]
                                if len(data) < packet_length + 6:  # 7878 + length + data + crc + 0D0A
                                    log(f"[ERROR] Paquete incompleto. Esperado: {packet_length + 6}, Recibido: {len(data)}")
                                    continue
                            
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
            except socket.error as e:
                log(f"[ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    main()
