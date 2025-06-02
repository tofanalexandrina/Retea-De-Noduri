import socket
import threading
import json
import sys 
import time


PORT=int(sys.argv[1]) #port number cum ar fi 9001
HOST = "127.0.0.1" #localhost

#servicii simulate
services = {
    "backup": {"running":False},
    "monitoring": {"running":False},
    "logger": {"running":False}
}

#comenzi suportate
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

#serverul asculta comenzi de la client/de la alt nod
def handle_connection(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            result = execute_command(data)
            conn.send(result.encode())

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[NODE {PORT}] Ascultă conexiuni...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_connection, args=(conn, addr)).start()


#clientul incearca sa se conecteze la alte noduri
def connect_to_nearby_nodes():
    with open("config.json") as f:
        nodes = json.load(f)

    for ip, port in nodes:
        if port == PORT:  # Nu încercăm să ne conectăm la noi înșine
            continue
        try:
            s = socket.create_connection((ip, port), timeout=2)
            print(f"[NODE {PORT}] Conectat la {ip}:{port}")
            s.close()
            return
        except:
            continue
    print(f"[NODE {PORT}] Nu s-a putut conecta la niciun nod apropiat.")

#pornire nod
if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(1)  #asteapta pornirea serverului
    connect_to_nearby_nodes()