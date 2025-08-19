import socket
import datetime
import time
import threading

HOST = '200.58.98.187'
PORT = 5003
pp = 4994

LOG_FILE = "datosChino.txt"

# Comando para configurar el dispositivo en modo de transmisión directa (sin login)
# Ajusta este valor según el manual de tu fabricante si difiere
DIRECT_MODE_COMMAND = b"MODE,1#"

# Tabla CRC-ITU del fabricante (CRC-CCITT)
CRC_TAB16 = [
    0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF,
    0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
    0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E,
    0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
    0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD,
    0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
    0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C,
    0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
    0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB,
    0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
    0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A,
    0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
    0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9,
    0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
    0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738,
    0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
    0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7,
    0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
    0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036,
    0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
    0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5,
    0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
    0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134,
    0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
    0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3,
    0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
    0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232,
    0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
    0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1,
    0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
    0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330,
    0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78,
]

def crc16_itu_factory(data):
    """
    Implementación exacta del algoritmo CRC-ITU del fabricante
    Basado en el código C del manual
    """
    fcs = 0xFFFF  # Inicialización
    for byte in data:
        fcs = (fcs >> 8) ^ CRC_TAB16[(fcs ^ byte) & 0xFF]
    return ~fcs & 0xFFFF  # Negado y máscara de 16 bits

def crc16_itu_factory_bytes(data):
    """
    Retorna el CRC en formato bytes (little-endian)
    """
    crc = crc16_itu_factory(data)
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_itu_factory_bytes_be(data):
    """
    Retorna el CRC en formato bytes (big-endian)
    """
    crc = crc16_itu_factory(data)
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def test_crc_example():
    """
    Prueba el CRC del ejemplo del manual
    """
    # Datos del ACK del ejemplo: 05 01 00 02
    ack_data = b'\x05\x01\x00\x02'
    expected_crc = b'\xEB\x47'  # CRC del ejemplo
    
    crc_itu_le = crc16_itu_factory_bytes(ack_data)
    crc_itu_be = crc16_itu_factory_bytes_be(ack_data)
    
    print(f"ACK data: {ack_data.hex()}")
    print(f"Expected CRC: {expected_crc.hex()}")
    print(f"Calculated CRC (ITU LE): {crc_itu_le.hex()}")
    print(f"Calculated CRC (ITU BE): {crc_itu_be.hex()}")
    
    if crc_itu_le == expected_crc:
        print("✓ CRC coincide con algoritmo CRC-ITU del fabricante (LE)")
        return 'itu_le'
    elif crc_itu_be == expected_crc:
        print("✓ CRC coincide con algoritmo CRC-ITU del fabricante (BE)")
        return 'itu_be'
    else:
        print("✗ CRC no coincide con ninguna variante del fabricante")
        return 'none'

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def send_alternative_ack(serial, conn, ack_type='itu_le'):
    """
    Envía un ACK con CRC-ITU del fabricante
    """
    ack_data = b'\x04\x01' + serial
    
    if ack_type == 'itu_le':
        # CRC-ITU del fabricante (Little-Endian)
        crc = crc16_itu_factory_bytes(ack_data)
        log(f"[ACK_ITU_LE] Enviando ACK con CRC-ITU del fabricante (LE): {ack_data.hex()}, CRC: {crc.hex()}")
    elif ack_type == 'itu_be':
        # CRC-ITU del fabricante (Big-Endian)
        crc = crc16_itu_factory_bytes_be(ack_data)
        log(f"[ACK_ITU_BE] Enviando ACK con CRC-ITU del fabricante (BE): {ack_data.hex()}, CRC: {crc.hex()}")
    else:
        log(f"[ERROR] Tipo de ACK no reconocido: {ack_type}")
        return
    
    ack = b'\x78\x78' + ack_data + crc + b'\x0D\x0A'
    conn.sendall(ack)
    log_sent(ack)

