from datetime import datetime
import socket
import os
import threading
import time
import hashlib

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

lock = threading.Lock()

def handle_client(conn,addr,filename, barrera, nombreLog):
    exito = False
    hasher = hashlib.sha256()
    print(f"[+] {addr} is connected.")
    while True:
        received = conn.recv(BUFFER_SIZE).decode()
        print(received)
        if not received:
            break
        if received=="Listo":
            barrera.wait()
            with open(filename, "rb") as f:
                start = time.time()
                while True:
                    bytes_read = f.read(BUFFER_SIZE)           
                    if not bytes_read:
                        print("Archivo enviado")
                        conn.send(hasher.digest())
                        integridad = conn.recv(BUFFER_SIZE).decode()
                        if integridad == "Correcto":
                            exito = True
                        break
                    #print("Se esta enviando el archivo")
                    hasher.update(bytes_read)
                    conn.sendall(bytes_read)
                end = time.time()
            tiempo = end-start
            log(addr, exito, tiempo, nombreLog) 


def log(cliente, exito, tiempo, nombreLog):
    texto = ["Conexion del cliente: " + str(cliente) + "\n", "\tEstado de exito: " + str(exito) + "\n", "\tTiempo de transferencia: " + str(tiempo) + "\n"]
    lock.acquire()
    with open("Logs/"+nombreLog, "a") as f:
        f.writelines(texto)
        f.close()
    lock.release()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(25)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
    filename = None
    numClientes = None
    while True:
        conn, addr = s.accept()
        received = conn.recv(BUFFER_SIZE).decode()
        filename, numClientes = received.split(":")
        conn.close()
        break
    nombreLog = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    filesize = os.path.getsize(filename)
    barrera = threading.Barrier(int(numClientes))
    texto = ["Archivo enviado: " + filename + "\n", "Tamaño del archivo: " + str(filesize) + "\n"]
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    with open("Logs/"+nombreLog, "w") as f:
        f.writelines(texto)
        f.close()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, filename, barrera, nombreLog))
        thread.start()

if __name__ == "__main__":
    main()
