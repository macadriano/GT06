#!/usr/bin/env python3
"""
Análisis de diferentes variantes en la estructura de datos del ACK GT06
"""

# Tabla CRC-ITU del fabricante
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
    fcs = 0xFFFF
    for byte in data:
        fcs = (fcs >> 8) ^ CRC_TAB16[(fcs ^ byte) & 0xFF]
    return ~fcs & 0xFFFF

def crc16_itu_factory_bytes_be(data):
    crc = crc16_itu_factory(data)
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def crc16_itu_factory_bytes_le(data):
    crc = crc16_itu_factory(data)
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def generate_ack_variants(serial):
    """
    Genera todas las posibles variantes del ACK basadas en diferentes interpretaciones
    del protocolo GT06
    """
    variants = {}
    
    # Serial de ejemplo del manual: 0002
    # ACK del manual: 7878 05 01 00 02 EB 47 0D 0A
    
    print("=== ANÁLISIS DE VARIANTES DE ACK ===")
    print(f"Serial de prueba: {serial.hex()}")
    print()
    
    # 1. ACK ESTÁNDAR (como lo hemos estado usando)
    # 7878 + 05 + 01 + serial + CRC + 0D0A
    ack_data = b'\x05\x01' + serial
    crc_be = crc16_itu_factory_bytes_be(ack_data)
    ack_standard = b'\x78\x78' + ack_data + crc_be + b'\x0D\x0A'
    variants['standard'] = ack_standard
    print(f"1. ACK ESTÁNDAR:")
    print(f"   Data: {ack_data.hex()}")
    print(f"   CRC (BE): {crc_be.hex()}")
    print(f"   ACK completo: {ack_standard.hex()}")
    print(f"   Formato: 78 78 05 01 {serial.hex()} {crc_be.hex()} 0D 0A")
    print()
    
    # 2. ACK CON LONGITUD 03 (algunos protocolos usan esto)
    # 7878 + 03 + 01 + serial + CRC + 0D0A
    ack_data_03 = b'\x03\x01' + serial
    crc_03 = crc16_itu_factory_bytes_be(ack_data_03)
    ack_03 = b'\x78\x78' + ack_data_03 + crc_03 + b'\x0D\x0A'
    variants['length_03'] = ack_03
    print(f"2. ACK CON LONGITUD 03:")
    print(f"   Data: {ack_data_03.hex()}")
    print(f"   CRC (BE): {crc_03.hex()}")
    print(f"   ACK completo: {ack_03.hex()}")
    print(f"   Formato: 78 78 03 01 {serial.hex()} {crc_03.hex()} 0D 0A")
    print()
    
    # 3. ACK CON LONGITUD 04 (otra variante común)
    # 7878 + 04 + 01 + serial + CRC + 0D0A
    ack_data_04 = b'\x04\x01' + serial
    crc_04 = crc16_itu_factory_bytes_be(ack_data_04)
    ack_04 = b'\x78\x78' + ack_data_04 + crc_04 + b'\x0D\x0A'
    variants['length_04'] = ack_04
    print(f"3. ACK CON LONGITUD 04:")
    print(f"   Data: {ack_data_04.hex()}")
    print(f"   CRC (BE): {crc_04.hex()}")
    print(f"   ACK completo: {ack_04.hex()}")
    print(f"   Formato: 78 78 04 01 {serial.hex()} {crc_04.hex()} 0D 0A")
    print()
    
    # 4. ACK CON PROTOCOLO 00 (en lugar de 01)
    # 7878 + 05 + 00 + serial + CRC + 0D0A
    ack_data_proto00 = b'\x05\x00' + serial
    crc_proto00 = crc16_itu_factory_bytes_be(ack_data_proto00)
    ack_proto00 = b'\x78\x78' + ack_data_proto00 + crc_proto00 + b'\x0D\x0A'
    variants['protocol_00'] = ack_proto00
    print(f"4. ACK CON PROTOCOLO 00:")
    print(f"   Data: {ack_data_proto00.hex()}")
    print(f"   CRC (BE): {crc_proto00.hex()}")
    print(f"   ACK completo: {ack_proto00.hex()}")
    print(f"   Formato: 78 78 05 00 {serial.hex()} {crc_proto00.hex()} 0D 0A")
    print()
    
    # 5. ACK CON PROTOCOLO 02 (otra variante)
    # 7878 + 05 + 02 + serial + CRC + 0D0A
    ack_data_proto02 = b'\x05\x02' + serial
    crc_proto02 = crc16_itu_factory_bytes_be(ack_data_proto02)
    ack_proto02 = b'\x78\x78' + ack_data_proto02 + crc_proto02 + b'\x0D\x0A'
    variants['protocol_02'] = ack_proto02
    print(f"5. ACK CON PROTOCOLO 02:")
    print(f"   Data: {ack_data_proto02.hex()}")
    print(f"   CRC (BE): {crc_proto02.hex()}")
    print(f"   ACK completo: {ack_proto02.hex()}")
    print(f"   Formato: 78 78 05 02 {serial.hex()} {crc_proto02.hex()} 0D 0A")
    print()
    
    # 6. ACK CON CRC LITTLE-ENDIAN
    crc_le = crc16_itu_factory_bytes_le(ack_data)
    ack_le = b'\x78\x78' + ack_data + crc_le + b'\x0D\x0A'
    variants['le_crc'] = ack_le
    print(f"6. ACK CON CRC LITTLE-ENDIAN:")
    print(f"   Data: {ack_data.hex()}")
    print(f"   CRC (LE): {crc_le.hex()}")
    print(f"   ACK completo: {ack_le.hex()}")
    print(f"   Formato: 78 78 05 01 {serial.hex()} {crc_le.hex()} 0D 0A")
    print()
    
    # 7. ACK SIN CRC (solo para pruebas)
    ack_no_crc = b'\x78\x78' + ack_data + b'\x00\x00' + b'\x0D\x0A'
    variants['no_crc'] = ack_no_crc
    print(f"7. ACK SIN CRC (solo pruebas):")
    print(f"   Data: {ack_data.hex()}")
    print(f"   CRC: 0000")
    print(f"   ACK completo: {ack_no_crc.hex()}")
    print(f"   Formato: 78 78 05 01 {serial.hex()} 00 00 0D 0A")
    print()
    
    # 8. ACK CON SERIAL INVERTIDO (little-endian)
    serial_le = bytes(reversed(serial))
    ack_data_le_serial = b'\x05\x01' + serial_le
    crc_le_serial = crc16_itu_factory_bytes_be(ack_data_le_serial)
    ack_le_serial = b'\x78\x78' + ack_data_le_serial + crc_le_serial + b'\x0D\x0A'
    variants['le_serial'] = ack_le_serial
    print(f"8. ACK CON SERIAL LITTLE-ENDIAN:")
    print(f"   Data: {ack_data_le_serial.hex()}")
    print(f"   CRC (BE): {crc_le_serial.hex()}")
    print(f"   ACK completo: {ack_le_serial.hex()}")
    print(f"   Formato: 78 78 05 01 {serial_le.hex()} {crc_le_serial.hex()} 0D 0A")
    print()
    
    # 9. ACK CON BYTE EXTRA (algunos protocolos usan un byte adicional)
    # 7878 + 06 + 01 + 00 + serial + CRC + 0D0A
    ack_data_extra = b'\x06\x01\x00' + serial
    crc_extra = crc16_itu_factory_bytes_be(ack_data_extra)
    ack_extra = b'\x78\x78' + ack_data_extra + crc_extra + b'\x0D\x0A'
    variants['extra_byte'] = ack_extra
    print(f"9. ACK CON BYTE EXTRA:")
    print(f"   Data: {ack_data_extra.hex()}")
    print(f"   CRC (BE): {crc_extra.hex()}")
    print(f"   ACK completo: {ack_extra.hex()}")
    print(f"   Formato: 78 78 06 01 00 {serial.hex()} {crc_extra.hex()} 0D 0A")
    print()
    
    # 10. ACK CON LONGITUD CALCULADA (longitud real de datos)
    # La longitud real es: protocol(1) + serial(2) = 3 bytes
    ack_data_real_len = b'\x03\x01' + serial
    crc_real_len = crc16_itu_factory_bytes_be(ack_data_real_len)
    ack_real_len = b'\x78\x78' + ack_data_real_len + crc_real_len + b'\x0D\x0A'
    variants['real_length'] = ack_real_len
    print(f"10. ACK CON LONGITUD REAL (3 bytes):")
    print(f"   Data: {ack_data_real_len.hex()}")
    print(f"   CRC (BE): {crc_real_len.hex()}")
    print(f"   ACK completo: {ack_real_len.hex()}")
    print(f"   Formato: 78 78 03 01 {serial.hex()} {crc_real_len.hex()} 0D 0A")
    print()
    
    # 11. ACK CON LONGITUD INCLUYENDO CRC (longitud total)
    # La longitud total es: protocol(1) + serial(2) + crc(2) = 5 bytes
    ack_data_total_len = b'\x05\x01' + serial
    crc_total_len = crc16_itu_factory_bytes_be(ack_data_total_len)
    ack_total_len = b'\x78\x78' + ack_data_total_len + crc_total_len + b'\x0D\x0A'
    variants['total_length'] = ack_total_len
    print(f"11. ACK CON LONGITUD TOTAL (5 bytes):")
    print(f"   Data: {ack_data_total_len.hex()}")
    print(f"   CRC (BE): {crc_total_len.hex()}")
    print(f"   ACK completo: {ack_total_len.hex()}")
    print(f"   Formato: 78 78 05 01 {serial.hex()} {crc_total_len.hex()} 0D 0A")
    print()
    
    # 12. ACK CON PROTOCOLO DE RESPUESTA (0x81 en lugar de 0x01)
    ack_data_resp = b'\x05\x81' + serial
    crc_resp = crc16_itu_factory_bytes_be(ack_data_resp)
    ack_resp = b'\x78\x78' + ack_data_resp + crc_resp + b'\x0D\x0A'
    variants['response_protocol'] = ack_resp
    print(f"12. ACK CON PROTOCOLO DE RESPUESTA (0x81):")
    print(f"   Data: {ack_data_resp.hex()}")
    print(f"   CRC (BE): {crc_resp.hex()}")
    print(f"   ACK completo: {ack_resp.hex()}")
    print(f"   Formato: 78 78 05 81 {serial.hex()} {crc_resp.hex()} 0D 0A")
    print()
    
    return variants