def build_server_command_packet(command_ascii: bytes, serial: bytes, crc_variant: str = 'itu_be') -> bytes:
    """
    Construye un paquete de comando hacia el dispositivo (protocolo 0x80) con framing 0x7878.
    command_ascii: Contenido ASCII del comando, por ejemplo b"MODE,1#".
    serial: Número de serie de 2 bytes.
    crc_variant: 'itu_le' o 'itu_be'.
    """
    protocol_no = 0x80
    if not isinstance(command_ascii, (bytes, bytearray)):
        raise ValueError("command_ascii debe ser bytes")
    if not isinstance(serial, (bytes, bytearray)) or len(serial) != 2:
        raise ValueError("serial debe ser bytes de longitud 2")

    # length = protocolo(1) + contenido(len) + serial(2)
    body = bytes([1 + len(command_ascii) + 2, protocol_no]) + command_ascii + serial

    if crc_variant == 'itu_le':
        crc = crc16_itu_factory_bytes(body)
    else:
        crc = crc16_itu_factory_bytes_be(body)

    return b"\x78\x78" + body + crc + b"\x0D\x0A"

def send_direct_mode_command(conn, conn_data: dict):
    """
    Envía el comando para configurar el equipo en modo directo (sin login) usando 0x80.
    Elige automáticamente la variante de CRC a partir de lo observado en el login.
    """
    try:
        if conn_data is None:
            log("[CMD] No hay datos de conexión para enviar comando de modo directo")
            return

        if conn_data.get('direct_cfg_sent'):
            return

        serial = conn_data.get('login_serial') or b"\x00\x01"
        crc_variant = conn_data.get('login_ack_type') or 'itu_be'

        packet = build_server_command_packet(DIRECT_MODE_COMMAND, serial, crc_variant)
        log(f"[CMD] Enviando comando de modo directo ({crc_variant}): {packet.hex()}")
        conn.sendall(packet)
        log_sent(packet)
        conn_data['direct_cfg_sent'] = True
    except Exception as e:
        log(f"[ERROR] Error enviando comando de modo directo: {e}")

def send_position_request(conn, conn_data: dict):
    """
    Envía un comando para solicitar posición específicamente
    """
    try:
        if conn_data is None:
            log("[CMD] No hay datos de conexión para enviar solicitud de posición")
            return

        if conn_data.get('position_request_sent'):
            return

        serial = conn_data.get('login_serial') or b"\x00\x01"
        crc_variant = conn_data.get('login_ack_type') or 'itu_be'

        # Comando para solicitar posición (ajustar según el fabricante)
        position_command = b"POSITION#"
        
        packet = build_server_command_packet(position_command, serial, crc_variant)
        log(f"[CMD] Enviando solicitud de posición ({crc_variant}): {packet.hex()}")
        conn.sendall(packet)
        log_sent(packet)
        conn_data['position_request_sent'] = True
    except Exception as e:
        log(f"[ERROR] Error enviando solicitud de posición: {e}")

def auto_retry_ack(serial, conn, conn_data):
    """
    Sistema automático de reintentos de ACK
    Prueba solo las dos versiones del CRC-ITU del fabricante
    """
    def retry_thread():
        # Usar el mismo tipo de ACK que funcionó para el login, o probar ambos si no se sabe
        login_ack_type = conn_data.get('login_ack_type')
        if login_ack_type:
            # Si sabemos qué tipo funcionó para el login, usar ese primero
            ack_types = [login_ack_type]
            log(f"[AUTO_RETRY] Usando el mismo tipo de ACK que funcionó para el login: {login_ack_type}")
        else:
            # Si no sabemos, probar ambos
            ack_types = ['itu_le', 'itu_be']
            log(f"[AUTO_RETRY] Probando ambos tipos de ACK del fabricante")
        
        current_ack = 0
        max_retries_per_type = 3  # Máximo 3 intentos por tipo de ACK
        
        # Esperar 2 segundos antes del primer reintento
        time.sleep(2)
        
        while current_ack < len(ack_types) and not conn_data.get('ack_success', False):
            if conn_data.get('connection_closed', False):
                break
                
            ack_type = ack_types[current_ack]
            
            # Probar múltiples veces el mismo tipo de ACK
            for retry in range(max_retries_per_type):
                if conn_data.get('ack_success', False):
                    break
                    
                log(f"[AUTO_RETRY] Intento {current_ack + 1}/{len(ack_types)} (retry {retry + 1}/{max_retries_per_type}): Probando ACK tipo '{ack_type}'")
                
                try:
                    send_alternative_ack(serial, conn, ack_type)
                    conn_data['current_ack_type'] = ack_type
                    conn_data['ack_attempts'] = conn_data.get('ack_attempts', 0) + 1
                    
                    # Esperar 2 segundos antes del siguiente intento del mismo tipo
                    time.sleep(2)
                    
                except Exception as e:
                    log(f"[ERROR] Error en auto_retry_ack: {e}")
                    break
            
            # Pasar al siguiente tipo de ACK
            current_ack += 1
        
        if not conn_data.get('ack_success', False):
            total_attempts = len(ack_types) * max_retries_per_type
            log(f"[AUTO_RETRY] Completados {total_attempts} intentos sin éxito")
        else:
            log(f"[AUTO_RETRY] ACK exitoso después de {conn_data.get('ack_attempts', 0)} intentos")
    
    # Iniciar thread de reintentos
    retry_thread = threading.Thread(target=retry_thread, daemon=True)
    retry_thread.start()
    conn_data['retry_thread'] = retry_thread

