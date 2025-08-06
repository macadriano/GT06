# emulaGPS.py (versión corregida y funcional para protocolo GT06)

import socket
import time
import random
from datetime import datetime

# IMEI válido (15 dígitos numéricos)
imei = '123456789012345'

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

# Coordenadas aleatorias dentro de CABA
def generar_coordenadas_buenos_aires():
    lat = round(random.uniform(-34.6037, -34.6200), 6)
    lon = round(random.uniform(-58.3816, -58.4455), 6)
    return lat, lon

# Codificación BCD para el IMEI
def bcd_encode(value):
    if len(value) % 2:
        value = '0' + value
    return bytes.fromhex(value)

# Armar paquete de login
def build_login_packet(imei):
    # Estructura correcta del paquete de login GT06
    # 7878 + length + 01 + IMEI(8 bytes) + serial(2 bytes) + error_check(2 bytes) + CRC16(2 bytes) + 0D0A
    imei_bytes = bcd_encode(imei)
    serial = random.randint(1, 65535).to_bytes(2, 'big')
    error_check = b'\x00\x00'  # Error check (2 bytes)
    
    # Contenido del paquete (sin 7878)
    content = bytes([0x01]) + imei_bytes + serial + error_check
    length = len(content)
    
    # Paquete completo
    packet = b'\x78\x78' + bytes([length]) + content
    checksum = crc16(packet[2:])
    packet += checksum + b'\x0D\x0A'
    
    print(f"Paquete login generado: {packet.hex()}")
    return packet

# Armar paquete de localización
def build_location_packet():
    # Estructura correcta del paquete de posición GT06
    now = datetime.utcnow()
    date_bytes = now.strftime('%y%m%d%H%M%S')
    date_bcd = bcd_encode(date_bytes)
    
    lat, lon = generar_coordenadas_buenos_aires()
    
    # Manejar signo de coordenadas correctamente
    lat_val = int(abs(lat) * 1800000)
    lon_val = int(abs(lon) * 1800000)
    
    # Agregar bit de signo (0 = positivo, 1 = negativo)
    if lat < 0:
        lat_val |= 0x80000000  # Bit 31 = 1 para latitud sur
    if lon < 0:
        lon_val |= 0x80000000  # Bit 31 = 1 para longitud oeste
    
    lat_bytes = lat_val.to_bytes(4, 'big')
    lon_bytes = lon_val.to_bytes(4, 'big')

    speed = random.randint(10, 100)
    course = random.randint(0, 359)
    course_bytes = course.to_bytes(2, 'big')
    
    # Información adicional del paquete de posición
    quantity = 1  # Cantidad de posiciones
    status = 0x00  # Estado del GPS
    mcc = 722  # Mobile Country Code (Argentina)
    mnc = 10   # Mobile Network Code
    lac = random.randint(1, 65535)  # Location Area Code
    cell_id = random.randint(1, 16777215)  # Cell ID
    serial = random.randint(1, 65535)  # Serial number
    error_check = b'\x00\x00'  # Error check
    
    # Contenido del paquete (sin 7878)
    content = (bytes([0x12]) + date_bcd + bytes([quantity]) + 
               lat_bytes + lon_bytes + bytes([speed]) + course_bytes + 
               bytes([status]) + mcc.to_bytes(2, 'big') + bytes([mnc]) + 
               lac.to_bytes(2, 'big') + cell_id.to_bytes(3, 'big') + 
               serial.to_bytes(2, 'big') + error_check)
    
    length = len(content)
    packet = b'\x78\x78' + bytes([length]) + content
    checksum = crc16(packet[2:])
    packet += checksum + b'\x0D\x0A'
    
    print(f"Paquete posición generado: {packet.hex()}")
    return packet

def validate_login_ack(response):
    """
    Valida que la respuesta del servidor sea un ACK de login correcto
    """
    if len(response) < 11:
        return False
    
    # Verificar estructura del ACK: 7878 + 05 + 01 + serial + CRC16 + 0D0A
    if not response.startswith(b'\x78\x78'):
        return False
    
    if response[2] != 0x05:  # Length debe ser 5
        return False
    
    if response[3] != 0x01:  # Tipo debe ser 01 (ACK de login)
        return False
    
    # Verificar que termine con 0D0A
    if not response.endswith(b'\x0D\x0A'):
        return False
    
    return True

# ------------------- MAIN --------------------

def main():
    host = '200.58.98.187'  # Cambiar si es otro host o usar '127.0.0.1' para pruebas
    port = 5003
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Configurar timeout para evitar bloqueos indefinidos
            s.settimeout(10)
            s.connect((host, port))
            print(f"Conectado a {host}:{port}")

            # Enviar login
            login_pkt = build_login_packet(imei)
            s.sendall(login_pkt)
            print("Login enviado")
            
            # Esperar respuesta del servidor
            try:
                response = s.recv(1024)
                if response:
                    print(f"Respuesta del servidor: {response.hex()}")
                    if validate_login_ack(response):
                        print("✓ ACK de login recibido correctamente")
                    else:
                        print("✗ ACK de login inválido o no recibido")
                        return
                else:
                    print("✗ No se recibió respuesta del servidor")
                    return
            except socket.timeout:
                print("✗ Timeout esperando respuesta del servidor")
                return
            
            time.sleep(2)

            # Enviar paquetes de localización
            for i in range(10):
                try:
                    loc_pkt = build_location_packet()
                    s.sendall(loc_pkt)
                    print(f"Paquete de localización enviado ({i+1}/10)")
                    
                    # Esperar breve respuesta del servidor (opcional para paquetes de posición)
                    try:
                        s.settimeout(2)  # Timeout más corto para respuestas de posición
                        response = s.recv(1024)
                        if response:
                            print(f"Respuesta: {response.hex()}")
                    except socket.timeout:
                        pass  # Es normal que no haya respuesta para paquetes de posición
                    finally:
                        s.settimeout(10)  # Restaurar timeout original
                        
                    time.sleep(5)
                except socket.error as e:
                    print(f"Error enviando paquete {i+1}: {e}")
                    break
                    
    except socket.timeout:
        print(f"Timeout conectando a {host}:{port}")
    except ConnectionRefusedError:
        print(f"Conexión rechazada en {host}:{port} - verificar que el servidor esté ejecutándose")
    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == '__main__':
    main()