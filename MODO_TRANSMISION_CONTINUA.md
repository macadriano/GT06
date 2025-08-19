# Modo de Transmisión Continua (Sin Login) - GT06

## Descripción

El servidor ahora soporta **dos modos de operación** para dispositivos GT06:

1. **Modo Login** (tradicional): Dispositivo envía login → Servidor responde ACK → Dispositivo envía posición
2. **Modo Transmisión Continua** (nuevo): Dispositivo envía posición directamente sin login previo

## Detección Automática

El servidor detecta automáticamente el modo del dispositivo en el primer paquete recibido:

### Modo Login
```
Dispositivo → Servidor: 7878 + 0D + 01 + [IMEI] + [serial] + [error_check] + [CRC] + 0D0A
Servidor → Dispositivo: 7878 + 05 + 01 + [serial] + [CRC] + 0D0A
Dispositivo → Servidor: 7878 + [datos de posición] + [CRC] + 0D0A
```

### Modo Transmisión Continua
```
Dispositivo → Servidor: 7878 + [datos de posición] + [CRC] + 0D0A
Servidor → Dispositivo: 7878 + 05 + 01 + [serial] + [CRC] + 0D0A
```

## Tipos de Paquetes Soportados

### 1. Posición Directa (0x12)
- **Descripción**: Datos de ubicación GPS sin login previo
- **ACK**: Automático con CRC-ITU del fabricante (BE)
- **Serial**: Extraído del paquete o por defecto (0x0001)

### 2. Heartbeat Directo (0x23)
- **Descripción**: Señal de vida del dispositivo sin login previo
- **ACK**: Automático con CRC-ITU del fabricante (BE)
- **Serial**: Por defecto (0x0001)

### 3. Alarma Directa (0x26)
- **Descripción**: Alertas de emergencia sin login previo
- **Tipos de alarma**:
  - 0x01: SOS
  - 0x02: Batería baja
  - 0x03: Movimiento
  - 0x04: Geocerca
  - 0x05: Impacto
- **ACK**: Automático con CRC-ITU del fabricante (BE)
- **Serial**: Por defecto (0x0001)

## Configuración del Dispositivo

Para activar el modo de transmisión continua en el dispositivo GT06:

### Parámetro 0x0001: Modo de Transmisión
- **0x00**: Modo normal (requiere login)
- **0x01**: Modo de transmisión continua (sin login)

### Comando de Configuración
```
7878 + 01 + 27 + [IMEI] + 0001 + 01 + [CRC] + 0D0A
```

## Ventajas del Modo Transmisión Continua

1. **Menor latencia**: No hay overhead de login
2. **Mayor eficiencia**: Menos paquetes de protocolo
3. **Mejor para alarmas**: Respuesta inmediata en emergencias
4. **Compatibilidad**: Funciona con dispositivos configurados para transmisión continua

## Logs del Servidor

### Modo Login Detectado
```
[MODO] Dispositivo en modo login (0x01)
[LOGIN] IMEI: 0869412076668133
[LOGIN] Serial: 0081
```

### Modo Transmisión Continua Detectado
```
[MODO] Dispositivo en modo transmisión continua (0x12)
[POSICION_DIRECTA] Dispositivo enviando posición sin login previo
[POSICION_DIRECTA] Serial extraído del paquete: 0081
[SUCCESS] ACK enviado para posición directa
```

## Compatibilidad

El servidor es **completamente compatible** con ambos modos:
- Detecta automáticamente el modo del dispositivo
- Maneja correctamente los ACKs para cada modo
- Mantiene la funcionalidad existente para dispositivos con login
- Agrega soporte transparente para dispositivos sin login

## Uso

No se requiere configuración adicional. El servidor maneja automáticamente ambos modos según el primer paquete recibido de cada dispositivo.
