# Correcciones al Formato de ACK GT06

## Problema Identificado

El análisis de las especificaciones del protocolo GT06 reveló que estábamos usando un formato de ACK incorrecto.

## Formato Incorrecto (Anterior)
```
ACK data: b'\x04\x01' + serial
Formato: 7878 + 04 + 01 + serial + CRC + 0D0A
Longitud total: 10 bytes
```

## Formato Correcto (Según Especificaciones)
```
ACK data: b'\x05\x01' + serial
Formato: 7878 + 05 + 01 + serial + CRC + 0D0A
Longitud total: 11 bytes
```

## Verificación con Ejemplo del Manual

**Ejemplo del manual:**
- Login packet: `78 78 0D 01 03 53 41 35 32 15 03 62 00 02 2D 06 0D 0A`
- ACK packet: `78 78 05 01 00 02 EB 47 0D 0A`

**Análisis del ACK:**
- Length byte: `05` (5 bytes)
- Protocol: `01`
- Serial: `00 02`
- CRC: `EB 47`
- End: `0D 0A`
- Total: 11 bytes

## Correcciones Aplicadas

### 1. GT06_TRACKER.PY
- ✅ `handle_login`: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`
- ✅ `send_alternative_ack`: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`
- ✅ `handle_position_direct`: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`
- ✅ `handle_heartbeat_direct`: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`
- ✅ `handle_alarm_direct`: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`
- ✅ ACK para estado: Cambiado de `b'\x04\x01'` a `b'\x05\x01'`

### 2. GT06_TRACKER_CORRECTED.py
- ✅ Nuevo servidor con formato correcto desde el inicio
- ✅ Función `send_correct_ack()` implementada
- ✅ Validación de CRC mejorada
- ✅ Puerto 4997 para pruebas

### 3. test_gt06_protocol_variants.py
- ✅ Script de prueba con múltiples variantes de ACK
- ✅ Puerto 4996 para pruebas
- ✅ Análisis detallado de estructura de paquetes

## Especificaciones del Protocolo GT06

### Estructura General del Paquete
```
Header: 78 78 (2 bytes)
Length: 1 byte (longitud de los datos)
Protocol: 1 byte (tipo de paquete)
Data: N bytes (datos específicos del protocolo)
CRC: 2 bytes (checksum)
End: 0D 0A (2 bytes)
Total: 6 + length bytes
```

### Tipos de Paquetes Principales
- `0x01`: Login Information
- `0x12`: Location Data
- `0x13`: Status Information
- `0x23`: Heartbeat
- `0x26`: Alarm Data
- `0x80`: Server Command

### Algoritmo CRC
- **Polinomio**: 0x1021 (CRC-CCITT)
- **Valor inicial**: 0xFFFF
- **XOR final**: 0xFFFF
- **Byte order**: Big-endian (MSB first)

## Archivos Creados/Modificados

1. **GT06_TRACKER.PY** - Servidor principal corregido
2. **GT06_TRACKER_CORRECTED.py** - Versión corregida para pruebas
3. **test_gt06_protocol_variants.py** - Script de prueba de variantes
4. **analyze_gt06_specifications.py** - Análisis de especificaciones
5. **GT06_TRACKER_ALTERNATIVE.py** - Versión alternativa con múltiples estrategias

## Próximos Pasos

1. **Probar GT06_TRACKER_CORRECTED.py** en puerto 4997
2. **Monitorear logs** para verificar si el dispositivo envía posición (0x12)
3. **Si funciona**, aplicar las correcciones al servidor principal
4. **Si no funciona**, continuar con el análisis de otras variantes

## Comandos para Probar

```bash
# Probar servidor corregido
python GT06_TRACKER_CORRECTED.py

# Probar variantes de protocolo
python test_gt06_protocol_variants.py

# Analizar especificaciones
python analyze_gt06_specifications.py
```

## Logs a Monitorear

- `datosChino_corrected.txt` - Servidor corregido
- `test_protocol_variants.txt` - Pruebas de variantes
- `datosChino_alt.txt` - Versión alternativa

## Estado Actual

- ✅ Formato de ACK corregido según especificaciones
- ✅ CRC-ITU del fabricante implementado correctamente
- ✅ Múltiples estrategias de prueba disponibles
- 🔄 Pendiente: Verificar si el dispositivo reconoce el ACK correcto
