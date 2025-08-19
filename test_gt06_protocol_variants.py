#!/usr/bin/env python3
"""
Script para probar diferentes variantes del protocolo GT06 según especificaciones del fabricante
"""

import socket
import datetime
import time
import threading

HOST = '200.58.98.187'
PORT = 4996  # Puerto diferente para pruebas

LOG_FILE = "test_protocol_variants.txt"

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

def crc16_itu_factory_bytes_le(data):
    """CRC en formato bytes (little-endian)"""
    crc = crc16_itu_factory(data)
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a") as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    log(f"[ENVIADO] {data.hex()}")

def test_ack_variants(serial, conn):
    """
    Prueba diferentes variantes de ACK según especificaciones GT06
    """
    log("[TEST] === PRUEBA DE VARIANTES DE ACK ===")
    
    # Variante 1: ACK estándar GT06 (longitud 05 como en el manual)
    # Estructura: 7878 + 05 + 01 + serial + CRC + 0D0A
    ack_data_1 = b'\x05\x01' + serial
    crc_1 = crc16_itu_factory_bytes_be(ack_data_1)
    ack_1 = b'\x78\x78' + ack_data_1 + crc_1 + b'\x0D\x0A'
    log(f"[TEST] Variante 1 - ACK estándar GT06: {ack_1.hex()}")
    conn.sendall(ack_1)
    log_sent(ack_1)
    time.sleep(2)
    
    # Variante 2: ACK con longitud 04 (formato común)
    # Estructura: 7878 + 04 + 01 + serial + CRC + 0D0A
    ack_data_2 = b'\x04\x01' + serial
    crc_2 = crc16_itu_factory_bytes_be(ack_data_2)
    ack_2 = b'\x78\x78' + ack_data_2 + crc_2 + b'\x0D\x0A'
    log(f"[TEST] Variante 2 - ACK longitud 04: {ack_2.hex()}")
    conn.sendall(ack_2)
    log_sent(ack_2)
    time.sleep(2)
    
    # Variante 3: ACK con longitud 03 (formato mínimo)
    # Estructura: 7878 + 03 + 01 + serial + CRC + 0D0A
    ack_data_3 = b'\x03\x01' + serial
    crc_3 = crc16_itu_factory_bytes_be(ack_data_3)
    ack_3 = b'\x78\x78' + ack_data_3 + crc_3 + b'\x0D\x0A'
    log(f"[TEST] Variante 3 - ACK longitud 03: {ack_3.hex()}")
    conn.sendall(ack_3)
    log_sent(ack_3)
    time.sleep(2)
    
    # Variante 4: ACK con CRC little-endian
    # Estructura: 7878 + 04 + 01 + serial + CRC_LE + 0D0A
    ack_data_4 = b'\x04\x01' + serial
    crc_4 = crc16_itu_factory_bytes_le(ack_data_4)
    ack_4 = b'\x78\x78' + ack_data_4 + crc_4 + b'\x0D\x0A'
    log(f"[TEST] Variante 4 - ACK CRC LE: {ack_4.hex()}")
    conn.sendall(ack_4)
    log_sent(ack_4)
    time.sleep(2)
    
    # Variante 5: ACK con checksum simple (no CRC)
    # Estructura: 7878 + 04 + 01 + serial + checksum + 0D0A
    ack_data_5 = b'\x04\x01' + serial
    checksum = sum(ack_data_5) & 0xFFFF
    checksum_bytes = bytes([(checksum >> 8) & 0xFF, checksum & 0xFF])
    ack_5 = b'\x78\x78' + ack_data_5 + checksum_bytes + b'\x0D\x0A'
    log(f"[TEST] Variante 5 - ACK checksum simple: {ack_5.hex()}")
    conn.sendall(ack_5)
    log_sent(ack_5)
    time.sleep(2)
    
    # Variante 6: ACK sin terminador 0D0A
    # Estructura: 7878 + 04 + 01 + serial + CRC
    ack_data_6 = b'\x04\x01' + serial
    crc_6 = crc16_itu_factory_bytes_be(ack_data_6)
    ack_6 = b'\x78\x78' + ack_data_6 + crc_6
    log(f"[TEST] Variante 6 - ACK sin 0D0A: {ack_6.hex()}")
    conn.sendall(ack_6)
    log_sent(ack_6)
    time.sleep(2)
    
    # Variante 7: ACK con formato diferente (protocolo 02 en lugar de 01)
    # Estructura: 7878 + 04 + 02 + serial + CRC + 0D0A
    ack_data_7 = b'\x04\x02' + serial
    crc_7 = crc16_itu_factory_bytes_be(ack_data_7)
    ack_7 = b'\x78\x78' + ack_data_7 + crc_7 + b'\x0D\x0A'
    log(f"[TEST] Variante 7 - ACK protocolo 02: {ack_7.hex()}")
    conn.sendall(ack_7)
    log_sent(ack_7)
    time.sleep(2)
    
    # Variante 8: ACK con formato GT06N (diferente estructura)
    # Estructura: 7878 + 03 + 01 + serial + CRC + 0D0A
    ack_data_8 = b'\x03\x01' + serial
    crc_8 = crc16_itu_factory_bytes_be(ack_data_8)
    ack_8 = b'\x78\x78' + ack_data_8 + crc_8 + b'\x0D\x0A'
    log(f"[TEST] Variante 8 - ACK GT06N: {ack_8.hex()}")
    conn.sendall(ack_8)
    log_sent(ack_8)
    time.sleep(2)

