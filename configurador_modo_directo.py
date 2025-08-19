#!/usr/bin/env python3
"""
Configurador de Modo Directo para GT06
======================================

Este script recibe la conexión del dispositivo GT06 y lo configura
para que envíe datos directamente sin necesidad de login previo.

Uso:
    python configurador_modo_directo.py

El script:
1. Espera la conexión del dispositivo
2. Procesa el login inicial
3. Envía comando para cambiar a modo directo
4. Confirma que el dispositivo aceptó el cambio
"""

import socket
import datetime
import time
import threading

# Configuración del servidor
HOST = '200.58.98.187'
PORT = 5003  # Puerto diferente al servidor principal
LOG_FILE = "configurador_modo_directo.txt"

# Comando para configurar modo directo (ajustar según el fabricante)
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
    """Implementación exacta del algoritmo CRC-ITU del fabricante"""
    fcs = 0xFFFF
    for byte in data:
        fcs = (fcs >> 8) ^ CRC_TAB16[(fcs ^ byte) & 0xFF]
    return ~fcs & 0xFFFF

def crc16_itu_factory_bytes(data):
    """Retorna el CRC en formato bytes (little-endian)"""
    crc = crc16_itu_factory(data)
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_itu_factory_bytes_be(data):
    """Retorna el CRC en formato bytes (big-endian)"""
    crc = crc16_itu_factory(data)
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def log(message):
    """Función de logging con timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {message}"
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"{line}\n")
    print(line)

def log_sent(data):
    """Log de datos enviados"""
    log(f"[ENVIADO] {data.hex()}")

def validate_packet_crc(data):
    """Valida el CRC16 de un paquete recibido"""
    if len(data) < 6:
        return False
    
    packet_data = data[2:-4]  # Sin 7878 y sin CRC16 + 0D0A
    received_crc = data[-4:-2]  # CRC recibido
    
    expected_crc_itu_le = crc16_itu_factory_bytes(packet_data)
    expected_crc_itu_be = crc16_itu_factory_bytes_be(packet_data)
    
    log(f"[DEBUG] Packet data: {packet_data.hex()}")
    log(f"[DEBUG] Received CRC: {received_crc.hex()}")
    log(f"[DEBUG] Expected CRC (ITU LE): {expected_crc_itu_le.hex()}")
    log(f"[DEBUG] Expected CRC (ITU BE): {expected_crc_itu_be.hex()}")
    
    if received_crc == expected_crc_itu_le:
        log("[DEBUG] CRC coincide con algoritmo CRC-ITU del fabricante (LE)")
        return 'itu_le'
    elif received_crc == expected_crc_itu_be:
        log("[DEBUG] CRC coincide con algoritmo CRC-ITU del fabricante (BE)")
        return 'itu_be'
    else:
        log("[DEBUG] CRC no coincide con ninguna variante del fabricante")
        return None

def handle_login(data):
    """Maneja el paquete de login y retorna el ACK correspondiente"""
    try:
        if len(data) < 18:
            log(f"[ERROR] Paquete de login demasiado corto: {len(data)} bytes")
            return None, None, None
        
        # Validar CRC del paquete de login
        crc_type = validate_packet_crc(data)
        if not crc_type:
            log("[WARNING] CRC del paquete de login no coincide, pero continuando...")
        
        # Extraer IMEI
        if len(data) >= 12:
            imei = data[4:12].hex()
            log(f"[LOGIN] IMEI: {imei}")
        else:
            log(f"[ERROR] No se puede extraer IMEI del paquete de {len(data)} bytes")
            return None, None, None
        
        # Extraer serial
        if len(data) >= 14:
            serial = data[12:14]
            log(f"[LOGIN] Serial: {serial.hex()}")
        else:
            serial = b'\x00\x01'
            log(f"[LOGIN] Serial no encontrado, usando por defecto: {serial.hex()}")
        
        # Construir ACK
        ack_data = b'\x05\x01' + serial
        
        if crc_type == 'itu_le':
            checksum = crc16_itu_factory_bytes(ack_data)
            log("[DEBUG] Usando CRC-ITU del fabricante (LE) para ACK")
        elif crc_type == 'itu_be':
            checksum = crc16_itu_factory_bytes_be(ack_data)
            log("[DEBUG] Usando CRC-ITU del fabricante (BE) para ACK")
        else:
            checksum = crc16_itu_factory_bytes_be(ack_data)  # Por defecto BE
            log("[DEBUG] Usando CRC-ITU del fabricante (BE) por defecto")
            crc_type = 'itu_be'
        
        ack = b'\x78\x78' + ack_data + checksum + b'\x0D\x0A'
        log_sent(ack)
        
        return ack, serial, crc_type
        
    except Exception as e:
        log(f"[ERROR] Error en handle_login: {e}")
        return None, None, None

def build_server_command_packet(command_ascii, serial, crc_variant='itu_be'):
    """Construye un paquete de comando hacia el dispositivo (protocolo 0x80)"""
    protocol_no = 0x80
    
    # length = protocolo(1) + contenido(len) + serial(2)
    body = bytes([1 + len(command_ascii) + 2, protocol_no]) + command_ascii + serial
    
    if crc_variant == 'itu_le':
        crc = crc16_itu_factory_bytes(body)
    else:
        crc = crc16_itu_factory_bytes_be(body)
    
    return b"\x78\x78" + body + crc + b"\x0D\x0A"

def send_direct_mode_command(conn, serial, crc_variant):
    """Envía el comando para configurar el equipo en modo directo"""
    try:
        packet = build_server_command_packet(DIRECT_MODE_COMMAND, serial, crc_variant)
        log(f"[CMD] Enviando comando de modo directo ({crc_variant}): {packet.hex()}")
        log(f"[CMD] Comando ASCII: {DIRECT_MODE_COMMAND.decode('ascii', errors='ignore')}")
        conn.sendall(packet)
        log_sent(packet)
        return True
    except Exception as e:
        log(f"[ERROR] Error enviando comando de modo directo: {e}")
        return False

def wait_for_confirmation(conn, timeout=30):
    """Espera confirmación del dispositivo de que aceptó el comando"""
    log(f"[CONFIRMACION] Esperando respuesta del dispositivo (timeout: {timeout}s)")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn.settimeout(1)  # Timeout de 1 segundo para cada recv
            data = conn.recv(1024)
            if data:
                log(f"[RECIBIDO] {data.hex()}")
                
                if data.startswith(b'\x78\x78'):
                    tipo_paquete = data[3] if len(data) > 3 else 0
                    
                    if tipo_paquete == 0x12:  # Posición
                        log(f"[SUCCESS] ¡Dispositivo envió posición! Modo directo configurado exitosamente")
                        return True
                    elif tipo_paquete == 0x13:  # Estado
                        log(f"[INFO] Dispositivo envió estado - posible confirmación")
                        return True
                    elif tipo_paquete == 0x23:  # Heartbeat
                        log(f"[INFO] Dispositivo envió heartbeat - posible confirmación")
                        return True
                    else:
                        log(f"[INFO] Dispositivo envió paquete tipo 0x{tipo_paquete:02X}")
                        
        except socket.timeout:
            continue
        except Exception as e:
            log(f"[ERROR] Error esperando confirmación: {e}")
            break
    
    log(f"[TIMEOUT] No se recibió confirmación en {timeout} segundos")
    return False

def main():
    """Función principal del configurador"""
    log(f"=== CONFIGURADOR DE MODO DIRECTO ===")
    log(f"Servidor iniciado en {HOST}:{PORT}")
    log(f"Comando a enviar: {DIRECT_MODE_COMMAND.decode('ascii', errors='ignore')}")
    log(f"Esperando conexión del dispositivo...")
    log(f"=====================================")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    log(f"Conexión entrante desde {addr}")
                    log(f"Iniciando proceso de configuración...")
                    
                    # Esperar el paquete de login
                    data = conn.recv(1024)
                    if not data:
                        log("[ERROR] No se recibieron datos")
                        continue
                    
                    log(f"[RECIBIDO] {data.hex()}")
                    
                    if not data.startswith(b'\x78\x78'):
                        log("[ERROR] Paquete no comienza con cabecera 7878")
                        continue
                    
                    tipo_paquete = data[3] if len(data) > 3 else 0
                    
                    if tipo_paquete != 0x01:
                        log(f"[ERROR] Se esperaba paquete de login (0x01), se recibió 0x{tipo_paquete:02X}")
                        continue
                    
                    # Procesar login
                    ack, serial, crc_type = handle_login(data)
                    if not ack:
                        log("[ERROR] No se pudo procesar el login")
                        continue
                    
                    # Enviar ACK de login
                    conn.sendall(ack)
                    log(f"[LOGIN] ACK enviado exitosamente")
                    
                    # Esperar un momento antes de enviar el comando
                    time.sleep(2)
                    
                    # Enviar comando de modo directo
                    if send_direct_mode_command(conn, serial, crc_type):
                        log(f"[CMD] Comando enviado exitosamente")
                        
                        # Esperar confirmación
                        if wait_for_confirmation(conn, timeout=30):
                            log(f"[SUCCESS] ¡Configuración completada exitosamente!")
                            log(f"[SUCCESS] El dispositivo ahora está en modo directo")
                            log(f"[SUCCESS] Puedes desconectarlo y conectarlo al servidor principal")
                        else:
                            log(f"[WARNING] No se recibió confirmación clara")
                            log(f"[WARNING] El dispositivo puede no haber aceptado el comando")
                    else:
                        log(f"[ERROR] No se pudo enviar el comando de modo directo")
                    
                    # Mantener la conexión abierta un poco más para recibir posibles respuestas
                    log(f"[INFO] Manteniendo conexión abierta por 10 segundos más...")
                    time.sleep(10)
                    
            except socket.error as e:
                log(f"[ERROR] Error de socket: {e}")
            except Exception as e:
                log(f"[ERROR] Error inesperado: {e}")
                import traceback
                log(f"[ERROR] Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
