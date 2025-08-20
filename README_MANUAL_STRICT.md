# GT06_MANUAL_STRICT - Implementación Estricta del Manual del Fabricante

## Propósito

Este módulo implementa **EXACTAMENTE** las especificaciones del manual del fabricante del dispositivo GT06, sin ninguna interpretación adicional o variantes experimentales. Se basa únicamente en el ejemplo documentado en el punto 5.1.3 del manual.

## Características Principales

### 1. Implementación Estricta del ACK
- **Estructura exacta**: `7878 + 05 + 01 + serial + CRC + 0D0A`
- **CRC del fabricante**: Utiliza la tabla CRC-ITU proporcionada en el apéndice del manual
- **Sin variantes**: No prueba diferentes formatos, solo el especificado oficialmente

### 2. Análisis Completo de Paquetes
- **Todos los paquetes**: Analiza y loguea cada byte recibido
- **Verificación de CRC**: Calcula y verifica el CRC de cada paquete
- **Estructura detallada**: Muestra la composición completa de cada mensaje

### 3. Logging Detallado
- **Archivo**: `datosChino_manual_strict.txt`
- **Formato**: Timestamp + etiqueta + información detallada
- **Etiquetas**: `[MANUAL_ACK]`, `[MANUAL_LOGIN]`, `[MANUAL_PACKET]`, etc.

## Ejemplo del Manual (Punto 5.1.3)

```
Login packet: 78 78 0D 01 03 53 41 35 32 15 03 62 00 02 2D 06 0D 0A
ACK response: 78 78 05 01 00 02 EB 47 0D 0A
```

### Análisis del ACK
- **7878**: Inicio del paquete
- **05**: Longitud del payload (5 bytes)
- **01**: Protocolo de respuesta
- **0002**: Serial del dispositivo
- **EB47**: CRC calculado
- **0D0A**: Fin del paquete

## Uso

### Puerto
- **Puerto**: 5007 (diferente a otros módulos para evitar conflictos)

### Ejecución
```bash
python GT06_MANUAL_STRICT.py
```

### Configuración del Dispositivo
El dispositivo GPS debe estar configurado para enviar datos al puerto 5007 de tu servidor.

## Ventajas de este Enfoque

1. **Fidelidad al Manual**: Implementa exactamente lo que especifica el fabricante
2. **Sin Interpretaciones**: No hay suposiciones sobre variantes o modificaciones
3. **Debugging Completo**: Muestra cada byte y cálculo para verificación
4. **Base de Referencia**: Sirve como implementación de referencia para comparar con otros módulos

## Diferencias con Otros Módulos

| Característica | GT06_TRACKER_NEW | GT06_MANUAL_STRICT |
|----------------|-------------------|-------------------|
| **Variantes de ACK** | 6 variantes experimentales | Solo 1 (manual) |
| **CRC** | Múltiples algoritmos | Solo CRC-ITU del fabricante |
| **Enfoque** | Experimental | Estricto al manual |
| **Puerto** | 5006 | 5007 |
| **Log** | `datosChino_new.txt` | `datosChino_manual_strict.txt` |

## Casos de Uso

### 1. Verificación del Manual
- Confirmar que las especificaciones del manual son correctas
- Validar que el CRC del fabricante funciona

### 2. Comparación con Implementaciones Experimentales
- Contrastar resultados con módulos que prueban variantes
- Identificar si el problema está en la implementación o en el dispositivo

### 3. Debugging de Protocolo
- Analizar cada byte del intercambio de mensajes
- Verificar la estructura exacta de los paquetes

## Estructura del Log

```
2025-08-19 22:50:00 [MANUAL] ==========================================
2025-08-19 22:50:00 [MANUAL] SERVIDOR GT06 - IMPLEMENTACIÓN MANUAL ESTRICTA
2025-08-19 22:50:00 [MANUAL] Basado ÚNICAMENTE en especificaciones del fabricante
2025-08-19 22:50:00 [MANUAL] Puerto: 5007
2025-08-19 22:50:00 [MANUAL] Archivo de log: datosChino_manual_strict.txt
2025-08-19 22:50:00 [MANUAL] ==========================================
2025-08-19 22:50:00 [MANUAL] Servidor iniciado en 0.0.0.0:5007
2025-08-19 22:50:00 [MANUAL] Esperando conexiones...
```

## Expectativas

Si el dispositivo GPS sigue las especificaciones del manual:
1. **Login**: Debería enviar paquete tipo 0x01
2. **ACK**: El servidor responde con formato exacto del manual
3. **Posición**: El dispositivo debería enviar paquete tipo 0x12 después del ACK

Si esto no funciona, el problema está en:
- Configuración del dispositivo
- Versión del firmware
- Interpretación incorrecta del manual
- Requisitos adicionales no documentados

## Próximos Pasos

1. **Ejecutar** este módulo en puerto 5007
2. **Configurar** el dispositivo GPS para enviar a puerto 5007
3. **Analizar** los logs para ver el intercambio exacto de mensajes
4. **Comparar** con los resultados de otros módulos experimentales

Este módulo nos dará la línea base exacta para determinar si el problema está en nuestra implementación o en el dispositivo.
