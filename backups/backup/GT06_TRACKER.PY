import socket
import datetime

def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='big')

def parse_imei(data):
    imei_bcd = data[4:12]
    imei = ''.join(f'{(b & 0xF0) >> 4}{b & 0x0F}' for b in imei_bcd).lstrip('0')
    return imei

def decode_position_data(data):
    if len(data) < 28:
        print("Datos de posición incompletos")
        return

    # Fecha y hora
    year = 2000 + data[4]
    month = data[5]
    day = data[6]
    hour = data[7]
    minute = data[8]
    second = data[9]

    timestamp = f'{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'

    # Latitud y longitud
    lat_raw = int.from_bytes(data[11:15], 'big')
    lon_raw = int.from_bytes(data[15:19], 'big')
    lat = lat_raw / 1800000
    lon = lon_raw / 1800000

    # Velocidad
    speed = data[19]

    # Rumbo (Course)
    course = ((data[20] & 0x7F) << 8) | data[21]

    # IMEI
    imei = parse_imei(data[24:])

    result = f'{timestamp}, ID: {imei}, LAT: {lat:.6f}, LON: {lon:.6f}, SPEED: {speed} km/h, COURSE: {course}°\n'
    print(result)

    with open('datosChino.txt', 'a') as f:
        f.write(result)

def send_login_ack(sock, data):
    serial = data[-6:-4]
    content = b'\x01' + serial
    crc = crc16(content)
    ack = b'\x78\x78' + bytes([len(content)]) + content + crc + b'\x0D\x0A'
    sock.sendall(ack)
    print("ACK de login enviado.")

def send_position_request(sock, serial_num=1):
    content = b'\x80' + serial_num.to_bytes(2, 'big')
    crc = crc16(content)
    request = b'\x78\x78\x02' + content + crc + b'\x0D\x0A'
    sock.sendall(request)
    print("Solicitud de posición enviada.")

def start_server(host='200.58.98.187', port=5003):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Servidor escuchando en {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexión establecida con {addr}")
        while True:
            try:
                raw_data = client_socket.recv(1024)
                if not raw_data:
                    break
                hex_data = raw_data.hex()
                print(">> Recibido:", hex_data)

                if hex_data.startswith('7878'):
                    protocol = hex_data[6:8]

                    if protocol == '01':  # LOGIN
                        send_login_ack(client_socket, raw_data)
                        send_position_request(client_socket)

                    elif protocol == '12':  # POSICIÓN
                        decode_position_data(raw_data)

            except Exception as e:
                print("Error:", e)
                break

        client_socket.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    start_server()
