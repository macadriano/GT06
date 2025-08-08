#!/usr/bin/env python3

def test_crc_algorithm(data, expected_crc, algorithm_name, crc_func):
    """Prueba un algoritmo de CRC específico"""
    calculated_crc = crc_func(data)
    matches = calculated_crc == expected_crc
    print(f"{algorithm_name:20} | {calculated_crc.hex():8} | {'✓' if matches else '✗'}")
    return matches

def crc16_modbus(data):
    """CRC16 Modbus (polinomio 0xA001, inicial 0xFFFF, little-endian)"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')

def crc16_modbus_be(data):
    """CRC16 Modbus Big-endian"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'big')

def crc16_ccitt(data):
    """CRC16 CCITT (polinomio 0x1021, inicial 0xFFFF)"""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc.to_bytes(2, 'big')

def crc16_ccitt_le(data):
    """CRC16 CCITT Little-endian"""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc.to_bytes(2, 'little')

def crc16_xmodem(data):
    """CRC16 XMODEM (polinomio 0x1021, inicial 0x0000)"""
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc.to_bytes(2, 'big')

def crc16_xmodem_le(data):
    """CRC16 XMODEM Little-endian"""
    crc = 0x0000
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc.to_bytes(2, 'little')

def crc16_kermit(data):
    """CRC16 Kermit (polinomio 0x1021, inicial 0x0000, byte order swapped)"""
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')

def crc16_kermit_be(data):
    """CRC16 Kermit Big-endian"""
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc.to_bytes(2, 'big')

def crc16_reverse(data):
    """CRC16 con bytes invertidos"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    # Invertir bytes
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

# Ejemplos del manual
example1_data = b'\x05\x01\x00\x02'
example1_expected = b'\xEB\x47'

example2_data = b'\x05\x01\x00\x01'
example2_expected = b'\xD9\xDC'

print("=== ANÁLISIS DE ALGORITMOS CRC CON EJEMPLOS DEL MANUAL ===\n")

# Lista de algoritmos a probar
algorithms = [
    ("CRC16 Modbus LE", crc16_modbus),
    ("CRC16 Modbus BE", crc16_modbus_be),
    ("CRC16 CCITT BE", crc16_ccitt),
    ("CRC16 CCITT LE", crc16_ccitt_le),
    ("CRC16 XMODEM BE", crc16_xmodem),
    ("CRC16 XMODEM LE", crc16_xmodem_le),
    ("CRC16 Kermit LE", crc16_kermit),
    ("CRC16 Kermit BE", crc16_kermit_be),
    ("CRC16 Reverse", crc16_reverse),
]

print("Ejemplo 1: ACK data = 05010002, CRC esperado = EB47")
print("Algoritmo" + " " * 12 + "| Calculado | Coincide")
print("-" * 50)

matches1 = []
for name, func in algorithms:
    if test_crc_algorithm(example1_data, example1_expected, name, func):
        matches1.append(name)

print(f"\nEjemplo 2: ACK data = 05010001, CRC esperado = D9DC")
print("Algoritmo" + " " * 12 + "| Calculado | Coincide")
print("-" * 50)

matches2 = []
for name, func in algorithms:
    if test_crc_algorithm(example2_data, example2_expected, name, func):
        matches2.append(name)

print(f"\n=== RESULTADOS ===")
print(f"Algoritmos que coinciden con Ejemplo 1: {matches1}")
print(f"Algoritmos que coinciden con Ejemplo 2: {matches2}")

# Encontrar algoritmos que coinciden con ambos ejemplos
common_matches = set(matches1) & set(matches2)
if common_matches:
    print(f"\n🎉 ¡ALGORITMO ENCONTRADO!")
    print(f"El algoritmo correcto es: {list(common_matches)[0]}")
else:
    print(f"\n❌ No se encontró un algoritmo que coincida con ambos ejemplos")
    print("Esto sugiere que el manual puede tener errores o usar un algoritmo no estándar") 