def validate_packet_crc(data):
    """
    Valida el CRC16 de un paquete recibido usando solo CRC-ITU del fabricante
    """
    if len(data) < 6:  # Mínimo: 7878 + length + data + CRC16 + 0D0A
        return False
    
    # Extraer datos para calcular CRC (desde length hasta antes del CRC)
    packet_data = data[2:-4]  # Sin 7878 y sin CRC16 + 0D0A
    received_crc = data[-4:-2]  # CRC recibido
    
    # Calcular solo las dos versiones del CRC-ITU del fabricante
    expected_crc_itu_le = crc16_itu_factory_bytes(packet_data)  # CRC-ITU LE
    expected_crc_itu_be = crc16_itu_factory_bytes_be(packet_data)  # CRC-ITU BE
    
    log(f"[DEBUG] Packet data: {packet_data.hex()}")
    log(f"[DEBUG] Received CRC: {received_crc.hex()}")
    log(f"[DEBUG] Expected CRC (ITU LE): {expected_crc_itu_le.hex()}")
    log(f"[DEBUG] Expected CRC (ITU BE): {expected_crc_itu_be.hex()}")
    
    # Verificar si coincide con alguna variante del fabricante
    if received_crc == expected_crc_itu_le:
        log("[DEBUG] CRC coincide con algoritmo CRC-ITU del fabricante (LE)")
        return True
    elif received_crc == expected_crc_itu_be:
        log("[DEBUG] CRC coincide con algoritmo CRC-ITU del fabricante (BE)")
        return True
    else:
        log("[DEBUG] CRC no coincide con ninguna variante del fabricante")
        return False

