import socket
import datetime
import time
import threading

HOST = '200.58.98.187'
PORT = 5003
pp = 4994

LOG_FILE = "datosChino.txt"

def crc16(data):
    """
    Calcula el CRC16 para el protocolo GT06 (algoritmo correcto)
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

def crc16_big_endian(data):
    """
    Calcula el CRC16 en big-endian (alternativa)
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'big')  # Big-endian

def crc16_gt06_correct(data):
    """
    Calcula el CRC16 correcto para el protocolo GT06
    Algoritmo oficial del GT06 (polinomio 0xA001, valor inicial 0xFFFF)
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'big')  # Big-endian para ACK

def test_crc_example():
    """
    Prueba el CRC del ejemplo del manual
    """
    # Datos del ACK del ejemplo: 05 01 00 02
    ack_data = b'\x05\x01\x00\x02'
    expected_crc = b'\xEB\x47'  # CRC del ejemplo
    
    crc_le = crc16(ack_data)
    crc_be = crc16_big_endian(ack_data)
    crc_gt06 = crc16_gt06_correct(ack_data)
    
    print(f"ACK data: {ack_data.hex()}")
    print(f"Expected CRC: {expected_crc.hex()}")
    print(f"Calculated CRC (LE): {crc_le.hex()}")
    print(f"Calculated CRC (BE): {crc_be.hex()}")
    print(f"Calculated CRC (GT06): {crc_gt06.hex()}")
    
    if crc_le == expected_crc:
        print("✓ CRC coincide con little-endian")
        return 'little'
    elif crc_be == expected_crc:
        print("✓ CRC coincide con big-endian")
        return 'big'
    elif crc_gt06 == expected_crc:
        print("✓ CRC coincide con algoritmo GT06 correcto")
        return 'gt06'
    else:
        print("✗ CRC no coincide con ninguna variante")
        print("Nota: Usando algoritmo oficial del GT06 (polinomio 0xA001)")
        return 'official'

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def send_alternative_ack(serial, conn, ack_type='le'):
    """
    Envía un ACK alternativo con diferentes tipos de CRC
    """
    ack_data = b'\x05\x01' + serial
    
    if ack_type == 'le':
        # Little-endian CRC
        crc = crc16(ack_data)
        log(f"[ACK_LE] Enviando ACK con CRC little-endian: {ack_data.hex()}, CRC: {crc.hex()}")
    elif ack_type == 'be':
        # Big-endian CRC
        crc = crc16_big_endian(ack_data)
        log(f"[ACK_BE] Enviando ACK con CRC big-endian: {ack_data.hex()}, CRC: {crc.hex()}")
    elif ack_type == 'gt06':
        # GT06 oficial CRC
        crc = crc16_gt06_correct(ack_data)
        log(f"[ACK_GT06] Enviando ACK con CRC GT06 oficial: {ack_data.hex()}, CRC: {crc.hex()}")
    else:
        log(f"[ERROR] Tipo de ACK no reconocido: {ack_type}")
        return
    
    ack = b'\x78\x78' + ack_data + crc + b'\x0D\x0A'
    conn.sendall(ack)
    log_sent(ack)

def auto_retry_ack(serial, conn, conn_data):
    """
    Sistema automático de reintentos de ACK
    Prueba diferentes tipos de CRC automáticamente
    """
    def retry_thread():
        # Tipos de ACK a probar en orden
        ack_types = ['le', 'be', 'gt06']
        current_ack = 0
        
        # Esperar 3 segundos antes del primer reintento
        time.sleep(3)
        
        while current_ack < len(ack_types) and not conn_data.get('ack_success', False):
            if conn_data.get('connection_closed', False):
                break
                
            ack_type = ack_types[current_ack]
            log(f"[AUTO_RETRY] Intento {current_ack + 1}/3: Probando ACK tipo '{ack_type}'")
            
            try:
                send_alternative_ack(serial, conn, ack_type)
                conn_data['current_ack_type'] = ack_type
                conn_data['ack_attempts'] = conn_data.get('ack_attempts', 0) + 1
                
                # Esperar 5 segundos antes del siguiente intento
                time.sleep(5)
                current_ack += 1
                
            except Exception as e:
                log(f"[ERROR] Error en auto_retry_ack: {e}")
                break
        
        if not conn_data.get('ack_success', False):
            log(f"[AUTO_RETRY] Completados {len(ack_types)} intentos sin éxito")
    
    # Iniciar thread de reintentos
    retry_thread = threading.Thread(target=retry_thread, daemon=True)
    retry_thread.start()
    conn_data['retry_thread'] = retry_thread

def validate_packet_crc(data):
    """
    Valida el CRC16 de un paquete recibido
    """
    if len(data) < 6:  # Mínimo: 7878 + length + data + CRC16 + 0D0A
        return False
    
    # Extraer datos para calcular CRC (desde length hasta antes del CRC)
    packet_data = data[2:-4]  # Sin 7878 y sin CRC16 + 0D0A
    received_crc = data[-4:-2]  # CRC recibido
    
    # Calcular diferentes variantes del CRC
    expected_crc_le = crc16(packet_data)  # Little-endian
    expected_crc_be = crc16_big_endian(packet_data)  # Big-endian
    expected_crc_gt06 = crc16_gt06_correct(packet_data)  # GT06 correcto
    
    log(f"[DEBUG] Packet data: {packet_data.hex()}")
    log(f"[DEBUG] Received CRC: {received_crc.hex()}")
    log(f"[DEBUG] Expected CRC (LE): {expected_crc_le.hex()}")
    log(f"[DEBUG] Expected CRC (BE): {expected_crc_be.hex()}")
    log(f"[DEBUG] Expected CRC (GT06): {expected_crc_gt06.hex()}")
    
    # Verificar si coincide con alguna variante
    if received_crc == expected_crc_le:
        log("[DEBUG] CRC coincide con little-endian")
        return True
    elif received_crc == expected_crc_be:
        log("[DEBUG] CRC coincide con big-endian")
        return True
    elif received_crc == expected_crc_gt06:
        log("[DEBUG] CRC coincide con algoritmo GT06 correcto")
        return True
    else:
        log("[DEBUG] CRC no coincide con ninguna variante")
        return False

def handle_login(data, conn_data=None):
    try:
        # Estructura del paquete de login: 7878 + length + 01 + IMEI(8) + serial(2) + error_check(2) + CRC16(2) + 0D0A
        if len(data) < 18:  # Longitud mínima del paquete de login (18 bytes para paquetes reales)
            log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return None
        
        # Validar CRC del paquete recibido (permitir CRC diferente para dispositivos reales)
        received_crc = data[-4:-2]  # CRC recibido del paquete de login
        packet_data = data[2:-4]    # Datos del paquete para calcular CRC
        
        # Calcular diferentes variantes del CRC para el paquete de login
        expected_crc_le = crc16(packet_data)
        expected_crc_be = crc16_big_endian(packet_data)
        expected_crc_gt06 = crc16_gt06_correct(packet_data)
        
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de login no coincide, pero continuando...")
            # No retornar None, continuar procesando de todas formas
            
        # Extraer IMEI - puede estar en diferentes posiciones según el dispositivo
        if len(data) >= 12:
            imei = data[4:12].hex()  # IMEI está en bytes 4-11
            log(f"[LOGIN] IMEI: {imei}")
        else:
            log(f"[ERROR] No se puede extraer IMEI del paquete de {len(data)} bytes")
            return None
        
        # Extraer serial - puede estar en diferentes posiciones
        if len(data) >= 14:
            serial = data[12:14]  # Serial está en bytes 12-13
            log(f"[LOGIN] Serial: {serial.hex()}")
            
            # Guardar el serial en los datos de conexión para posible reintento
            if conn_data is not None:
                conn_data['login_serial'] = serial
                log(f"[DEBUG] Serial guardado en datos de conexión: {serial.hex()}")
            else:
                log(f"[DEBUG] No hay datos de conexión para guardar serial")
        else:
            # Si no hay serial, usar uno por defecto
            serial = b'\x00\x01'
            log(f"[LOGIN] Serial no encontrado, usando por defecto: {serial.hex()}")
            if conn_data is not None:
                conn_data['login_serial'] = serial
                log(f"[DEBUG] Serial por defecto guardado en datos de conexión: {serial.hex()}")
            else:
                log(f"[DEBUG] No hay datos de conexión para guardar serial por defecto")
        
        # Construir ACK: 7878 + 05 + 01 + serial + CRC16 + 0D0A
        # El ACK debe ser: 7878 + 05 + 01 + serial + CRC16 + 0D0A
        ack_data = b'\x05\x01' + serial  # Datos para calcular CRC (sin 7878)
        
        # Probar diferentes algoritmos de CRC para el ACK
        crc_le = crc16(ack_data)
        crc_be = crc16_big_endian(ack_data)
        crc_gt06 = crc16_gt06_correct(ack_data)
        
        log(f"[DEBUG] ACK data: {ack_data.hex()}")
        log(f"[DEBUG] ACK CRC (LE): {crc_le.hex()}")
        log(f"[DEBUG] ACK CRC (BE): {crc_be.hex()}")
        log(f"[DEBUG] ACK CRC (GT06): {crc_gt06.hex()}")
        
        # Intentar usar el mismo algoritmo que coincidió con el paquete de login
        if received_crc == expected_crc_le:
            checksum = crc_le
            log("[DEBUG] Usando CRC little-endian para ACK")
        elif received_crc == expected_crc_be:
            checksum = crc_be
            log("[DEBUG] Usando CRC big-endian para ACK")
        elif received_crc == expected_crc_gt06:
            checksum = crc_gt06
            log("[DEBUG] Usando CRC GT06 para ACK")
        else:
            # Si ninguno coincide, probar con little-endian (más común)
            checksum = crc_le
            log("[DEBUG] Ningún CRC coincide, usando little-endian para ACK")
        
        ack = b'\x78\x78' + ack_data + checksum + b'\x0D\x0A'
        log_sent(ack)
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error en handle_login: {e}")
        import traceback
        log(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None

def parse_position(data):
    try:
        # Estructura del paquete de posición: puede variar según el dispositivo
        log(f"[DEBUG] Longitud del paquete de posición: {len(data)} bytes")
        log(f"[DEBUG] Paquete completo: {data.hex()}")
        
        if len(data) < 20:  # Longitud mínima más flexible para paquetes reales
            log(f"[ERROR] Paquete de posición demasiado corto: {len(data)} bytes")
            return
            
        # Intentar extraer campos según diferentes estructuras posibles
        try:
            # Estructura básica: 7878 + length + 12 + date(6) + quantity(1) + lat(4) + lon(4) + speed(1) + course(2) + ...
            if len(data) >= 25:
                date_bytes = data[4:10]  # Fecha/hora en BCD
                quantity = data[10]      # Cantidad de posiciones
                lat_raw = data[11:15]    # Latitud
                lon_raw = data[15:19]    # Longitud
                speed = data[19]         # Velocidad
                course = int.from_bytes(data[20:22], byteorder='big')  # Rumbo
                
                log(f"[DEBUG] Date: {date_bytes.hex()}, Quantity: {quantity}, Speed: {speed}, Course: {course}")
                log(f"[DEBUG] Lat raw: {lat_raw.hex()}, Lon raw: {lon_raw.hex()}")
                
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

                log(f"[POSICION] LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}°")
                
                # Intentar extraer información adicional si está disponible
                if len(data) >= 23:
                    status = data[22] if len(data) > 22 else 0
                    log(f"[INFO] Status: {status}")
                    
                if len(data) >= 25:
                    serial = int.from_bytes(data[23:25], byteorder='big')
                    log(f"[INFO] Serial: {serial}")
                    
            else:
                log(f"[WARNING] Paquete de posición muy corto para extraer todos los campos")
                return
                
        except IndexError as e:
            log(f"[ERROR] Error de índice al parsear posición: {e}")
            return

    except ValueError as e:
        log(f"[ERROR] Error de valor al parsear posición: {e}")
    except Exception as e:
        log(f"[ERROR] Error inesperado parseando datos de posicion: {e}")

def main():
    log(f"Servidor iniciado en {HOST}:{PORT}")
    
    # Diccionario para almacenar datos de conexiones
    connection_data = {}
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"Conexion entrante desde {addr}")
                    
                    # Inicializar datos de esta conexión
                    connection_data[conn] = {
                        'login_serial': None, 
                        'retry_sent': False,
                        'ack_success': False,
                        'ack_attempts': 0,
                        'current_ack_type': None,
                        'connection_closed': False,
                        'retry_thread': None
                    }
                    
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
                                expected_length = packet_length + 6  # 7878 + length + data + crc + 0D0A
                                
                                # Para paquetes reales, ser más flexible con la longitud
                                if len(data) < expected_length - 1:  # Permitir 1 byte de diferencia
                                    log(f"[WARNING] Paquete posiblemente incompleto. Esperado: {expected_length}, Recibido: {len(data)}")
                                    # Continuar procesando de todas formas
                                elif len(data) > expected_length + 2:  # Permitir hasta 2 bytes extra
                                    log(f"[WARNING] Paquete más largo de lo esperado. Esperado: {expected_length}, Recibido: {len(data)}")
                                    # Continuar procesando de todas formas
                            
                            tipo_paquete = data[3]

                            if tipo_paquete == 0x01:  # Login
                                respuesta = handle_login(data, connection_data[conn])
                                if respuesta is not None:
                                    conn.sendall(respuesta)
                                    # Iniciar sistema automático de reintentos
                                    conn_data = connection_data[conn]
                                    if conn_data['login_serial'] is not None:
                                        log(f"[AUTO_RETRY] Iniciando sistema automático de reintentos para serial: {conn_data['login_serial'].hex()}")
                                        auto_retry_ack(conn_data['login_serial'], conn, conn_data)
                                else:
                                    log("[ERROR] No se pudo procesar el login")
                            elif tipo_paquete == 0x12:  # Posición
                                log(f"[SUCCESS] ¡ACK exitoso! GPS envió paquete de posición (0x12)")
                                conn_data = connection_data[conn]
                                conn_data['ack_success'] = True
                                if conn_data.get('current_ack_type'):
                                    log(f"[SUCCESS] ACK tipo '{conn_data['current_ack_type']}' funcionó correctamente")
                                parse_position(data)
                            elif tipo_paquete == 0x13:  # Estado del terminal
                                log(f"[STATUS] Paquete de estado recibido (0x13) - ACK aún no reconocido")
                                # El sistema automático ya está probando diferentes ACKs
                                conn_data = connection_data[conn]
                                if conn_data.get('ack_attempts', 0) > 0:
                                    log(f"[STATUS] Ya se han probado {conn_data['ack_attempts']} tipos de ACK")
                                else:
                                    log(f"[STATUS] Sistema automático de reintentos en progreso...")
                            else:
                                log(f"[WARNING] Tipo de paquete no reconocido: 0x{tipo_paquete:02X}")
                        else:
                            log("[ERROR] Paquete no comienza con cabecera 7878")
                    
                    # Limpiar datos de conexión al cerrar
                    if conn in connection_data:
                        conn_data = connection_data[conn]
                        conn_data['connection_closed'] = True
                        log(f"[INFO] Conexión cerrada, limpiando datos")
                        del connection_data[conn]
                        
            except socket.error as e:
                log(f"[ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    # Probar CRC del ejemplo del manual
    print("=== PRUEBA CRC DEL MANUAL ===")
    crc_type = test_crc_example()
    print(f"Tipo de CRC correcto: {crc_type}")
    print("=============================")
    print()
    
    main()
