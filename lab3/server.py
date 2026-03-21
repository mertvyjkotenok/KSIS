import socket
import threading
import errno
import os 

clients = []
active_ips = set()

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                if client in clients: clients.remove(client)

def handle_tcp_client(client_socket, addr):
    client_ip = addr[0]
    print(f"Установлено соединение с {addr}")
    
    while True:
        try:
            data = client_socket.recv(1024)
            if not data: break 
            print(f"[Сообщение от {addr}]: {data.decode('utf-8')}")
            broadcast(data, client_socket) 
        except: break
            
    if client_socket in clients: clients.remove(client_socket)
    if client_ip in active_ips: active_ips.remove(client_ip)
    client_socket.close()
    print(f"Соединение с {addr} разорвано.")

def start_server():
    while True:
        print("\n--- Настройка Сервера ---")
        srv_ip = input("Введите IP сервера (напр. 127.0.0.1): ")
        tcp_port = int(input("Введите TCP порт для чата: "))
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            tcp_sock.bind((srv_ip, tcp_port))
            tcp_sock.listen(5)
            tcp_sock.settimeout(1.0)
            break
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print(f"[!] ОШИБКА: Порт {tcp_port} уже занят другой программой.")
            elif e.errno == errno.EADDRNOTAVAIL:
                print(f"[!] ОШИБКА: IP-адрес {srv_ip} не принадлежит этому компьютеру.")
            else:
                print(f"[!] НЕИЗВЕСТНАЯ ОШИБКА: {e}")
            tcp_sock.close()

    print(f"\n[*] Сервер запущен на {srv_ip}:{tcp_port}! Для выключения: Ctrl+C")

    try:
        while True:
            try:
                client_sock, addr = tcp_sock.accept()
            except socket.timeout:
                continue
            
            client_ip = addr[0]
            if client_ip in active_ips:
                client_sock.send("[!] ОТКАЗ СЕРВЕРА: Этот IP уже находится в чате.".encode('utf-8'))
                client_sock.close()
                continue

            client_sock.send("SUCCESS".encode('utf-8'))
            active_ips.add(client_ip)
            clients.append(client_sock)
            threading.Thread(target=handle_tcp_client, args=(client_sock, addr), daemon=True).start()
            
    except KeyboardInterrupt:
        print("\n\n[*] Остановка сервера...")
        for client in clients:
            try:
                client.send("\n[СЕРВЕР]: Работа сервера завершена.".encode('utf-8'))
                client.close()
            except: pass
        tcp_sock.close()
        print("[*] Сервер успешно выключен.")
        os._exit(0) 

if __name__ == "__main__":
    start_server()