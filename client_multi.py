import socket
import threading
import sys
import os

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if msg:
                print(msg)
            else:
                print("\n[ ! ] Koneksi terputus dari server.")
                sock.close()
                os._exit(0) # Force exit
                break
        except:
            print("\n[ ! ] Terjadi error atau server mati.")
            sock.close()
            os._exit(0)
            break

def write_messages(sock):
    while True:
        try:
            msg = input()
            # Trick visual: Hapus baris input user dan ganti dengan pesan server nanti
            # (Agar tidak ada double text di layar sendiri)
            sys.stdout.write("\033[F") 
            if msg:
                sock.send(msg.encode('utf-8'))
        except:
            break

def start_client():
    if len(sys.argv) != 2:
        print("Usage: python client_multi.py <IP_SERVER>")
        sys.exit(1)
        
    HOST = sys.argv[1]
    PORT = 2000

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        
        # BANNER CLIENT
        print("="*60)
        print(f" TERHUBUNG KE SERVER: {HOST}:{PORT}")
        print("="*60)
        print(" Ketik pesan Anda lalu tekan ENTER.")
        print("-" * 60)
        
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        write_thread = threading.Thread(target=write_messages, args=(client,))
        write_thread.start()

    except Exception as e:
        print(f"[x] Gagal konek ke server: {e}")

if __name__ == "__main__":
    start_client()