def verify_manual_example():
    """
    Verifica el ejemplo del manual para confirmar cuál variante es correcta
    """
    print("=== VERIFICACIÓN CON EJEMPLO DEL MANUAL ===")
    print("Ejemplo del manual:")
    print("Login: 78 78 0D 01 03 53 41 35 32 15 03 62 00 02 2D 06 0D 0A")
    print("ACK:   78 78 05 01 00 02 EB 47 0D 0A")
    print()
    
    # Extraer serial del ejemplo del manual
    manual_serial = b'\x00\x02'
    manual_ack = b'\x78\x78\x05\x01\x00\x02\xEB\x47\x0D\x0A'
    
    print(f"Serial del manual: {manual_serial.hex()}")
    print(f"ACK del manual: {manual_ack.hex()}")
    print()
    
    # Generar todas las variantes para este serial
    variants = generate_ack_variants(manual_serial)
    
    print("=== COMPARACIÓN CON MANUAL ===")
    for name, ack in variants.items():
        if ack == manual_ack:
            print(f"✓ {name.upper()}: COINCIDE CON MANUAL")
        else:
            print(f"✗ {name.upper()}: NO COINCIDE")
            print(f"  Esperado: {manual_ack.hex()}")
            print(f"  Generado: {ack.hex()}")
        print()

if __name__ == "__main__":
    # Probar con serial de ejemplo
    test_serial = b'\x00\x01'
    generate_ack_variants(test_serial)
    
    print("\n" + "="*60 + "\n")
    
    # Verificar con ejemplo del manual
    verify_manual_example()
