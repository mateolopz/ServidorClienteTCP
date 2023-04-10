import socket
import os
import threading
import hashlib
import time

BUFFER_SIZE = 4096
host = "192.168.89.131"
port = 5001

def client(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")
    s.send("Listo".encode())

    hasher = hashlib.sha256()
    if not os.path.exists("ArchivosRecibidos"):
        os.makedirs("ArchivosRecibidos")
    with open("ArchivosRecibidos/"+filename, "wb") as f:
        start = time.time()
        while True:
            bytes_read = s.recv(BUFFER_SIZE)
            if bytes_read == hasher.digest():    
                s.send("Correcto".encode())
                break
            hasher.update(bytes_read)
            f.write(bytes_read)
        end = time.time()
        print(end-start)
def main():
    numClientes = input("numero clientes\n")
    for i in range(int(numClientes)):
        nombre = f"Cliente{i}-Prueba-{numClientes}.txt"
        thread = threading.Thread(target=client, args=(nombre,))
        thread.start()

if __name__ == "__main__":
    main()