import socket
import threading
from datetime import datetime
import sys
import os

# === DEFINISI WARNA ANSI ===
COLOR_RESET = "\033[0m"
COLOR_YELLOW = "\033[93m"  # Untuk Info Sistem
COLOR_GREEN = "\033[92m"   # Untuk Pesan Client
COLOR_CYAN = "\033[96m"    # Untuk Pesan Admin
COLOR_RED = "\033[91m"     # Untuk Error/Exit

# Trik agar Windows support kode warna ANSI
os.system('')

# Konfigurasi Server
HOST = '0.0.0.0'
PORT = 2000

clients = []
client_names = []
server_socket = None

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def broadcast(message, sender_socket=None):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            remove_client(client)

def handle_client(client_socket, client_name):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                ts = get_timestamp()
                # Format: [HIJAU] [Jam] Nama : Pesan [RESET]
                formatted_msg = f"{COLOR_GREEN}[{ts}] {client_name.ljust(10)} : {msg}{COLOR_RESET}"
                
                print(formatted_msg)
                broadcast(formatted_msg, client_socket)
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def remove_client(client_socket):
    if client_socket in clients:
        index = clients.index(client_socket)
        name = client_names[index]
        clients.remove(client_socket)
        client_names.remove(name)
        client_socket.close()
        
        ts = get_timestamp()
        # Format: [KUNING] Info keluar [RESET]
        msg = f"\n{COLOR_YELLOW}[!] {ts} | {name} telah keluar chat room.{COLOR_RESET}"
        print(msg)
        broadcast(msg)

def server_write():
    while True:
        try:
            msg = input("") 
            
            if msg.lower() == 'exit':
                shutdown_server()
                break

            if msg:
                # Hapus baris input admin biar rapi
                sys.stdout.write("\033[F\033[K") 
                ts = get_timestamp()
                
                # Format: [CYAN] ADMIN >> Pesan [RESET]
                formatted_msg = f"{COLOR_CYAN}[{ts}] ADMIN      >> {msg}{COLOR_RESET}"
                
                print(formatted_msg) 
                broadcast(formatted_msg)
        except:
            break

def shutdown_server():
    print(f"\n{COLOR_RED}" + "="*60)
    print(" [!] MEMATIKAN SERVER...")
    broadcast(f"\n{COLOR_RED}[!] SERVER SEDANG DIMATIKAN OLEH ADMIN. TERIMA KASIH.{COLOR_RESET}")
    print(" [!] Koneksi ditutup.")
    print("="*60 + f"{COLOR_RESET}")
    os._exit(0)

def start_server():
    global server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_socket.settimeout(1)

        print(f"{COLOR_CYAN}" + "="*60)
        print(f" SERVER CHAT MULTI-CLIENT (COLOR MODE) | PORT: {PORT}")
        print("="*60)
        print(f" [i] Tekan Ctrl+C atau ketik 'exit' untuk berhenti.")
        print("-" * 60 + f"{COLOR_RESET}")
        
        thread_write = threading.Thread(target=server_write)
        thread_write.daemon = True
        thread_write.start()

        client_counter = 1

        while True:
            try:
                client_socket, addr = server_socket.accept()
                
                name = f"Client {client_counter}"
                client_counter += 1
                
                clients.append(client_socket)
                client_names.append(name)

                ts = get_timestamp()
                # Info Join warna KUNING
                print(f"\n{COLOR_YELLOW}[+] {ts} | Koneksi baru dari {addr[0]} as {name}{COLOR_RESET}")
                broadcast(f"\n{COLOR_YELLOW}[+] {ts} | {name} bergabung ke dalam chat!{COLOR_RESET}")
                
                thread = threading.Thread(target=handle_client, args=(client_socket, name))
                thread.daemon = True
                thread.start()
            
            except socket.timeout:
                continue
            except OSError:
                break

    except KeyboardInterrupt:
        shutdown_server()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_server()