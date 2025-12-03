import socket
import threading
from datetime import datetime
import sys

# Konfigurasi Server
HOST = '0.0.0.0'
PORT = 2000

clients = []
client_names = []

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def broadcast(message, sender_socket=None):
    """Mengirim pesan ke semua client"""
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            remove_client(client)

def handle_client(client_socket, client_name):
    """Menangani pesan dari client"""
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                ts = get_timestamp()
                # Format: [Jam] Nama : Pesan
                formatted_msg = f"[{ts}] {client_name.ljust(10)} : {msg}"
                print(formatted_msg) # Tampilkan di server
                broadcast(formatted_msg, client_socket) # Kirim ke semua
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def remove_client(client_socket):
    """Menghapus client yang disconnect"""
    if client_socket in clients:
        index = clients.index(client_socket)
        name = client_names[index]
        clients.remove(client_socket)
        client_names.remove(name)
        client_socket.close()
        
        ts = get_timestamp()
        msg = f"\n[!] {ts} | {name} telah keluar chat room."
        print(msg)
        broadcast(msg)

def server_write():
    """Admin Server mengetik pesan"""
    while True:
        try:
            msg = input("") # Admin mengetik di sini
            if msg:
                # Trik visual: Hapus baris input admin biar gak dobel
                sys.stdout.write("\033[F\033[K") 
                
                ts = get_timestamp()
                formatted_msg = f"[{ts}] ADMIN      >> {msg}"
                print(formatted_msg) # Tampilkan di server sendiri
                broadcast(formatted_msg) # Kirim ke semua client
        except:
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # BANNER JUDUL
    print("="*60)
    print(f" SERVER CHAT MULTI-CLIENT | PORT: {PORT}")
    print("="*60)
    print(" [i] Menunggu koneksi client...")
    print(" [i] Admin bisa langsung mengetik pesan (Blind Type).")
    print("-" * 60)
    
    # Thread khusus buat Admin ngetik
    thread_write = threading.Thread(target=server_write)
    thread_write.start()

    client_counter = 1

    while True:
        client_socket, addr = server.accept()
        
        # Penamaan otomatis (Inovasi)
        name = f"Client {client_counter}"
        client_counter += 1
        
        clients.append(client_socket)
        client_names.append(name)

        ts = get_timestamp()
        print(f"\n[+] {ts} | Koneksi baru dari {addr[0]} as {name}")
        broadcast(f"\n[+] {ts} | {name} bergabung ke dalam chat!")
        
        thread = threading.Thread(target=handle_client, args=(client_socket, name))
        thread.start()

if __name__ == "__main__":
    start_server()