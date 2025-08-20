#!/usr/bin/env python3
"""
GT06_MANUAL_STRICT - Módulo que implementa EXACTAMENTE las especificaciones
del manual del fabricante, basándose únicamente en el ejemplo del punto 5.1.3
"""

import socket
import datetime
import time

HOST = '0.0.0.0'
PORT = 5007  # Puerto específico para este módulo

LOG_FILE = "datosChino_manual_strict.txt"

# Tabla CRC-ITU del fabricante (del apéndice del manual)
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
    Implementación EXACTA del CRC-ITU según el manual del fabricante
    """
    fcs = 0xFFFF
    for byte in data:
        fcs = (fcs >> 8) ^ CRC_TAB16[(fcs ^ byte) & 0xFF]
    return ~fcs & 0xFFFF

def log(message):
    """
    Logging con timestamp
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"{line}\n")
    print(line)

def send_ack_manual(serial, conn):
    """
    Envía ACK EXACTAMENTE como especifica el manual del fabricante
    Basado en el ejemplo del punto 5.1.3:
    
    Login packet: 78 78 0D 01 03 53 41 35 32 15 03 62 00 02 2D 06 0D 0A
    ACK response: 78 78 05 01 00 02 EB 47 0D 0A
    
    Estructura: 7878 + 05 + 01 + serial + CRC + 0D0A
    """
    # Construir ACK según especificación del manual
    ack_data = b'\x05\x01' + serial  # 05 = longitud, 01 = protocolo, serial
    
    # Calcular CRC usando el algoritmo del fabricante
    crc = crc16_itu_factory(ack_data)
    crc_bytes = bytes([(crc >> 8) & 0xFF, crc & 0xFF])  # Big-endian
    
    # Construir ACK completo
    ack = b'\x78\x78' + ack_data + crc_bytes + b'\x0D\x0A'
    
    log(f"[MANUAL_ACK] === ACK SEGÚN MANUAL DEL FABRICANTE ===")
    log(f"[MANUAL_ACK] Serial recibido: {serial.hex()}")
    log(f"[MANUAL_ACK] ACK data: {ack_data.hex()}")
    log(f"[MANUAL_ACK] CRC calculado: {crc:04X} -> {crc_bytes.hex()}")
    log(f"[MANUAL_ACK] ACK completo: {ack.hex()}")
    log(f"[MANUAL_ACK] Estructura: 7878 + {ack_data.hex()} + {crc_bytes.hex()} + 0D0A")
    
    # Enviar ACK
    conn.sendall(ack)
    log(f"[MANUAL_ENVIADO] {ack.hex()}")
    
    return ack

