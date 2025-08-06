import socket
from datetime import datetime

HOST = '200.58.98.187'
PORT = 5003

# Archivo donde se guardarán los datos
FILE_PATH = 'recibidoGPS.txt'

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(FILE_PATH, 'a') as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log(f"Servidor escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                log(f"Conexion entrante desde {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        log("Conexion cerrada por el cliente")
                        break
                    log(f"Datos recibidos (hex): {data.hex()}")
                    try:
                        log(f"Datos recibidos (ascii): {data.decode('ascii', errors='replace')}")
                    except Exception as e:
                        log(f"Error al decodificar a ASCII: {e}")

if __name__ == '__main__':
    start_server()
