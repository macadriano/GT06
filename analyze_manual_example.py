#!/usr/bin/env python3
"""
Análisis del ejemplo del manual GT06 para verificar el ACK correcto
"""

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

print("=== ANÁLISIS DEL EJEMPLO DEL MANUAL GT06 ===")
print()

# Ejemplo del manual:
# Login packet: 78 78 0D 01 01 23 45 67 89 01 23 45 00 01 8C DD 0D 0A
# ACK packet:   78 78 05 01 00 01 D9 DC 0D 0A

print("1. ANÁLISIS DEL PAQUETE DE LOGIN:")
login_packet = bytes.fromhex("78780d01012345678901234500018cdd0d0a")
print(f"Login packet completo: {login_packet.hex()}")
print(f"Login packet (formato): {' '.join([f'{b:02X}' for b in login_packet])}")

# Extraer componentes del login
start_bit = login_packet[0:2]  # 78 78
length = login_packet[2]       # 0D
protocol = login_packet[3]     # 01
terminal_id = login_packet[4:12]  # 01 23 45 67 89 01 23 45
serial = login_packet[12:14]   # 00 01
error_check = login_packet[14:16]  # 8C DD
stop_bit = login_packet[16:18] # 0D 0A

print(f"Start bit: {start_bit.hex()}")
print(f"Length: {length:02X}")
print(f"Protocol: {protocol:02X}")
print(f"Terminal ID: {terminal_id.hex()}")
print(f"Serial: {serial.hex()}")
print(f"Error check (CRC): {error_check.hex()}")
print(f"Stop bit: {stop_bit.hex()}")

# Verificar CRC del login
login_data = login_packet[2:-4]  # Desde length hasta antes del CRC
expected_crc = crc16_itu_factory_bytes_be(login_data)
print(f"Login data para CRC: {login_data.hex()}")
print(f"CRC esperado (BE): {expected_crc.hex()}")
print(f"CRC recibido: {error_check.hex()}")
print(f"¿CRC coincide?: {'SÍ' if expected_crc == error_check else 'NO'}")

print()
print("2. ANÁLISIS DEL ACK DEL MANUAL:")
ack_packet = bytes.fromhex("787805010001d9dc0d0a")
print(f"ACK packet completo: {ack_packet.hex()}")
print(f"ACK packet (formato): {' '.join([f'{b:02X}' for b in ack_packet])}")

# Extraer componentes del ACK
ack_start_bit = ack_packet[0:2]  # 78 78
ack_length = ack_packet[2]       # 05
ack_protocol = ack_packet[3]     # 01
ack_serial = ack_packet[4:6]     # 00 01
ack_error_check = ack_packet[6:8]  # D9 DC
ack_stop_bit = ack_packet[8:10]  # 0D 0A

print(f"ACK Start bit: {ack_start_bit.hex()}")
print(f"ACK Length: {ack_length:02X}")
print(f"ACK Protocol: {ack_protocol:02X}")
print(f"ACK Serial: {ack_serial.hex()}")
print(f"ACK Error check (CRC): {ack_error_check.hex()}")
print(f"ACK Stop bit: {ack_stop_bit.hex()}")

# Verificar CRC del ACK
ack_data = ack_packet[2:-4]  # Desde length hasta antes del CRC
expected_ack_crc = crc16_itu_factory_bytes_be(ack_data)
print(f"ACK data para CRC: {ack_data.hex()}")
print(f"ACK CRC esperado (BE): {expected_ack_crc.hex()}")
print(f"ACK CRC recibido: {ack_error_check.hex()}")
print(f"¿ACK CRC coincide?: {'SÍ' if expected_ack_crc == ack_error_check else 'NO'}")

print()
print("3. VERIFICACIÓN DE NUESTRO ACK:")
# Nuestro serial del ejemplo: 00 01
our_serial = b'\x00\x01'
our_ack_data = b'\x05\x01' + our_serial
our_crc = crc16_itu_factory_bytes_be(our_ack_data)
our_ack = b'\x78\x78' + our_ack_data + our_crc + b'\x0D\x0A'

print(f"Nuestro serial: {our_serial.hex()}")
print(f"Nuestro ACK data: {our_ack_data.hex()}")
print(f"Nuestro CRC: {our_crc.hex()}")
print(f"Nuestro ACK completo: {our_ack.hex()}")
print(f"Nuestro ACK (formato): {' '.join([f'{b:02X}' for b in our_ack])}")
print(f"¿Nuestro ACK coincide con el manual?: {'SÍ' if our_ack == ack_packet else 'NO'}")

print()
print("4. PRUEBAS CON DIFERENTES VARIANTES:")
variants = [
    ("standard", b'\x05\x01'),
    ("short_length", b'\x03\x01'),
    ("manual_exact", b'\x05\x01'),  # Igual al manual
]

for variant_name, ack_data_base in variants:
    ack_data = ack_data_base + our_serial
    crc_be = crc16_itu_factory_bytes_be(ack_data)
    crc_le = crc16_itu_factory_bytes_le(ack_data)
    ack_be = b'\x78\x78' + ack_data + crc_be + b'\x0D\x0A'
    ack_le = b'\x78\x78' + ack_data + crc_le + b'\x0D\x0A'
    
    print(f"{variant_name.upper()}:")
    print(f"  ACK data: {ack_data.hex()}")
    print(f"  CRC (BE): {crc_be.hex()}")
    print(f"  CRC (LE): {crc_le.hex()}")
    print(f"  ACK (BE): {ack_be.hex()}")
    print(f"  ACK (LE): {ack_le.hex()}")
    print(f"  ¿Coincide con manual?: {'SÍ' if ack_be == ack_packet else 'NO'}")
    print()
