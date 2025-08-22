#!/usr/bin/env python3
"""
Test TCP Connectivity - Módulo para probar conectividad TCP en puerto 5003
Puede ejecutarse tanto como servidor como cliente para testing bidireccional
"""

import socket
import threading
import time
import sys
import os

# Configuración
HOST = '0.0.0.0'  # Para servidor
CLIENT_HOST = 'localhost'  # Para cliente (cambiar por IP del servidor)
PORT = 5003
BUFFER_SIZE = 1024

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Muestra banner del programa"""
    print("=" * 60)
    print("🔌 TEST TCP CONNECTIVITY - PUERTO 5003")
    print("=" * 60)
    print("Este módulo puede ejecutarse como:")
    print("  SERVIDOR: python test_tcp_connectivity.py server")
    print("  CLIENTE:  python test_tcp_connectivity.py client [IP_SERVIDOR]")
    print("=" * 60)

def run_server():
    """Ejecuta el servidor TCP"""
    print("🚀 Iniciando SERVIDOR TCP en puerto 5003...")
    print(f"📡 Escuchando en {HOST}:{PORT}")
    print("⏳ Esperando conexiones de clientes...")
    print("-" * 60)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Configurar socket para reutilizar puerto
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        
        print(f"✅ Servidor iniciado exitosamente en puerto {PORT}")
        print("💡 Presiona Ctrl+C para detener el servidor")
        print("💬 Escribe mensajes para enviar a todos los clientes conectados")
        print("-" * 60)
        
        # Lista para mantener clientes conectados
        connected_clients = []
        
        # Thread para manejar entrada del servidor
        def server_input_handler():
            try:
                while True:
                    server_message = input("📤 Servidor: ").strip()
                    if server_message:
                        # Enviar mensaje a todos los clientes conectados
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"📤 Enviando: {server_message}")
                        
                        # Filtrar clientes desconectados y enviar mensaje
                        active_clients = []
                        for client_info in connected_clients:
                            try:
                                client_info['socket'].send(server_message.encode('utf-8'))
                                active_clients.append(client_info)
                            except:
                                print(f"🔌 Cliente {client_info['address']} desconectado")
                        
                        connected_clients[:] = active_clients
                        
            except (EOFError, KeyboardInterrupt):
                pass
        
        # Iniciar thread para entrada del servidor
        input_thread = threading.Thread(target=server_input_handler)
        input_thread.daemon = True
        input_thread.start()
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"🔗 Cliente conectado desde: {client_address}")
                
                # Agregar cliente a la lista
                client_info = {'socket': client_socket, 'address': client_address}
                connected_clients.append(client_info)
                
                # Crear thread para manejar cliente
                client_thread = threading.Thread(
                    target=handle_client, 
                    args=(client_socket, client_address, connected_clients)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error en servidor: {e}")

def handle_client(client_socket, client_address, connected_clients):
    """Maneja la comunicación con un cliente"""
    print(f"💬 Iniciando chat con {client_address}")
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            
            message = data.decode('utf-8', errors='ignore').strip()
            if message:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] 📥 {client_address}: {message}")
                
                # Enviar confirmación al cliente
                response = f"✅ Mensaje recibido: {message}"
                client_socket.send(response.encode('utf-8'))
                
    except Exception as e:
        print(f"❌ Error con cliente {client_address}: {e}")
    finally:
        # Remover cliente de la lista cuando se desconecte
        try:
            connected_clients[:] = [c for c in connected_clients if c['address'] != client_address]
        except:
            pass
        client_socket.close()
        print(f"🔌 Cliente {client_address} desconectado")

def run_client(server_ip=None):
    """Ejecuta el cliente TCP"""
    target_host = server_ip if server_ip else CLIENT_HOST
    
    print(f"🔌 Iniciando CLIENTE TCP...")
    print(f"🎯 Conectando a: {target_host}:{PORT}")
    print("-" * 60)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Intentar conexión
            print(f"⏳ Conectando a {target_host}:{PORT}...")
            client_socket.connect((target_host, PORT))
            print(f"✅ Conexión exitosa a {target_host}:{PORT}")
            print("💬 Chat iniciado! Escribe mensajes (escribe 'quit' para salir)")
            print("-" * 60)
            
            # Thread para recibir mensajes del servidor
            def receive_messages():
                try:
                    while True:
                        data = client_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                        message = data.decode('utf-8', errors='ignore').strip()
                        if message:
                            timestamp = time.strftime("%H:%M:%S")
                            print(f"[{timestamp}] 📥 Servidor: {message}")
                except Exception as e:
                    print(f"❌ Error recibiendo mensajes: {e}")
            
            # Iniciar thread de recepción
            receive_thread = threading.Thread(target=receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Loop principal para enviar mensajes
            try:
                while True:
                    user_input = input("📤 Tú: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'salir']:
                        print("👋 Cerrando conexión...")
                        break
                    
                    if user_input:
                        # Enviar mensaje al servidor
                        client_socket.send(user_input.encode('utf-8'))
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"[{timestamp}] 📤 Enviado: {user_input}")
                        
            except KeyboardInterrupt:
                print("\n👋 Cerrando conexión...")
                
    except ConnectionRefusedError:
        print(f"❌ Error: No se pudo conectar a {target_host}:{PORT}")
        print("💡 Verifica que:")
        print("   - El servidor esté ejecutándose")
        print("   - La IP del servidor sea correcta")
        print("   - El puerto 5003 esté abierto")
        print("   - No haya firewall bloqueando la conexión")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_local_connection():
    """Prueba conexión local al puerto 5003"""
    print("🔍 Probando conectividad local al puerto 5003...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            test_socket.settimeout(5)
            result = test_socket.connect_ex(('localhost', PORT))
            
            if result == 0:
                print("✅ Puerto 5003 está abierto y accesible localmente")
                return True
            else:
                print("❌ Puerto 5003 no está abierto localmente")
                return False
                
    except Exception as e:
        print(f"❌ Error en test local: {e}")
        return False

def show_help():
    """Muestra ayuda del programa"""
    print_banner()
    print("\n📖 USO:")
    print("  python test_tcp_connectivity.py server")
    print("  python test_tcp_connectivity.py client [IP_SERVIDOR]")
    print("  python test_tcp_connectivity.py test")
    print("  python test_tcp_connectivity.py help")
    print("\n📋 EJEMPLOS:")
    print("  # Ejecutar como servidor")
    print("  python test_tcp_connectivity.py server")
    print("\n  # Ejecutar como cliente (conectar a localhost)")
    print("  python test_tcp_connectivity.py client")
    print("\n  # Ejecutar como cliente (conectar a IP específica)")
    print("  python test_tcp_connectivity.py client 192.168.1.100")
    print("\n  # Probar conectividad local")
    print("  python test_tcp_connectivity.py test")
    print("\n💡 CONSEJOS:")
    print("  - Ejecuta primero el servidor en una terminal")
    print("  - Luego ejecuta el cliente en otra terminal")
    print("  - El servidor puede escribir mensajes para enviar a todos los clientes")
    print("  - Para conectar desde otra PC, usa la IP del servidor")
        print("  - El puerto 5003 debe estar abierto en el firewall")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'server':
        run_server()
    elif command == 'client':
        server_ip = sys.argv[2] if len(sys.argv) > 2 else None
        run_client(server_ip)
    elif command == 'test':
        test_local_connection()
    elif command in ['help', '--help', '-h']:
        show_help()
    else:
        print(f"❌ Comando desconocido: {command}")
        print("💡 Usa 'python test_tcp_connectivity.py help' para ver la ayuda")
        show_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Programa terminado por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("💡 Usa 'python test_tcp_connectivity.py help' para ver la ayuda")