def analyze_packet_structure(data):
    """
    Analiza la estructura del paquete recibido
    """
    log(f"[ANALYSIS] === ANÁLISIS DE ESTRUCTURA DE PAQUETE ===")
    log(f"[ANALYSIS] Paquete completo: {data.hex()}")
    log(f"[ANALYSIS] Longitud: {len(data)} bytes")
    
    if len(data) >= 4:
        header = data[0:2]
        length_byte = data[2]
        protocol = data[3]
        
        log(f"[ANALYSIS] Header: {header.hex()}")
        log(f"[ANALYSIS] Length byte: {length_byte:02X} ({length_byte})")
        log(f"[ANALYSIS] Protocol: {protocol:02X}")
        
        # Verificar longitud esperada
        expected_length = length_byte + 6  # 7878 + length + data + crc + 0D0A
        log(f"[ANALYSIS] Longitud esperada: {expected_length}")
        log(f"[ANALYSIS] Longitud real: {len(data)}")
        log(f"[ANALYSIS] ¿Coincide?: {'SÍ' if len(data) == expected_length else 'NO'}")
        
        # Analizar estructura según protocolo
        if protocol == 0x01:  # Login
            log(f"[ANALYSIS] Protocolo: LOGIN (0x01)")
            if len(data) >= 18:
                imei = data[4:12].hex()
                serial = data[12:14].hex()
                error_check = data[14:16].hex()
                crc = data[16:18].hex()
                
                log(f"[ANALYSIS] IMEI: {imei}")
                log(f"[ANALYSIS] Serial: {serial}")
                log(f"[ANALYSIS] Error check: {error_check}")
                log(f"[ANALYSIS] CRC: {crc}")
                
        elif protocol == 0x12:  # Posición
            log(f"[ANALYSIS] Protocolo: POSICIÓN (0x12)")
            if len(data) >= 25:
                date_bytes = data[4:10].hex()
                quantity = data[10]
                lat_raw = data[11:15].hex()
                lon_raw = data[15:19].hex()
                speed = data[19]
                course = int.from_bytes(data[20:22], byteorder='big')
                
                log(f"[ANALYSIS] Date: {date_bytes}")
                log(f"[ANALYSIS] Quantity: {quantity}")
                log(f"[ANALYSIS] Lat raw: {lat_raw}")
                log(f"[ANALYSIS] Lon raw: {lon_raw}")
                log(f"[ANALYSIS] Speed: {speed}")
                log(f"[ANALYSIS] Course: {course}")
                
        elif protocol == 0x13:  # Estado
            log(f"[ANALYSIS] Protocolo: ESTADO (0x13)")
            if len(data) >= 8:
                status_data = data[4:-4].hex()
                log(f"[ANALYSIS] Status data: {status_data}")

def handle_login_test(data, conn):
    """
    Maneja el login con análisis detallado
    """
    try:
        log(f"[TEST] === PROCESANDO LOGIN ===")
        
        if len(data) < 18:
            log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return
        
        # Analizar estructura del paquete
        analyze_packet_structure(data)
        
        # Extraer IMEI y serial
        imei = data[4:12].hex()
        serial = data[12:14]
        
        log(f"[TEST] IMEI extraído: {imei}")
        log(f"[TEST] Serial extraído: {serial.hex()}")
        
        # Probar diferentes variantes de ACK
        test_ack_variants(serial, conn)
        
        return True
        
    except Exception as e:
        log(f"[ERROR] Error en handle_login_test: {e}")
        return False

def main():
    log(f"[TEST] Servidor de prueba iniciado en {HOST}:{PORT}")
    log(f"[TEST] Probando diferentes variantes del protocolo GT06")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"[TEST] Conexión entrante desde {addr}")
                    
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        log(f"[TEST] [RECIBIDO] {data.hex()}")
                        
                        if len(data) < 8:
                            log("[TEST] [ERROR] Paquete demasiado corto")
                            continue
                        
                        if data.startswith(b'\x78\x78'):
                            if len(data) >= 4:
                                protocol = data[3]
                                
                                log(f"[TEST] Protocolo detectado: 0x{protocol:02X}")
                                
                                if protocol == 0x01:  # Login
                                    log("[TEST] Procesando login...")
                                    handle_login_test(data, conn)
                                    
                                elif protocol == 0x12:  # Posición
                                    log("[TEST] ¡POSICIÓN RECIBIDA! ACK funcionó")
                                    analyze_packet_structure(data)
                                    
                                elif protocol == 0x13:  # Estado
                                    log("[TEST] Estado recibido - ACK aún no reconocido")
                                    analyze_packet_structure(data)
                                    
                                elif protocol == 0x23:  # Heartbeat
                                    log("[TEST] Heartbeat recibido")
                                    
                                elif protocol == 0x26:  # Alarma
                                    log("[TEST] Alarma recibida")
                                    
                                else:
                                    log(f"[TEST] Protocolo desconocido: 0x{protocol:02X}")
                        else:
                            log("[TEST] [ERROR] Paquete no comienza con 7878")
                            
            except socket.error as e:
                log(f"[TEST] [ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[TEST] [ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    main()
