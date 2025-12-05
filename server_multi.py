import socket
import threading
from datetime import datetime
import os
import sys

RESET   = "\033[0m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
GREY    = "\033[90m"
RED     = "\033[91m"

HOST = "0.0.0.0" 
PORT = 2000

clients = []            
client_names = []       
client_addrs = []       

if os.name == "nt":
    os.system("")

def timestamp():
    return datetime.now().strftime("%H:%M")

def make_box(title, message, color=CYAN):
    lines = message.split("\n")
    width = max(len(title) + 6, max(len(line) for line in lines) + 2)
    top    = f"{color}┌── {title} {'─' * (width - len(title) - 4)}┐{RESET}"
    bottom = f"{color}└{'─' * (width + 2)}┘{RESET}"
    middle = ""
    for line in lines:
        middle += f"{color}│ {RESET}{line.ljust(width)}{color} │{RESET}\n"
    return f"\n{top}\n{middle}{bottom}"

def broadcast(msg):
    # Fungsi ini mengirim pesan ke SEMUA client yang ada di dalam list clients.
    for c in clients:
        try:
            c.send(msg.encode("utf-8"))
        except:
            pass

def send_private(cid, message):
    idx = cid - 1
    if idx < 0 or idx >= len(clients):
        print(f"{YELLOW}[x] Client ID tidak valid.{RESET}")
        return

    box = make_box(f"PRIVATE → Client {cid} | {timestamp()}", message, MAGENTA)
    try:
        clients[idx].send(box.encode("utf-8"))
        print(f"{MAGENTA}[PM terkirim ke Client {cid}]{RESET}")
    except:
        print(f"{YELLOW}[x] Gagal mengirim PM.{RESET}")

def kick_user(cid):
    idx = cid - 1
    if idx < 0 or idx >= len(clients):
        print(f"{YELLOW}[x] Client ID tidak valid.{RESET}")
        return

    target = clients[idx]
    try:
        target.send(f"{YELLOW}[!] Anda dikeluarkan oleh ADMIN.{RESET}".encode("utf-8"))
        target.close()
    except:
        pass
    
    remove_client(target)
    print(f"{YELLOW}[KICK] Client {cid} dikeluarkan.{RESET}")

def show_online():
    print("\n[ONLINE USERS]")
    for i, (name, addr) in enumerate(zip(client_names, client_addrs), start=1):
        print(f"{i}. {name} ({addr[0]}:{addr[1]})")
    print()

def handle_client(sock, name, addr):
    # Ini fungsi Threading. Setiap client punya 1 thread ini khusus buat dia.
    while True:
        try:
            # Buffer 1024 byte. Pesan yang panjang akan dipecah dan diambil bertahap (TCP Stream).
            msg = sock.recv(1024).decode("utf-8")
            if not msg:
                remove_client(sock)
                break

            box = make_box(f"{name} | {timestamp()}", msg, CYAN)
            print(box)
            broadcast(box)

        except:
            remove_client(sock)
            break

def remove_client(sock):
    if sock in clients:
        idx = clients.index(sock)
        name = client_names[idx]

        clients.remove(sock)
        client_addrs.remove(client_addrs[idx])
        client_names.remove(name)

        try:
            sock.close()
        except:
            pass

        info = f"{BLUE}[+] {name} keluar dari chat.{RESET}"
        print(info)
        broadcast(info)

def server_write():
    # Thread khusus agar Admin Server bisa ikut mengetik pesan atau command.
    while True:
        try:
            msg = input("")

            if msg.lower() == "exit":
                print(f"{YELLOW}[!] SERVER DIMATIKAN ADMIN.{RESET}")
                shutdown_server()
                break

            if msg.startswith("/pm "):
                try:
                    parts = msg.split(" ", 2)
                    if len(parts) == 3:
                        send_private(int(parts[1]), parts[2])
                    else:
                        print(f"{YELLOW}[x] Format: /pm <id> <pesan>{RESET}")
                except:
                    print(f"{YELLOW}[x] Format: /pm <id> <pesan>{RESET}")
                continue

            if msg.startswith("/kick "):
                try:
                    parts = msg.split(" ", 1)
                    if len(parts) == 2:
                        kick_user(int(parts[1]))
                    else:
                        print(f"{YELLOW}[x] Format: /kick <id>{RESET}")
                except:
                    print(f"{YELLOW}[x] Format: /kick <id>{RESET}")
                continue

            if msg == "/who":
                show_online()
                continue

            box = make_box(f"ADMIN | {timestamp()}", msg, YELLOW)
            sys.stdout.write("\033[F\033[K")
            print(box)
            broadcast(box)
        except EOFError:
            break
        except Exception:
            break

def shutdown_server():
    print(f"\n{RED}[!] SERVER SHUTDOWN...{RESET}")
    broadcast(f"{YELLOW}[!] SERVER DIMATIKAN ADMIN.{RESET}")
    os._exit(0)

def start_server():
    try:
        # Socket() defaultnya pakai TCP (SOCK_STREAM) dan IPv4 (AF_INET).
        server = socket.socket()
        
        # Bind untuk menentukan alamat IP dan Pintu (Port) server.
        server.bind((HOST, PORT))
        
        # Listen membuat server masuk mode 'menunggu tamu'.
        server.listen()
        
        # Timeout 1 detik. Server bangun tiap 1 detik buat cek apakah saya tekan Ctrl+C.
        server.settimeout(1.0) 

        print("=" * 60)
        print(f"{YELLOW} SERVER CHAT MULTI-CLIENT (DISCORD MODE){RESET}")
        print(f"{YELLOW} PORT: {PORT}{RESET}")
        print("=" * 60)
        print("[i] Commands: /pm <id> <pesan> | /kick <id> | /who | exit")
        print(f"{RED}[i] Tekan Ctrl+C untuk mematikan server secara paksa.{RESET}")
        print("-" * 60)

        # Daemon True artinya thread ini mati otomatis kalau program utama mati.
        t = threading.Thread(target=server_write, daemon=True)
        t.start()

        count = 1
        while True:
            try:
                # Accept menerima koneksi (3-Way Handshake TCP selesai di sini).
                sock, addr = server.accept()
                
                name = f"Client {count}"
                count += 1

                clients.append(sock)
                client_names.append(name)
                client_addrs.append(addr)

                join_msg = f"{BLUE}[+] {name} bergabung dari {addr[0]}:{addr[1]}{RESET}"
                print(join_msg)
                broadcast(join_msg)

                # Memanggil thread baru supaya Server bisa layani banyak client sekaligus (Concurrent)."
                threading.Thread(target=handle_client, args=(sock, name, addr), daemon=True).start()
            
            except socket.timeout:
                # Jika 1 detik gak ada tamu, kode masuk sini (pass), lalu loop lagi buat cek Ctrl+C.
                pass
            except OSError:
                break
                
    except KeyboardInterrupt:
        shutdown_server()
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    start_server()