def handle_login_manual(data, conn):
    """
    Maneja login EXACTAMENTE como especifica el manual
    """
    try:
        log(f"[MANUAL_LOGIN] === LOGIN SEGÚN MANUAL ===")
        log(f"[MANUAL_LOGIN] Paquete completo: {data.hex()}")
        
        # Verificar longitud mínima según manual
        if len(data) < 18:
            log(f"[MANUAL_ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return None
        
        # Extraer campos según especificación del manual
        packet_length = data[2]
        protocol = data[3]
        imei = data[4:12]
        serial = data[12:14]
        
        log(f"[MANUAL_LOGIN] Longitud del paquete: {packet_length}")
        log(f"[MANUAL_LOGIN] Protocolo: 0x{protocol:02X}")
        log(f"[MANUAL_LOGIN] IMEI: {imei.hex()}")
        log(f"[MANUAL_LOGIN] Serial: {serial.hex()}")
        
        # Verificar que sea un paquete de login válido
        if protocol != 0x01:
            log(f"[MANUAL_ERROR] Protocolo incorrecto: 0x{protocol:02X} (esperado: 0x01)")
            return None
        
        # Verificar longitud del paquete
        expected_length = packet_length + 5  # +5 por 7878 + length + CRC + 0D0A
        if len(data) != expected_length:
            log(f"[MANUAL_WARNING] Longitud del paquete no coincide: esperado {expected_length}, recibido {len(data)}")
        
        # Enviar ACK según especificación del manual
        ack = send_ack_manual(serial, conn)
        
        log(f"[MANUAL_LOGIN] ✓ Login procesado y ACK enviado según manual")
        return ack
        
    except Exception as e:
        log(f"[MANUAL_ERROR] Error en handle_login_manual: {e}")
        return None

def parse_packet_manual(data):
    """
    Parsea cualquier paquete recibido mostrando su estructura completa
    """
    try:
        log(f"[MANUAL_PACKET] === ANÁLISIS DE PAQUETE ===")
        log(f"[MANUAL_PACKET] Paquete completo: {data.hex()}")
        log(f"[MANUAL_PACKET] Longitud: {len(data)} bytes")
        
        if len(data) < 8:
            log(f"[MANUAL_ERROR] Paquete demasiado corto para analizar")
            return False
        
        # Verificar inicio del paquete
        if not data.startswith(b'\x78\x78'):
            log(f"[MANUAL_ERROR] Paquete no comienza con 7878")
            return False
        
        # Extraer campos básicos
        packet_length = data[2]
        protocol = data[3]
        
        log(f"[MANUAL_PACKET] Longitud del paquete: {packet_length}")
        log(f"[MANUAL_PACKET] Protocolo: 0x{protocol:02X}")
        
        # Identificar tipo de paquete según manual
        protocol_names = {
            0x01: "LOGIN",
            0x12: "POSICIÓN",
            0x13: "ESTADO",
            0x23: "HEARTBEAT",
            0x26: "ALARMA",
            0x80: "COMANDO DEL SERVIDOR"
        }
        
        protocol_name = protocol_names.get(protocol, "DESCONOCIDO")
        log(f"[MANUAL_PACKET] Tipo: {protocol_name}")
        
        # Mostrar estructura del paquete
        if len(data) >= 4:
            payload = data[4:-4]  # Excluir 7878 al inicio y CRC + 0D0A al final
            log(f"[MANUAL_PACKET] Payload: {payload.hex()}")
            
            # Mostrar CRC recibido
            if len(data) >= 6:
                received_crc = data[-4:-2]
                log(f"[MANUAL_PACKET] CRC recibido: {received_crc.hex()}")
                
                # Calcular CRC esperado
                expected_crc = crc16_itu_factory(payload)
                expected_crc_bytes = bytes([(expected_crc >> 8) & 0xFF, expected_crc & 0xFF])
                log(f"[MANUAL_PACKET] CRC esperado: {expected_crc:04X} -> {expected_crc_bytes.hex()}")
                
                # Verificar CRC
                if received_crc == expected_crc_bytes:
                    log(f"[MANUAL_PACKET] ✓ CRC válido")
                else:
                    log(f"[MANUAL_PACKET] ✗ CRC inválido")
        
        log(f"[MANUAL_PACKET] === FIN ANÁLISIS ===")
        return True
        
    except Exception as e:
        log(f"[MANUAL_ERROR] Error en parse_packet_manual: {e}")
        return False

def main():
    """
    Servidor principal que implementa EXACTAMENTE las especificaciones del manual
    """
    log(f"[MANUAL] ==========================================")
    log(f"[MANUAL] SERVIDOR GT06 - IMPLEMENTACIÓN MANUAL ESTRICTA")
    log(f"[MANUAL] Basado ÚNICAMENTE en especificaciones del fabricante")
    log(f"[MANUAL] Puerto: {PORT}")
    log(f"[MANUAL] Archivo de log: {LOG_FILE}")
    log(f"[MANUAL] ==========================================")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        log(f"[MANUAL] Servidor iniciado en {HOST}:{PORT}")
        log(f"[MANUAL] Esperando conexiones...")
        
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"[MANUAL] ==========================================")
                    log(f"[MANUAL] Conexión entrante desde {addr}")
                    log(f"[MANUAL] ==========================================")
                    
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        log(f"[MANUAL] [RECIBIDO] {data.hex()}")
                        
                        # Analizar TODOS los paquetes recibidos
                        parse_packet_manual(data)
                        
                        # Procesar según protocolo
                        if len(data) >= 4 and data.startswith(b'\x78\x78'):
                            protocol = data[3]
                            
                            if protocol == 0x01:  # Login
                                log(f"[MANUAL] Procesando LOGIN...")
                                ack = handle_login_manual(data, conn)
                                if ack:
                                    log(f"[MANUAL] ✓ ACK de login enviado según manual")
                                else:
                                    log(f"[MANUAL] ✗ Error enviando ACK de login")
                            
                            elif protocol == 0x12:  # Posición
                                log(f"[MANUAL] ¡POSICIÓN RECIBIDA! ACK funcionó")
                                # Enviar ACK para posición usando la misma lógica del manual
                                if len(data) >= 25:
                                    pos_serial = data[23:25]
                                    send_ack_manual(pos_serial, conn)
                            
                            elif protocol == 0x13:  # Estado
                                log(f"[MANUAL] Estado recibido - ACK aún no reconocido")
                                # Enviar ACK para estado
                                if len(data) >= 8:
                                    status_info = data[4:-4]
                                    if len(status_info) >= 7:
                                        status_serial = status_info[-2:]
                                        send_ack_manual(status_serial, conn)
                            
                            elif protocol == 0x23:  # Heartbeat
                                log(f"[MANUAL] Heartbeat recibido")
                            
                            elif protocol == 0x26:  # Alarma
                                log(f"[MANUAL] Alarma recibida")
                            
                            elif protocol == 0x80:  # Comando del servidor
                                log(f"[MANUAL] Comando del servidor recibido")
                            
                            else:
                                log(f"[MANUAL] Protocolo desconocido: 0x{protocol:02X}")
                        else:
                            log(f"[MANUAL] [ERROR] Paquete no válido")
                            
            except socket.error as e:
                log(f"[MANUAL] [ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[MANUAL] [ERROR] Error inesperado: {e}")

if __name__ == "__main__":
    main()
