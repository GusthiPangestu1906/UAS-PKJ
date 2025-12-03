import socket
import threading
from datetime import datetime

# Konfigurasi Server
HOST = '0.0.0.0'
PORT = 2000

clients = []
client_names = []

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log_print(message):
    """Fungsi helper untuk print agar rapi"""
    print(message)

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
                # Format Pesan Client agar rapi
                # Menggunakan ljust agar nama client rata kiri
                formatted_msg = f"[{ts}] {client_name.ljust(10)} : {msg}"
                log_print(formatted_msg) # Tampilkan di server
                broadcast(formatted_msg, client_socket) # Kirim ke semua
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
        msg = f"\n[ ! ] {ts} | {name} telah keluar chat room."
        log_print(msg)
        broadcast(msg)

def server_write():
    while True:
        msg = input("") # Input bersih tanpa prompt agar tidak menumpuk
        if msg:
            ts = get_timestamp()
            # Pesan Admin diberi tanda khusus (>>)
            formatted_msg = f"[{ts}] ADMIN      >> {msg}"
            
            # Kita print manual sedikit ke atas agar input kita tidak tertimpa (trick visual)
            print(f"\033[A[{ts}] ADMIN      >> {msg}\033[K") 
            
            broadcast(formatted_msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # BANNER KEREN
    print("="*60)
    print(f" SERVER CHAT MULTI-CLIENT | PORT: {PORT}")
    print("="*60)
    print(" [i] Menunggu koneksi client...")
    print(" [i] Admin bisa langsung mengetik pesan di bawah.")
    print("-" * 60)
    
    thread_write = threading.Thread(target=server_write)
    thread_write.start()

    client_counter = 1

    while True:
        client_socket, addr = server.accept()
        
        name = f"Client {client_counter}"
        client_counter += 1
        
        clients.append(client_socket)
        client_names.append(name)

        # Info Koneksi Baru
        ts = get_timestamp()
        print(f"\n[+] {ts} | Koneksi baru dari {addr[0]} as {name}")
        
        broadcast(f"\n[+] {ts} | {name} bergabung ke dalam chat!")
        
        thread = threading.Thread(target=handle_client, args=(client_socket, name))
        thread.start()

if __name__ == "__main__":
    start_server()