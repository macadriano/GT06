# emulaGPS.py (versión corregida y funcional para protocolo GT06)

import socket
import time
import random
from datetime import datetime

# IMEI válido (15 dígitos numéricos)
imei = '123456789012345'

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

# Calcular checksum para el paquete
def calcular_checksum(data):
    return sum(data).to_bytes(2, byteorder='big')

# Armar paquete de login

def build_login_packet(imei):
    imei_bytes = bcd_encode(imei)
    content = bytes([0x01]) + imei_bytes
    length = len(content).to_bytes(2, byteorder='big')
    packet = b'\x78\x78' + length + content + calcular_checksum(content) + b'\x0D\x0A'
    return packet

# Armar paquete de localización

def build_location_packet():
    now = datetime.utcnow()
    date_bytes = now.strftime('%y%m%d%H%M%S')
    date_bcd = bcd_encode(date_bytes)
    
    lat, lon = generar_coordenadas_buenos_aires()
    lat_val = int(abs(lat) * 1800000)  # Grados a formato GT06
    lon_val = int(abs(lon) * 1800000)
    
    lat_bytes = lat_val.to_bytes(4, byteorder='big')
    lon_bytes = lon_val.to_bytes(4, byteorder='big')

    speed = random.randint(10, 100)
    course = random.randint(0, 359)
    
    gps_info = bytes([0xF8]) + speed.to_bytes(1, 'big') + course.to_bytes(2, 'big')
    
    content = bytes([0x12]) + date_bcd + b'\x00\x10\x04\x01' + lat_bytes + lon_bytes + gps_info
    length = len(content).to_bytes(2, byteorder='big')
    packet = b'\x78\x78' + length + content + calcular_checksum(content) + b'\x0D\x0A'
    return packet

# ------------------- MAIN --------------------

def main():
    host = '200.58.98.187'  # Cambiar si es otro host o usar '127.0.0.1' para pruebas
    port = 5003
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Conectado a {host}:{port}")

        login_pkt = build_login_packet(imei)
        s.sendall(login_pkt)
        print("Login enviado")
        time.sleep(2)

        for i in range(10):
            loc_pkt = build_location_packet()
            s.sendall(loc_pkt)
            print(f"Paquete de localización enviado ({i+1})")
            time.sleep(5)

if __name__ == '__main__':
    main()