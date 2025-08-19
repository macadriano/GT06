#!/usr/bin/env python3
"""
Servidor GT06 corregido con formato de ACK según especificaciones del fabricante
"""

import socket
import datetime
import time
import threading

HOST = '200.58.98.187'
PORT = 4997  # Puerto diferente para pruebas

LOG_FILE = "datosChino_corrected.txt"

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
    """CRC-ITU del fabricante"""
    fcs = 0xFFFF
    for byte in data:
        fcs = (fcs >> 8) ^ CRC_TAB16[(fcs ^ byte) & 0xFF]
    return ~fcs & 0xFFFF

def crc16_itu_factory_bytes_be(data):
    """CRC en formato bytes (big-endian)"""
    crc = crc16_itu_factory(data)
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def send_correct_ack(serial, conn):
    """
    Envía el ACK correcto según especificaciones GT06
    Formato: 7878 + 05 + 01 + serial + CRC + 0D0A
    """
    # ACK data: length(05) + protocol(01) + serial(2 bytes)
    ack_data = b'\x05\x01' + serial
    
    # Calcular CRC sobre ack_data
    crc = crc16_itu_factory_bytes_be(ack_data)
    
    # Construir ACK completo
    ack = b'\x78\x78' + ack_data + crc + b'\x0D\x0A'
    
    log(f"[ACK] Enviando ACK correcto: {ack.hex()}")
    log(f"[ACK] ACK data: {ack_data.hex()}")
    log(f"[ACK] CRC: {crc.hex()}")
    log(f"[ACK] Longitud total: {len(ack)} bytes")
    
    conn.sendall(ack)
    log_sent(ack)
    return ack

def validate_packet_crc(data):
    """
    Valida el CRC16 de un paquete recibido
    """
    if len(data) < 6:
        return False
    
    # Extraer datos para calcular CRC (desde length hasta antes del CRC)
    packet_data = data[2:-4]  # Sin 7878 y sin CRC16 + 0D0A
    received_crc = data[-4:-2]  # CRC recibido
    
    # Calcular CRC esperado
    expected_crc = crc16_itu_factory_bytes_be(packet_data)
    
    log(f"[CRC] Packet data: {packet_data.hex()}")
    log(f"[CRC] Received CRC: {received_crc.hex()}")
    log(f"[CRC] Expected CRC: {expected_crc.hex()}")
    
    return received_crc == expected_crc

def handle_login_corrected(data, conn):
    """
    Maneja el login con ACK correcto según especificaciones
    """
    try:
        log(f"[LOGIN] === PROCESANDO LOGIN ===")
        
        if len(data) < 18:
            log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return None
        
        # Validar CRC del paquete recibido
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de login no coincide, pero continuando...")
        
        # Extraer IMEI y serial
        imei = data[4:12].hex()
        serial = data[12:14]
        
        log(f"[LOGIN] IMEI: {imei}")
        log(f"[LOGIN] Serial: {serial.hex()}")
        
        # Enviar ACK correcto según especificaciones
        ack = send_correct_ack(serial, conn)
        
        return ack
        
    except Exception as e:
        log(f"[ERROR] Error en handle_login_corrected: {e}")
        return None

