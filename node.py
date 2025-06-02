import socket
import threading
import json
import sys 
import time


PORT=int(sys.argv[1]) #port number cum ar fi 9001
HOST = "127.0.0.1" #localhost

#cerinta 3: servicii care pot fi pornite/oprite prin comenzi
services = {
    "backup": {"running":False},
    "monitoring": {"running":False},
    "logger": {"running":False}
}
#comenzi suportate (start/stop/status)
def execute_command(command):
    parts=command.strip().split()
    if len(parts) == 1 and parts[0] == "status":
        return json.dumps(services)
    elif len(parts) == 2:
        action, service = parts
        if service in services and action in ["start", "stop"]:
            services[service]["running"] = (action == "start")
            return f"{action}ed {service}"
    return "Invalid command"

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[NODE {PORT}] Ascultă conexiuni...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr)).start()

active_connection=None
connected_port = None 

def connect_to_nearby_nodes():
    global active_connection, connected_port 
    #cerinta 1: citire lsita de noduri din config
    with open("config.json") as f:
        nodes = json.load(f)
    #cerinta 1: conectare la noduri
    for ip, port in nodes:
        if port == PORT: #nu ne conectam la noi insine
            continue
        try:
            #se incearca conectarea la nod
            s = socket.create_connection((ip, port), timeout=2)
            print(f"[NODE {PORT}] Conectat permanent la {ip}:{port}")
            #cerinta 2: mentinere o singura conexiune deschisa
            active_connection = s  
            connected_port = port 
            return 
        except:
            continue
    print(f"[NODE {PORT}] Nu s-a putut conecta la niciun nod apropiat.")


#serverul asculta comenzi de la client/de la alt nod
def handle_connection(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break            
            parts = data.strip().split()
            #cerinta 6: interogarea starii serviciior pe fiecare nod
            if len(parts) >= 3 and parts[0] == "remote":
                target_port = int(parts[1])
                remote_cmd = ' '.join(parts[2:])
                #nodul primeste o comanda - remote <port> <comanda>
                #acesta redirectioneaza comanda prin conexiunea activa
                if active_connection and connected_port == target_port:
                    active_connection.send(remote_cmd.encode())
                    response = active_connection.recv(1024).decode()
                    #cerinta 7: confirmarea executiei unei comenzi de la distanta
                    conn.send(f"Răspuns de la nodul {target_port}: {response}".encode())
                else:
                    conn.send(f"Nu avem conexiune activa la nodul {target_port}".encode())
            else:
                result = execute_command(data)
                conn.send(result.encode())

def periodic_connection_check():
    global active_connection, connected_port
    while True:
        if active_connection is None:  #daca nu avem conexiune activa, incercam sa ne reconectam
            connect_to_nearby_nodes()
        time.sleep(5)  #verificam la fiecare 5 secunde

#pornire nod
if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(1)  #asteapta pornirea serverului
    #checker pentru conexiuni ulterioare
    threading.Thread(target=periodic_connection_check, daemon=True).start()
    connect_to_nearby_nodes()