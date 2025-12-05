import socket
import threading
import sys
import os

if os.name == "nt":
    os.system("")

RESET   = "\033[0m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
GREY    = "\033[90m"
RED     = "\033[91m"

def make_box(title, message, color=CYAN):
    lines = message.split("\n")
    width = max(len(title) + 6, max(len(line) for line in lines) + 2)
    top    = f"{color}┌── {title} {'─' * (width - len(title) - 4)}┐{RESET}"
    bottom = f"{color}└{'─' * (width + 2)}┘{RESET}"
    middle = ""
    for line in lines:
        middle += f"{color}│ {RESET}{line.ljust(width)}{color} │{RESET}\n"
    return f"\n{top}\n{middle}{bottom}\n"

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(4096).decode("utf-8")
            if not msg:
                print(f"\n{RED}[!] Server memutus koneksi.{RESET}")
                os._exit(0)
            sys.stdout.write("\r" + msg + "\n> ")
            sys.stdout.flush()
        except:
            print(f"\n{RED}[!] Koneksi terputus.{RESET}")
            os._exit(0)

def write_messages(sock):
    while True:
        try:
            # Tampilkan prompt
            sys.stdout.write("> ")
            sys.stdout.flush()
            
            # Input user (Bisa kena Ctrl+C disini)
            msg = input()
            
            # Fitur exit lewat ketikan
            if msg.lower() == "exit":
                print(f"{YELLOW}[!] Keluar dari chat.{RESET}")
                sock.close()
                os._exit(0)
            
            # Trik Visual: Hapus baris input user biar ga numpuk
            sys.stdout.write("\033[F\033[K")
            
            sock.send(msg.encode("utf-8"))
            
        except KeyboardInterrupt:
            # Menangkap Ctrl+C
            print(f"\n{RED}[!] Anda menekan Ctrl+C. Keluar...{RESET}")
            sock.close()
            os._exit(0)
        except:
            break

def start_client():
    if len(sys.argv) != 2:
        print("Usage: python client_multi.py <IP_SERVER>")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = 2000

    try:
        sock = socket.socket()
        sock.connect((HOST, PORT))

        my_ip, my_port = sock.getsockname()

        print("=" * 60)
        print(f"{CYAN} TERHUBUNG KE SERVER {HOST}:{PORT}{RESET}")
        print(f"{BLUE} Client Port: {my_port}{RESET}")
        print("=" * 60)
        print(" [i] Ketik 'exit' atau Tekan Ctrl+C untuk keluar.\n")

        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
        write_messages(sock)

    except KeyboardInterrupt:
        print(f"\n{RED}[!] Batal/Keluar.{RESET}")
    except Exception as e:
        print(f"{RED}[x] Gagal konek: {e}{RESET}")

if __name__ == "__main__":
    start_client()