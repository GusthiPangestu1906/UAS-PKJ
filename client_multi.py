import socket
import threading
import sys
import os

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if msg:
                sys.stdout.write("\r" + msg + "\n> ")
                sys.stdout.flush()
            else:
                # Server menutup koneksi
                print("\n\n[!] Server telah ditutup. Tekan Enter untuk keluar.")
                sock.close()
                os._exit(0)
                break
        except:
            print("\n[!] Koneksi terputus.")
            sock.close()
            os._exit(0)
            break

def write_messages(sock):
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            msg = input()
            
            if msg.lower() == 'exit':
                print("\n[!] Anda memutuskan koneksi. Sampai jumpa!")
                sock.close()
                os._exit(0) # Keluar program
                break

            if msg:
                sys.stdout.write("\033[F\033[K")
                sock.send(msg.encode('utf-8'))
        except EOFError:
            pass

def start_client():
    if len(sys.argv) != 2:
        print("Usage: python client_multi.py <IP_SERVER>")
        sys.exit(1)
        
    HOST = sys.argv[1]
    PORT = 2000

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        
        print("="*60)
        print(f" TERHUBUNG KE SERVER: {HOST}:{PORT}")
        print("="*60)
        print(" [i] Ketik pesan lalu ENTER.")
        print(" [i] Ketik 'exit' atau Tekan Ctrl+C untuk keluar.")
        print("-" * 60)
        
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()

        write_messages(client)

    except KeyboardInterrupt:
        print("\n\n[!] Anda menekan Ctrl+C. Keluar dari chat...")
        client.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        print(f"[x] Gagal konek ke server: {e}")

if __name__ == "__main__":
    start_client()