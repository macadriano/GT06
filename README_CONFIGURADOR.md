# Configurador de Modo Directo - GT06

## Descripción

Este script permite configurar dispositivos GT06 para que envíen datos directamente sin necesidad de login previo, cambiando de **modo login** a **modo transmisión continua**.

## ¿Qué hace?

1. **Espera la conexión** del dispositivo GT06
2. **Procesa el login inicial** del dispositivo
3. **Envía un comando** para cambiar a modo directo
4. **Confirma** que el dispositivo aceptó el cambio
5. **Registra todo** en un archivo de log

## Uso

### 1. Ejecutar el configurador:
```bash
python configurador_modo_directo.py
```

### 2. Conectar el dispositivo:
- El dispositivo debe conectarse al puerto **5004** (diferente al servidor principal)
- El configurador esperará la conexión automáticamente

### 3. Proceso automático:
```
Dispositivo → Configurador: Login (0x01)
Configurador → Dispositivo: ACK de login
Configurador → Dispositivo: Comando modo directo (0x80)
Dispositivo → Configurador: Confirmación (posición/estado/heartbeat)
```

### 4. Resultado:
- Si es exitoso: "¡Configuración completada exitosamente!"
- El dispositivo ahora está en modo directo
- Puedes desconectarlo y conectarlo al servidor principal

## Configuración

### Puerto del servidor:
```python
HOST = '200.58.98.187'
PORT = 5004  # Puerto diferente al servidor principal
```

### Comando de configuración:
```python
DIRECT_MODE_COMMAND = b"MODE,1#"
```

**Nota**: Ajusta este comando según el manual de tu fabricante específico.

## Logs

El script genera logs detallados en `configurador_modo_directo.txt`:

```
2025-01-18 22:45:30 === CONFIGURADOR DE MODO DIRECTO ===
2025-01-18 22:45:30 Servidor iniciado en 200.58.98.187:5004
2025-01-18 22:45:30 Comando a enviar: MODE,1#
2025-01-18 22:45:30 Esperando conexión del dispositivo...
2025-01-18 22:45:35 Conexión entrante desde ('170.51.139.249', 49315)
2025-01-18 22:45:35 Iniciando proceso de configuración...
2025-01-18 22:45:35 [RECIBIDO] 78780d0108694120766681330081f8470d0a
2025-01-18 22:45:35 [LOGIN] IMEI: 0869412076668133
2025-01-18 22:45:35 [LOGIN] Serial: 0081
2025-01-18 22:45:35 [ENVIADO] 7878050100815dd40d0a
2025-01-18 22:45:35 [LOGIN] ACK enviado exitosamente
2025-01-18 22:45:37 [CMD] Enviando comando de modo directo (itu_be): 78780a804d4f44452c31230081a1b20d0a
2025-01-18 22:45:37 [CMD] Comando ASCII: MODE,1#
2025-01-18 22:45:37 [ENVIADO] 78780a804d4f44452c31230081a1b20d0a
2025-01-18 22:45:37 [CMD] Comando enviado exitosamente
2025-01-18 22:45:37 [CONFIRMACION] Esperando respuesta del dispositivo (timeout: 30s)
2025-01-18 22:45:40 [RECIBIDO] 78780a13450601000100825da20d0a
2025-01-18 22:45:40 [INFO] Dispositivo envió estado - posible confirmación
2025-01-18 22:45:40 [SUCCESS] ¡Configuración completada exitosamente!
2025-01-18 22:45:40 [SUCCESS] El dispositivo ahora está en modo directo
2025-01-18 22:45:40 [SUCCESS] Puedes desconectarlo y conectarlo al servidor principal
```

## Comandos Alternativos

Si el comando `MODE,1#` no funciona con tu dispositivo, prueba estos comandos alternativos:

### Opción 1: Comando de parámetro
```python
DIRECT_MODE_COMMAND = b"PARAM,0001,01#"
```

### Opción 2: Comando de configuración
```python
DIRECT_MODE_COMMAND = b"CONFIG,TRANSMODE,1#"
```

### Opción 3: Comando específico del fabricante
```python
DIRECT_MODE_COMMAND = b"SETMODE,CONTINUOUS#"
```

## Troubleshooting

### El dispositivo no responde al comando:
1. Verifica que el comando sea correcto para tu fabricante
2. Revisa el manual del dispositivo
3. Prueba comandos alternativos

### Error de CRC:
- El script detecta automáticamente el tipo de CRC (LE/BE)
- Si hay problemas, revisa los logs de debug

### Timeout en confirmación:
- El dispositivo puede tardar más de 30 segundos
- Aumenta el timeout en la función `wait_for_confirmation()`

## Integración con el Servidor Principal

Una vez configurado el dispositivo:

1. **Desconecta** el dispositivo del configurador
2. **Conecta** el dispositivo al servidor principal (puerto 5003)
3. **El servidor principal** detectará automáticamente el modo directo
4. **No necesitarás** configurar nada más

## Ventajas del Modo Directo

- ✅ **Menor latencia**: Sin overhead de login
- ✅ **Mayor eficiencia**: Menos paquetes de protocolo
- ✅ **Mejor para alarmas**: Respuesta inmediata en emergencias
- ✅ **Compatibilidad**: Funciona con dispositivos configurados para transmisión continua

## Notas Importantes

- El configurador usa el **puerto 5004** para no interferir con el servidor principal
- Solo se puede configurar **un dispositivo a la vez**
- El proceso es **automático** una vez que el dispositivo se conecta
- Los logs se guardan en `configurador_modo_directo.txt`
