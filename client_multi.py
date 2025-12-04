import socket
import threading
import sys
import os

# Warna Lokal Client
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"

os.system('') 

def receive_messages(sock):
    # Thread ini tugasnya cuma DENGAR pesan dari server terus menerus.
    while True:
        try:
            # recv() di sini blocking, menunggu paket data masuk
            msg = sock.recv(1024).decode('utf-8')
            if msg:
                sys.stdout.write("\r" + msg + "\n> ")
                sys.stdout.flush()
            else:
                print(f"\n\n{COLOR_RED}[!] Server telah ditutup. Tekan Enter untuk keluar.{COLOR_RESET}")
                sock.close()
                os._exit(0)
                break
        except:
            print(f"\n{COLOR_RED}[!] Koneksi terputus.{COLOR_RESET}")
            sock.close()
            os._exit(0)
            break

def write_messages(sock):
    # Fungsi ini untuk MENGIRIM pesan ke server.
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            msg = input()
            
            if msg.lower() == 'exit':
                print(f"\n{COLOR_RED}[!] Anda memutuskan koneksi.{COLOR_RESET}")
                sock.close()
                os._exit(0)
                break

            if msg:
                sys.stdout.write("\033[F\033[K")
                # send() mengirim data via TCP
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
        # Membuat Socket TCP
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Memulai 3-Way Handshake
        client.connect((HOST, PORT))
        
        print(f"{COLOR_CYAN}" + "="*60)
        print(f" TERHUBUNG KE SERVER: {HOST}:{PORT}")
        print("="*60)
        print(" [i] Ketik pesan lalu ENTER.")
        print(" [i] Ketik 'exit' atau Tekan Ctrl+C untuk keluar.")
        print("-" * 60 + f"{COLOR_RESET}")
        
        # Multitasking: Satu telinga mendengar (receive), satu mulut bicara (write)
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()

        write_messages(client)

    except KeyboardInterrupt:
        print(f"\n\n{COLOR_RED}[!] Keluar...{COLOR_RESET}")
        try:
            client.close()
        except:
            pass
        os._exit(0)
    except Exception as e:
        print(f"{COLOR_RED}[x] Gagal konek ke server: {e}{COLOR_RESET}")

if __name__ == "__main__":
    start_client()