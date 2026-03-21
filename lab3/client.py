import socket
import threading
import sys
import errno
import os 

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data: 
                print("\n[!] Соединение разорвано сервером.")
                os._exit(0) 
            msg = data.decode('utf-8')
            sys.stdout.write(f"\r{msg}\nВы: ")
            sys.stdout.flush()
        except: 
            os._exit(0)

def start_client():
    tcp_sock = None
    while True: 
        print("\n--- Данные сервера ---")
        srv_ip = input("IP сервера: ")
        srv_tcp_p = int(input("Порт сервера: "))
        connected = False
        
        while True:
            print("\n--- Ваши локальные настройки ---")
            my_ip = input("Ваш локальный IP: ")
            
            if my_ip == srv_ip:
                print("[!] ОШИБКА: Ваш IP совпадает с IP сервера.")
                continue
                
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                test_sock.bind((my_ip, 0))
                test_sock.close()
            except OSError:
                print(f"[!] ОШИБКА IP: {my_ip} недоступен на этом ПК.")
                test_sock.close()
                continue

            my_tcp_p = int(input("Ваш локальный порт: "))
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                # 1. Сначала биндим свой адрес
                tcp_sock.bind((my_ip, my_tcp_p))
                
                # 2. Пытаемся подключиться (Физическая проверка)
                try:
                    tcp_sock.connect((srv_ip, srv_tcp_p))
                except Exception:
                    print("[!] Сервер недоступен.")
                    tcp_sock.close()
                    break # Возврат к вводу данных СЕРВЕРА

                # 3. Читаем ответ (Логическая проверка: SUCCESS или ОТКАЗ)
                try:
                    auth_response = tcp_sock.recv(1024).decode('utf-8')
                    if auth_response == "SUCCESS":
                        print("[*] Успешное подключение!")
                        connected = True
                        break # Выход к вводу имени
                    else:
                        # Сюда попадет текст: "[!] ОТКАЗ СЕРВЕРА: Этот IP уже находится в чате."
                        print(f"\n{auth_response}")
                        tcp_sock.close()
                        continue # Даем шанс ввести другой ЛОКАЛЬНЫЙ IP
                except Exception:
                    print("[!] Ошибка при получении авторизации от сервера.")
                    tcp_sock.close()
                    break

            except OSError as e:
                if e.errno == errno.EADDRINUSE:
                    print(f"[!] ОШИБКА ПОРТА: Порт {my_tcp_p} уже занят.")
                else:
                    print(f"[!] ОШИБКА: {e}")
                tcp_sock.close()
                continue
                
        if connected: break

    name = input("Ваше имя: ")
    tcp_sock.send(f"{name} присоединился к чату.".encode('utf-8'))
    
    # Запуск потока на чтение
    threading.Thread(target=receive_messages, args=(tcp_sock,), daemon=True).start()

    while True:
        try:
            text = input("Вы: ")
            if text.lower() == 'exit': break
            tcp_sock.send(f"[{name}]: {text}".encode('utf-8'))
        except: 
            break
            
    tcp_sock.close()
    os._exit(0) 

if __name__ == "__main__":
    try:
        start_client()
    except KeyboardInterrupt:
        os._exit(0)