def parse_position_corrected(data):
    """
    Parseo de posición con validación mejorada
    """
    try:
        log(f"[POSITION] === PROCESANDO POSICIÓN ===")
        log(f"[POSITION] Longitud del paquete: {len(data)} bytes")
        log(f"[POSITION] Paquete completo: {data.hex()}")
        
        if len(data) < 25:
            log(f"[ERROR] Paquete de posición demasiado corto: {len(data)} bytes")
            return False
        
        # Validar CRC del paquete de posición
        if not validate_packet_crc(data):
            log("[WARNING] CRC del paquete de posición no coincide, pero continuando...")
        
        # Extraer campos según estructura GT06
        date_bytes = data[4:10]  # Fecha/hora en BCD
        quantity = data[10]      # Cantidad de posiciones
        lat_raw = data[11:15]    # Latitud
        lon_raw = data[15:19]    # Longitud
        speed = data[19]         # Velocidad
        course = int.from_bytes(data[20:22], byteorder='big')  # Rumbo
        
        log(f"[POSITION] Date: {date_bytes.hex()}, Quantity: {quantity}")
        log(f"[POSITION] Lat raw: {lat_raw.hex()}, Lon raw: {lon_raw.hex()}")
        log(f"[POSITION] Speed: {speed}, Course: {course}")
        
        # Validar que las coordenadas no sean cero
        if lat_raw == b'\x00\x00\x00\x00' or lon_raw == b'\x00\x00\x00\x00':
            log("[WARNING] Coordenadas GPS en cero - posible falta de señal")
            return False
        
        # Convertir coordenadas
        lat_val = int.from_bytes(lat_raw, byteorder='big')
        lon_val = int.from_bytes(lon_raw, byteorder='big')
        
        lat = (lat_val & 0x7FFFFFFF) / 1800000.0
        lon = (lon_val & 0x7FFFFFFF) / 1800000.0
        
        if lat_val & 0x80000000:  # Bit 31 = 1 significa latitud sur
            lat = -lat
        if lon_val & 0x80000000:  # Bit 31 = 1 significa longitud oeste
            lon = -lon
        
        # Validar rangos de coordenadas
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            log(f"[ERROR] Coordenadas fuera de rango: LAT={lat}, LON={lon}")
            return False
        
        log(f"[POSITION] ✓ LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}°")
        
        # Extraer información adicional si está disponible
        if len(data) >= 23:
            status = data[22]
            log(f"[POSITION] Status: {status}")
        
        if len(data) >= 25:
            serial = int.from_bytes(data[23:25], byteorder='big')
            log(f"[POSITION] Serial: {serial}")
        
        return True
        
    except Exception as e:
        log(f"[ERROR] Error en parse_position_corrected: {e}")
        return False

def main():
    log(f"[CORRECTED] Servidor GT06 corregido iniciado en {HOST}:{PORT}")
    log(f"[CORRECTED] Usando formato de ACK correcto según especificaciones")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"[CORRECTED] Conexión entrante desde {addr}")
                    
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        log(f"[CORRECTED] [RECIBIDO] {data.hex()}")
                        
                        if len(data) < 8:
                            log("[CORRECTED] [ERROR] Paquete demasiado corto")
                            continue
                        
                        if data.startswith(b'\x78\x78'):
                            if len(data) >= 4:
                                packet_length = data[2]
                                protocol = data[3]
                                
                                log(f"[CORRECTED] Protocol: 0x{protocol:02X}, Length: {packet_length}")
                                
                                if protocol == 0x01:  # Login
                                    log("[CORRECTED] Procesando login...")
                                    ack = handle_login_corrected(data, conn)
                                    if ack:
                                        log("[CORRECTED] ✓ ACK de login enviado correctamente")
                                    else:
                                        log("[CORRECTED] ✗ Error enviando ACK de login")
                                    
                                elif protocol == 0x12:  # Posición
                                    log("[CORRECTED] ¡POSICIÓN RECIBIDA! ACK funcionó")
                                    if parse_position_corrected(data):
                                        log("[CORRECTED] ✓ Posición parseada correctamente")
                                        
                                        # Enviar ACK para posición
                                        if len(data) >= 25:
                                            pos_serial = data[23:25]
                                            send_correct_ack(pos_serial, conn)
                                            log("[CORRECTED] ✓ ACK de posición enviado")
                                    else:
                                        log("[CORRECTED] ✗ Error parseando posición")
                                    
                                elif protocol == 0x13:  # Estado
                                    log("[CORRECTED] Estado recibido - ACK aún no reconocido")
                                    # Enviar ACK para estado
                                    if len(data) >= 8:
                                        status_info = data[4:-4]
                                        if len(status_info) >= 7:
                                            status_serial = status_info[-2:]
                                            send_correct_ack(status_serial, conn)
                                            log("[CORRECTED] ACK para estado enviado")
                                    
                                elif protocol == 0x23:  # Heartbeat
                                    log("[CORRECTED] Heartbeat recibido")
                                    
                                elif protocol == 0x26:  # Alarma
                                    log("[CORRECTED] Alarma recibida")
                                    
                                else:
                                    log(f"[CORRECTED] Protocolo desconocido: 0x{protocol:02X}")
                        else:
                            log("[CORRECTED] [ERROR] Paquete no comienza con 7878")
                            
            except socket.error as e:
                log(f"[CORRECTED] [ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[CORRECTED] [ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    main()