def handle_login(data, conn_data=None):
    try:
        # Estructura del paquete de login: 7878 + length + 01 + IMEI(8) + serial(2) + error_check(2) + CRC16(2) + 0D0A
        if len(data) < 18:  # Longitud mínima del paquete de login (18 bytes para paquetes reales)
            log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return None
        
        # Validar CRC del paquete recibido usando solo CRC-ITU del fabricante
        received_crc = data[-4:-2]  # CRC recibido del paquete de login
        packet_data = data[2:-4]    # Datos del paquete para calcular CRC
        
        # Calcular solo las dos versiones del CRC-ITU del fabricante
        expected_crc_itu_le = crc16_itu_factory_bytes(packet_data)
        expected_crc_itu_be = crc16_itu_factory_bytes_be(packet_data)
        
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de login no coincide con variantes del fabricante, pero continuando...")
            
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
        
        # Construir ACK: 7878 + 04 + 01 + serial + CRC16 + 0D0A
        ack_data = b'\x04\x01' + serial  # Datos para calcular CRC (sin 7878)
        
        # Calcular solo las dos versiones del CRC-ITU del fabricante
        crc_itu_le = crc16_itu_factory_bytes(ack_data)
        crc_itu_be = crc16_itu_factory_bytes_be(ack_data)
        
        log(f"[DEBUG] ACK data: {ack_data.hex()}")
        log(f"[DEBUG] ACK CRC (ITU LE): {crc_itu_le.hex()}")
        log(f"[DEBUG] ACK CRC (ITU BE): {crc_itu_be.hex()}")
        
        # Intentar usar el mismo algoritmo que coincidió con el paquete de login
        if received_crc == expected_crc_itu_le:
            checksum = crc_itu_le
            log("[DEBUG] Usando CRC-ITU del fabricante (LE) para ACK")
            # Guardar el tipo de ACK que funcionó para el login
            if conn_data is not None:
                conn_data['login_ack_type'] = 'itu_le'
        elif received_crc == expected_crc_itu_be:
            checksum = crc_itu_be
            log("[DEBUG] Usando CRC-ITU del fabricante (BE) para ACK")
            # Guardar el tipo de ACK que funcionó para el login
            if conn_data is not None:
                conn_data['login_ack_type'] = 'itu_be'
        else:
            # Si ninguno coincide, usar CRC-ITU del fabricante (LE) como primera opción
            checksum = crc_itu_le
            log("[DEBUG] Ningún CRC coincide, usando CRC-ITU del fabricante (LE) para ACK")
            if conn_data is not None:
                conn_data['login_ack_type'] = 'itu_le'
        
        ack = b'\x78\x78' + ack_data + checksum + b'\x0D\x0A'
        log_sent(ack)
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error en handle_login: {e}")
        import traceback
        log(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None

def handle_position_direct(data, conn_data=None):
    """
    Maneja paquetes de posición que llegan directamente sin login previo
    (Modo de transmisión continua)
    """
    try:
        log(f"[POSICION_DIRECTA] Dispositivo enviando posición sin login previo")
        
        # Validar CRC del paquete de posición
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de posición no coincide, pero continuando...")
        
        # Extraer información del paquete de posición
        parse_position(data)
        
        # Enviar ACK de confirmación
        # Para posición directa, usar serial por defecto o extraer del paquete
        if len(data) >= 25:
            # Intentar extraer serial del paquete de posición
            serial = data[23:25]  # Serial en posición 23-24
            log(f"[POSICION_DIRECTA] Serial extraído del paquete: {serial.hex()}")
        else:
            # Usar serial por defecto
            serial = b'\x00\x01'
            log(f"[POSICION_DIRECTA] Usando serial por defecto: {serial.hex()}")
        
        # Construir ACK: 7878 + 04 + 01 + serial + CRC16 + 0D0A
        ack_data = b'\x04\x01' + serial
        
        # Usar CRC-ITU del fabricante (BE) como primera opción para posición directa
        crc_itu_be = crc16_itu_factory_bytes_be(ack_data)
        ack = b'\x78\x78' + ack_data + crc_itu_be + b'\x0D\x0A'
        
        log(f"[POSICION_DIRECTA] Enviando ACK: {ack.hex()}")
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error en handle_position_direct: {e}")
        return None

def handle_heartbeat_direct(data, conn_data=None):
    """
    Maneja paquetes de heartbeat que llegan directamente sin login previo
    """
    try:
        log(f"[HEARTBEAT_DIRECTA] Dispositivo enviando heartbeat sin login previo")
        
        # Validar CRC del paquete de heartbeat
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de heartbeat no coincide, pero continuando...")
        
        # Parsear información del heartbeat si es posible
        try:
            if len(data) >= 8:
                heartbeat_info = data[4:-4]  # Sin cabecera y sin CRC
                log(f"[HEARTBEAT_DIRECTA] Información: {heartbeat_info.hex()}")
        except Exception as e:
            log(f"[ERROR] Error parseando heartbeat: {e}")
        
        # Enviar ACK de confirmación
        serial = b'\x00\x01'  # Serial por defecto
        ack_data = b'\x04\x01' + serial
        crc_itu_be = crc16_itu_factory_bytes_be(ack_data)
        ack = b'\x78\x78' + ack_data + crc_itu_be + b'\x0D\x0A'
        
        log(f"[HEARTBEAT_DIRECTA] Enviando ACK: {ack.hex()}")
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error en handle_heartbeat_direct: {e}")
        return None

def handle_alarm_direct(data, conn_data=None):
    """
    Maneja paquetes de alarma que llegan directamente sin login previo
    """
    try:
        log(f"[ALARMA_DIRECTA] Dispositivo enviando alarma sin login previo")
        
        # Validar CRC del paquete de alarma
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de alarma no coincide, pero continuando...")
        
        # Parsear información de la alarma
        try:
            if len(data) >= 8:
                alarm_info = data[4:-4]  # Sin cabecera y sin CRC
                log(f"[ALARMA_DIRECTA] Información de alarma: {alarm_info.hex()}")
                
                # Determinar tipo de alarma
                if len(alarm_info) >= 1:
                    alarm_type = alarm_info[0]
                    alarm_types = {
                        0x01: "SOS",
                        0x02: "Batería baja", 
                        0x03: "Movimiento",
                        0x04: "Geocerca",
                        0x05: "Impacto"
                    }
                    alarm_name = alarm_types.get(alarm_type, f"Desconocida (0x{alarm_type:02X})")
                    log(f"[ALARMA_DIRECTA] Tipo de alarma: {alarm_name}")
        except Exception as e:
            log(f"[ERROR] Error parseando alarma: {e}")
        
        # Enviar ACK de confirmación
        serial = b'\x00\x01'  # Serial por defecto
        ack_data = b'\x04\x01' + serial
        crc_itu_be = crc16_itu_factory_bytes_be(ack_data)
        ack = b'\x78\x78' + ack_data + crc_itu_be + b'\x0D\x0A'
        
        log(f"[ALARMA_DIRECTA] Enviando ACK: {ack.hex()}")
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error in handle_alarm_direct: {e}")
        return None

def detect_transmission_mode(data):
    """
    Detecta si el dispositivo está en modo de transmisión continua
    (envía datos directamente sin login previo)
    """
    if len(data) < 4:
        return False
    
    # Verificar si es un paquete de posición directa (0x12)
    if data[3] == 0x12:
        return True
    
    # Verificar si es un paquete de heartbeat directo (0x23)
    if data[3] == 0x23:
        return True
    
    # Verificar si es un paquete de alarma directa (0x26)
    if data[3] == 0x26:
        return True
    
    return False

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
                        'retry_thread': None,
                        'transmission_mode': None,  # 'login' o 'direct'
                        'first_packet': True
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
                            conn_data = connection_data[conn]
                            
                            # Detectar modo de transmisión en el primer paquete
                            if conn_data['first_packet']:
                                if tipo_paquete == 0x01:
                                    conn_data['transmission_mode'] = 'login'
                                    log(f"[MODO] Dispositivo en modo login (0x01)")
                                elif detect_transmission_mode(data):
                                    conn_data['transmission_mode'] = 'direct'
                                    log(f"[MODO] Dispositivo en modo transmisión continua (0x{tipo_paquete:02X})")
                                else:
                                    conn_data['transmission_mode'] = 'unknown'
                                    log(f"[MODO] Modo de transmisión desconocido (0x{tipo_paquete:02X})")
                                conn_data['first_packet'] = False

                            if tipo_paquete == 0x01:  # Login
                                 respuesta = handle_login(data, connection_data[conn])
                                 if respuesta is not None:
                                     conn.sendall(respuesta)
                                     # Marcar login como completado
                                     conn_data = connection_data[conn]
                                     conn_data['login_completed'] = True
                                     
                                     # Iniciar sistema automático de reintentos
                                     if conn_data['login_serial'] is not None:
                                         log(f"[AUTO_RETRY] Iniciando sistema automático de reintentos para serial: {conn_data['login_serial'].hex()}")
                                         auto_retry_ack(conn_data['login_serial'], conn, conn_data)
                                     
                                     # Enviar comando para modo directo (solo una vez)
                                     send_direct_mode_command(conn, conn_data)
                                     
                                     # Enviar solicitud de posición después de un delay
                                     import threading
                                     def delayed_position_request():
                                         import time
                                         time.sleep(5)  # Esperar 5 segundos
                                         send_position_request(conn, conn_data)
                                     
                                     position_thread = threading.Thread(target=delayed_position_request, daemon=True)
                                     position_thread.start()
                                 else:
                                     log("[ERROR] No se pudo procesar el login")
                            elif tipo_paquete == 0x12 and conn_data['transmission_mode'] == 'direct':  # Posición directa
                                respuesta = handle_position_direct(data, conn_data)
                                if respuesta is not None:
                                    conn.sendall(respuesta)
                                    log(f"[SUCCESS] ACK enviado para posición directa")
                                else:
                                    log("[ERROR] No se pudo procesar la posición directa")
                            elif tipo_paquete == 0x23 and conn_data['transmission_mode'] == 'direct':  # Heartbeat directo
                                respuesta = handle_heartbeat_direct(data, conn_data)
                                if respuesta is not None:
                                    conn.sendall(respuesta)
                                    log(f"[SUCCESS] ACK enviado para heartbeat directo")
                                else:
                                    log("[ERROR] No se pudo procesar el heartbeat directo")
                            elif tipo_paquete == 0x26 and conn_data['transmission_mode'] == 'direct':  # Alarma directa
                                respuesta = handle_alarm_direct(data, conn_data)
                                if respuesta is not None:
                                    conn.sendall(respuesta)
                                    log(f"[SUCCESS] ACK enviado para alarma directa")
                                else:
                                    log("[ERROR] No se pudo procesar la alarma directa")
                            elif tipo_paquete == 0x12:  # Posición
                                log(f"[SUCCESS] ¡ACK exitoso! GPS envió paquete de posición (0x12)")
                                conn_data = connection_data[conn]
                                conn_data['ack_success'] = True
                                if conn_data.get('current_ack_type'):
                                    log(f"[SUCCESS] ACK tipo '{conn_data['current_ack_type']}' funcionó correctamente")
                                parse_position(data)
                            elif tipo_paquete == 0x13:  # Estado del terminal
                                 log(f"[STATUS] Paquete de estado recibido (0x13) - ACK aún no reconocido")
                                 conn_data = connection_data[conn]
                                 
                                 # Parsear información del estado si es posible
                                 try:
                                     if len(data) >= 8:
                                         status_info = data[4:-4]  # Sin cabecera y sin CRC
                                         log(f"[STATUS] Información de estado: {status_info.hex()}")
                                         
                                         # Intentar extraer serial del estado
                                         if len(status_info) >= 7:
                                             status_serial = status_info[-2:]  # Últimos 2 bytes
                                             log(f"[STATUS] Serial del estado: {status_serial.hex()}")
                                             
                                             # Enviar ACK específico para el estado
                                             ack_data = b'\x04\x01' + status_serial
                                             crc_be = crc16_itu_factory_bytes_be(ack_data)
                                             ack = b'\x78\x78' + ack_data + crc_be + b'\x0D\x0A'
                                             conn.sendall(ack)
                                             log(f"[STATUS] ACK enviado para estado: {ack.hex()}")
                                 except Exception as e:
                                     log(f"[ERROR] Error parseando estado: {e}")
                            elif tipo_paquete == 0x23:  # Heartbeat
                                log(f"[HEARTBEAT] Paquete de heartbeat recibido (0x23) - ACK aún no reconocido")
                                conn_data = connection_data[conn]
                                if conn_data.get('ack_attempts', 0) > 0:
                                    log(f"[HEARTBEAT] Dispositivo responde pero ACK no confirmado")
                            elif tipo_paquete == 0x26:  # Alarma
                                log(f"[ALARMA] Paquete de alarma recibido (0x26) - ACK aún no reconocido")
                                # Parsear información de alarma si es posible
                                try:
                                    if len(data) >= 8:
                                        alarm_info = data[4:-4]  # Sin cabecera y sin CRC
                                        log(f"[ALARMA] Información de alarma: {alarm_info.hex()}")
                                except Exception as e:
                                    log(f"[ERROR] Error parseando alarma: {e}")
                            else:
                                log(f"[WARNING] Tipo de paquete no reconocido: 0x{tipo_paquete:02X} - ACK aún no reconocido")
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
