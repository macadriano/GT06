#!/usr/bin/env python3

def crc16_modbus_le(data):
    """CRC16 Modbus Little-endian"""
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

def crc16_kermit(data):
    """CRC16 Kermit"""
    crc = 0x0000
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')

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
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

# Ejemplos del manual
example1_data = b'\x05\x01\x00\x02'
example1_expected = b'\xEB\x47'

example2_data = b'\x05\x01\x00\x01'
example2_expected = b'\xD9\xDC'

print("=== ANÁLISIS CRC CON EJEMPLOS DEL MANUAL ===")
print()

print("Ejemplo 1: ACK data = 05010002, CRC esperado = EB47")
print("Algoritmo" + " " * 15 + "| Calculado | Coincide")
print("-" * 55)

algorithms = [
    ("CRC16 Modbus LE", crc16_modbus_le),
    ("CRC16 Modbus BE", crc16_modbus_be),
    ("CRC16 Kermit", crc16_kermit),
    ("CRC16 Reverse", crc16_reverse),
]

matches1 = []
for name, func in algorithms:
    calculated = func(example1_data)
    matches = calculated == example1_expected
    print(f"{name:20} | {calculated.hex():8} | {'✓' if matches else '✗'}")
    if matches:
        matches1.append(name)

print(f"\nEjemplo 2: ACK data = 05010001, CRC esperado = D9DC")
print("Algoritmo" + " " * 15 + "| Calculado | Coincide")
print("-" * 55)

matches2 = []
for name, func in algorithms:
    calculated = func(example2_data)
    matches = calculated == example2_expected
    print(f"{name:20} | {calculated.hex():8} | {'✓' if matches else '✗'}")
    if matches:
        matches2.append(name)

print(f"\n=== RESULTADOS ===")
print(f"Coinciden con Ejemplo 1: {matches1}")
print(f"Coinciden con Ejemplo 2: {matches2}")

common = set(matches1) & set(matches2)
if common:
    print(f"\n🎉 ¡ALGORITMO ENCONTRADO: {list(common)[0]}!")
else:
    print(f"\n❌ No se encontró algoritmo que coincida con ambos ejemplos") 