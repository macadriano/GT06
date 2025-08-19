#!/usr/bin/env python3
"""
Análisis de las especificaciones del protocolo GT06
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

def analyze_gt06_specifications():
    """
    Analiza las especificaciones del protocolo GT06
    """
    print("=== ANÁLISIS DE ESPECIFICACIONES GT06 ===")
    
    # Especificaciones conocidas del protocolo GT06
    print("\n1. ESTRUCTURA GENERAL DEL PAQUETE:")
    print("   - Header: 78 78 (2 bytes)")
    print("   - Length: 1 byte (longitud de los datos)")
    print("   - Protocol: 1 byte (tipo de paquete)")
    print("   - Data: N bytes (datos específicos del protocolo)")
    print("   - CRC: 2 bytes (checksum)")
    print("   - End: 0D 0A (2 bytes)")
    print("   - Total: 6 + length bytes")
    
    print("\n2. TIPOS DE PAQUETES:")
    print("   - 0x01: Login Information")
    print("   - 0x12: Location Data")
    print("   - 0x13: Status Information")
    print("   - 0x15: String Information")
    print("   - 0x16: Alarm Data")
    print("   - 0x1A: ICCID")
    print("   - 0x22: LBS Query")
    print("   - 0x23: LBS Response")
    print("   - 0x27: LBS Extended Query")
    print("   - 0x28: LBS Extended Response")
    print("   - 0x80: Server Command")
    print("   - 0x81: Server Command Response")
    print("   - 0x82: Server Command Response")
    print("   - 0x83: Server Command Response")
    print("   - 0x84: Server Command Response")
    print("   - 0x85: Server Command Response")
    print("   - 0x86: Server Command Response")
    print("   - 0x87: Server Command Response")
    print("   - 0x88: Server Command Response")
    print("   - 0x89: Server Command Response")
    print("   - 0x8A: Server Command Response")
    print("   - 0x8B: Server Command Response")
    print("   - 0x8C: Server Command Response")
    print("   - 0x8D: Server Command Response")
    print("   - 0x8E: Server Command Response")
    print("   - 0x8F: Server Command Response")
    print("   - 0x90: Server Command Response")
    print("   - 0x91: Server Command Response")
    print("   - 0x92: Server Command Response")
    print("   - 0x93: Server Command Response")
    print("   - 0x94: Server Command Response")
    print("   - 0x95: Server Command Response")
    print("   - 0x96: Server Command Response")
    print("   - 0x97: Server Command Response")
    print("   - 0x98: Server Command Response")
    print("   - 0x99: Server Command Response")
    print("   - 0x9A: Server Command Response")
    print("   - 0x9B: Server Command Response")
    print("   - 0x9C: Server Command Response")
    print("   - 0x9D: Server Command Response")
    print("   - 0x9E: Server Command Response")
    print("   - 0x9F: Server Command Response")
    print("   - 0xA0: Server Command Response")
    print("   - 0xA1: Server Command Response")
    print("   - 0xA2: Server Command Response")
    print("   - 0xA3: Server Command Response")
    print("   - 0xA4: Server Command Response")
    print("   - 0xA5: Server Command Response")
    print("   - 0xA6: Server Command Response")
    print("   - 0xA7: Server Command Response")
    print("   - 0xA8: Server Command Response")
    print("   - 0xA9: Server Command Response")
    print("   - 0xAA: Server Command Response")
    print("   - 0xAB: Server Command Response")
    print("   - 0xAC: Server Command Response")
    print("   - 0xAD: Server Command Response")
    print("   - 0xAE: Server Command Response")
    print("   - 0xAF: Server Command Response")
    print("   - 0xB0: Server Command Response")
    print("   - 0xB1: Server Command Response")
    print("   - 0xB2: Server Command Response")
    print("   - 0xB3: Server Command Response")
    print("   - 0xB4: Server Command Response")
    print("   - 0xB5: Server Command Response")
    print("   - 0xB6: Server Command Response")
    print("   - 0xB7: Server Command Response")
    print("   - 0xB8: Server Command Response")
    print("   - 0xB9: Server Command Response")
    print("   - 0xBA: Server Command Response")
    print("   - 0xBB: Server Command Response")
    print("   - 0xBC: Server Command Response")
    print("   - 0xBD: Server Command Response")
    print("   - 0xBE: Server Command Response")
    print("   - 0xBF: Server Command Response")
    print("   - 0xC0: Server Command Response")
    print("   - 0xC1: Server Command Response")
    print("   - 0xC2: Server Command Response")
    print("   - 0xC3: Server Command Response")
    print("   - 0xC4: Server Command Response")
    print("   - 0xC5: Server Command Response")
    print("   - 0xC6: Server Command Response")
    print("   - 0xC7: Server Command Response")
    print("   - 0xC8: Server Command Response")
    print("   - 0xC9: Server Command Response")
    print("   - 0xCA: Server Command Response")
    print("   - 0xCB: Server Command Response")
    print("   - 0xCC: Server Command Response")
    print("   - 0xCD: Server Command Response")
    print("   - 0xCE: Server Command Response")
    print("   - 0xCF: Server Command Response")
    print("   - 0xD0: Server Command Response")
    print("   - 0xD1: Server Command Response")
    print("   - 0xD2: Server Command Response")
    print("   - 0xD3: Server Command Response")
    print("   - 0xD4: Server Command Response")
    print("   - 0xD5: Server Command Response")
    print("   - 0xD6: Server Command Response")
    print("   - 0xD7: Server Command Response")
    print("   - 0xD8: Server Command Response")
    print("   - 0xD9: Server Command Response")
    print("   - 0xDA: Server Command Response")
    print("   - 0xDB: Server Command Response")
    print("   - 0xDC: Server Command Response")
    print("   - 0xDD: Server Command Response")
    print("   - 0xDE: Server Command Response")
    print("   - 0xDF: Server Command Response")
    print("   - 0xE0: Server Command Response")
    print("   - 0xE1: Server Command Response")
    print("   - 0xE2: Server Command Response")
    print("   - 0xE3: Server Command Response")
    print("   - 0xE4: Server Command Response")
    print("   - 0xE5: Server Command Response")
    print("   - 0xE6: Server Command Response")
    print("   - 0xE7: Server Command Response")
    print("   - 0xE8: Server Command Response")
    print("   - 0xE9: Server Command Response")
    print("   - 0xEA: Server Command Response")
    print("   - 0xEB: Server Command Response")
    print("   - 0xEC: Server Command Response")
    print("   - 0xED: Server Command Response")
    print("   - 0xEE: Server Command Response")
    print("   - 0xEF: Server Command Response")
    print("   - 0xF0: Server Command Response")
    print("   - 0xF1: Server Command Response")
    print("   - 0xF2: Server Command Response")
    print("   - 0xF3: Server Command Response")
    print("   - 0xF4: Server Command Response")
    print("   - 0xF5: Server Command Response")
    print("   - 0xF6: Server Command Response")
    print("   - 0xF7: Server Command Response")
    print("   - 0xF8: Server Command Response")
    print("   - 0xF9: Server Command Response")
    print("   - 0xFA: Server Command Response")
    print("   - 0xFB: Server Command Response")
    print("   - 0xFC: Server Command Response")
    print("   - 0xFD: Server Command Response")
    print("   - 0xFE: Server Command Response")
    print("   - 0xFF: Server Command Response")
    
    print("\n3. ESTRUCTURA DEL PAQUETE DE LOGIN (0x01):")
    print("   - Length: 0x0D (13 bytes)")
    print("   - Protocol: 0x01")
    print("   - IMEI: 8 bytes")
    print("   - Serial: 2 bytes")
    print("   - Error check: 2 bytes")
    print("   - CRC: 2 bytes")
    print("   - End: 0D 0A")
    print("   - Total: 19 bytes")
    
    print("\n4. ESTRUCTURA DEL ACK DE LOGIN:")
    print("   - Length: 0x05 (5 bytes)")
    print("   - Protocol: 0x01")
    print("   - Serial: 2 bytes (mismo que en login)")
    print("   - CRC: 2 bytes")
    print("   - End: 0D 0A")
    print("   - Total: 11 bytes")
    
    print("\n5. ESTRUCTURA DEL PAQUETE DE POSICIÓN (0x12):")
    print("   - Length: variable")
    print("   - Protocol: 0x12")
    print("   - Date/Time: 6 bytes (BCD)")
    print("   - Quantity: 1 byte")
    print("   - Latitude: 4 bytes")
    print("   - Longitude: 4 bytes")
    print("   - Speed: 1 byte")
    print("   - Course: 2 bytes")
    print("   - Status: 1 byte")
    print("   - Serial: 2 bytes")
    print("   - CRC: 2 bytes")
    print("   - End: 0D 0A")
    
    print("\n6. ALGORITMO CRC:")
    print("   - Polinomio: 0x1021 (CRC-CCITT)")
    print("   - Valor inicial: 0xFFFF")
    print("   - XOR final: 0xFFFF")
    print("   - Byte order: Big-endian (MSB first)")

def test_ack_formats():
    """
    Prueba diferentes formatos de ACK según especificaciones
    """
    print("\n=== PRUEBA DE FORMATOS DE ACK ===")
    
    # Serial de ejemplo
    serial = b'\x00\x01'
    
    print(f"Serial de prueba: {serial.hex()}")
    
    # Formato 1: ACK estándar GT06 (longitud 05)
    ack_data_1 = b'\x05\x01' + serial
    crc_1 = crc16_itu_factory_bytes_be(ack_data_1)
    ack_1 = b'\x78\x78' + ack_data_1 + crc_1 + b'\x0D\x0A'
    print(f"ACK formato 1 (longitud 05): {ack_1.hex()}")
    print(f"  - Longitud real: {len(ack_1)} bytes")
    print(f"  - Longitud esperada: {ack_data_1[0] + 6} bytes")
    
    # Formato 2: ACK con longitud 04
    ack_data_2 = b'\x04\x01' + serial
    crc_2 = crc16_itu_factory_bytes_be(ack_data_2)
    ack_2 = b'\x78\x78' + ack_data_2 + crc_2 + b'\x0D\x0A'
    print(f"ACK formato 2 (longitud 04): {ack_2.hex()}")
    print(f"  - Longitud real: {len(ack_2)} bytes")
    print(f"  - Longitud esperada: {ack_data_2[0] + 6} bytes")
    
    # Formato 3: ACK con longitud 03
    ack_data_3 = b'\x03\x01' + serial
    crc_3 = crc16_itu_factory_bytes_be(ack_data_3)
    ack_3 = b'\x78\x78' + ack_data_3 + crc_3 + b'\x0D\x0A'
    print(f"ACK formato 3 (longitud 03): {ack_3.hex()}")
    print(f"  - Longitud real: {len(ack_3)} bytes")
    print(f"  - Longitud esperada: {ack_data_3[0] + 6} bytes")
    
    return [ack_1, ack_2, ack_3]

def analyze_example_packets():
    """
    Analiza paquetes de ejemplo del manual
    """
    print("\n=== ANÁLISIS DE PAQUETES DE EJEMPLO ===")
    
    # Ejemplo del manual
    print("Ejemplo del manual:")
    print("Login packet: 78 78 0D 01 03 53 41 35 32 15 03 62 00 02 2D 06 0D 0A")
    print("ACK packet:   78 78 05 01 00 02 EB 47 0D 0A")
    
    # Analizar paquete de login
    login_packet = bytes.fromhex("78780d01035341353215036200022d060d0a")
    print(f"\nPaquete de login: {login_packet.hex()}")
    print(f"Longitud: {len(login_packet)} bytes")
    print(f"Header: {login_packet[0:2].hex()}")
    print(f"Length byte: {login_packet[2]:02X} ({login_packet[2]})")
    print(f"Protocol: {login_packet[3]:02X}")
    print(f"IMEI: {login_packet[4:12].hex()}")
    print(f"Serial: {login_packet[12:14].hex()}")
    print(f"Error check: {login_packet[14:16].hex()}")
    print(f"CRC: {login_packet[16:18].hex()}")
    print(f"End: {login_packet[18:20].hex()}")
    
    # Analizar paquete de ACK
    ack_packet = bytes.fromhex("787805010002eb470d0a")
    print(f"\nPaquete de ACK: {ack_packet.hex()}")
    print(f"Longitud: {len(ack_packet)} bytes")
    print(f"Header: {ack_packet[0:2].hex()}")
    print(f"Length byte: {ack_packet[2]:02X} ({ack_packet[2]})")
    print(f"Protocol: {ack_packet[3]:02X}")
    print(f"Serial: {ack_packet[4:6].hex()}")
    print(f"CRC: {ack_packet[6:8].hex()}")
    print(f"End: {ack_packet[8:10].hex()}")
    
    # Verificar CRC del ACK
    ack_data = ack_packet[2:-4]  # Sin header y sin CRC + end
    expected_crc = crc16_itu_factory_bytes_be(ack_data)
    received_crc = ack_packet[6:8]
    print(f"\nVerificación CRC:")
    print(f"ACK data: {ack_data.hex()}")
    print(f"CRC esperado: {expected_crc.hex()}")
    print(f"CRC recibido: {received_crc.hex()}")
    print(f"¿Coincide?: {'SÍ' if expected_crc == received_crc else 'NO'}")

def main():
    print("ANÁLISIS DE ESPECIFICACIONES DEL PROTOCOLO GT06")
    print("=" * 60)
    
    # Analizar especificaciones
    analyze_gt06_specifications()
    
    # Probar formatos de ACK
    ack_formats = test_ack_formats()
    
    # Analizar paquetes de ejemplo
    analyze_example_packets()
    
    print("\n" + "=" * 60)
    print("CONCLUSIONES:")
    print("1. El ACK debe tener longitud 05 según el manual")
    print("2. El CRC debe calcularse sobre los datos (length + protocol + serial)")
    print("3. El formato correcto es: 7878 + 05 + 01 + serial + CRC + 0D0A")
    print("4. El CRC debe ser big-endian (MSB first)")

if __name__ == "__main__":
    main()
