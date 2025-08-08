#!/usr/bin/env python3

def crc16_modbus_le(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_modbus_be(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def crc16_ccitt(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def crc16_ccitt_le(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_xmodem(data):
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def crc16_xmodem_le(data):
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_kermit(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def crc16_kermit_be(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def crc16_gt06_official(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def test_custom_crc(data, init_val, polynomial, byte_order='le'):
    crc = init_val
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
        crc &= 0xFFFF
    
    if byte_order == 'le':
        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    else:
        return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

if __name__ == "__main__":
    # Datos del ACK del log del fabricante
    ack_data = b'\x05\x01\x00\x2F'
    expected_crc = b'\x11\xA0'
    
    print('=== ANÁLISIS DEL LOG DEL FABRICANTE ===')
    print(f'ACK data: {ack_data.hex()}')
    print(f'Expected CRC: {expected_crc.hex()}')
    print()
    
    # Algoritmos estándar
    algorithms = [
        ('Modbus LE', crc16_modbus_le),
        ('Modbus BE', crc16_modbus_be),
        ('CCITT', crc16_ccitt),
        ('CCITT LE', crc16_ccitt_le),
        ('XMODEM', crc16_xmodem),
        ('XMODEM LE', crc16_xmodem_le),
        ('Kermit', crc16_kermit),
        ('Kermit BE', crc16_kermit_be),
        ('GT06 Official', crc16_gt06_official)
    ]
    
    print('Resultados de algoritmos estándar:')
    found_standard = False
    for name, func in algorithms:
        result = func(ack_data)
        match = '✓' if result == expected_crc else '✗'
        print(f'{name:12}: {result.hex()} {match}')
        if result == expected_crc:
            found_standard = True
            print(f'  ¡ENCONTRADO! Algoritmo: {name}')
    
    if not found_standard:
        print('\n=== PROBANDO VARIANTES ESPECIALES ===')
        
        # Variantes con diferentes valores iniciales y polinomios
        init_values = [0x0000, 0xFFFF, 0x8408, 0xA001, 0x1021]
        polynomials = [0x1021, 0x8408, 0xA001, 0x8005, 0x800D]
        
        for init_val in init_values:
            for poly in polynomials:
                # Little-endian
                result_le = test_custom_crc(ack_data, init_val, poly, 'le')
                if result_le == expected_crc:
                    print(f'✓ ENCONTRADO: Init={init_val:04X}, Poly={poly:04X}, LE: {result_le.hex()}')
                
                # Big-endian
                result_be = test_custom_crc(ack_data, init_val, poly, 'be')
                if result_be == expected_crc:
                    print(f'✓ ENCONTRADO: Init={init_val:04X}, Poly={poly:04X}, BE: {result_be.hex()}')
    
    print('\n=== CONCLUSIÓN ===')
    if found_standard:
        print('Se encontró un algoritmo estándar que coincide con el log del fabricante.')
    else:
        print('No se encontró coincidencia con algoritmos estándar.')
        print('Es posible que el fabricante use un algoritmo CRC personalizado.') 