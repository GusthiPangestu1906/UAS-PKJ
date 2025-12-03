import socket
import threading
from datetime import datetime
import sys
import os

# Konfigurasi Server
HOST = '0.0.0.0'
PORT = 2000

clients = []
client_names = []
server_socket = None # Variabel global agar bisa ditutup dari mana saja

def get_timestamp():
    # Fitur: Mengambil waktu saat ini untuk log chat
    return datetime.now().strftime("%H:%M:%S")

def broadcast(message, sender_socket=None):
    # Fitur: Server mengirimkan (broadcast) pesan ke SEMUA client yang terhubung
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            remove_client(client)

def handle_client(client_socket, client_name):
    # Fitur: Thread khusus untuk menangani pesan dari satu client tertentu
    while True:
        try:
            # Server menerima pesan dari client (buffer 1024 byte)
            msg = client_socket.recv(1024).decode('utf-8')
            
            if msg:
                ts = get_timestamp()
                formatted_msg = f"[{ts}] {client_name.ljust(10)} : {msg}"
                
                print(formatted_msg)
                
                # Server meneruskan pesan ke client lain
                broadcast(formatted_msg, client_socket)
            else:
                # Jika pesan kosong, berarti client menutup koneksi
                remove_client(client_socket)
                break
        except:
            # Jika terjadi error saat menerima data
            remove_client(client_socket)
            break

def remove_client(client_socket):
    # Fitur: Menghapus data client yang disconnect dari list
    if client_socket in clients:
        index = clients.index(client_socket)
        name = client_names[index]
        
        clients.remove(client_socket)
        client_names.remove(name)
        
        client_socket.close()
        
        ts = get_timestamp()
        msg = f"\n[!] {ts} | {name} telah keluar chat room."
        print(msg)
        
        # Server memberitahu semua orang bahwa ada yang keluar
        broadcast(msg)

def server_write():
    while True:
        try:
            msg = input("") 
            
            # Fitur: Server mendeteksi perintah 'exit' dari admin
            if msg.lower() == 'exit':
                shutdown_server()
                break

            if msg:
                sys.stdout.write("\033[F\033[K") 
                
                ts = get_timestamp()
                formatted_msg = f"[{ts}] ADMIN      >> {msg}"
                
                # Server menampilkan pesan admin di console sendiri
                print(formatted_msg) 
                
                # Server mengirim pesan admin ke semua client
                broadcast(formatted_msg)
        except EOFError:
            break

def shutdown_server():
    print("\n" + "="*60)
    print(" [!] MEMATIKAN SERVER...")
    
    # Server memberitahu client bahwa server akan mati
    broadcast("\n[!] SERVER SEDANG DIMATIKAN OLEH ADMIN. TERIMA KASIH.")
    
    print(" [!] Koneksi ditutup.")
    print("="*60)
    
    os._exit(0) 

def start_server():
    global server_socket
    try:
        # Membuat Socket TCP (SOCK_STREAM)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        server_socket.bind((HOST, PORT))
        
        # Server mulai mendengarkan koneksi masuk (Listen)
        server_socket.listen()
        
        # Memungkinkan server mendeteksi Ctrl+C lebih cepat
        server_socket.settimeout(1) 

        print("="*60)
        print(f" SERVER CHAT MULTI-CLIENT | PORT: {PORT}")
        print("="*60)
        print(" [i] Tekan Ctrl+C atau ketik 'exit' untuk berhenti.")
        print("-" * 60)
        
        thread_write = threading.Thread(target=server_write)
        thread_write.daemon = True 
        thread_write.start()

        client_counter = 1

        while True:
            try:
                # Server mencoba menerima koneksi (Accept) dari client baru
                client_socket, addr = server_socket.accept()
                
                # Penamaan client
                name = f"Client {client_counter}"
                client_counter += 1
                
                clients.append(client_socket)
                client_names.append(name)

                ts = get_timestamp()
                print(f"\n[+] {ts} | Koneksi baru dari {addr[0]} as {name}")
                broadcast(f"\n[+] {ts} | {name} bergabung ke dalam chat!")
                
                # Fitur: Membuat Thread baru untuk menangani client tersebut (Concurrent)
                thread = threading.Thread(target=handle_client, args=(client_socket, name))
                thread.daemon = True
                thread.start()
            
            except socket.timeout:
                # Jika tidak ada tamu dalam 1 detik, ulangi loop (cek Ctrl+C)
                continue
            
            except OSError:
                break

    except KeyboardInterrupt:
        shutdown_server()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_server()