#codul pentru un nod(server)
import socket
import threading
import json
import subprocess
import time
from common import load_json, save_json

config = load_json('config.json')
services = load_json('services.json')

HOST = '127.0.0.1'
PORT = config["port"]
NEIGHBORS = config["neighbors"]

def handle_command(data):
    global services
    try:
        command = json.loads(data)
        action = command["action"]
        if action == "status":
            return json.dumps(services)
        svc = command["service"]
        if svc not in services:
            return f"Serviciul {svc} nu exista"

        if action == "start":
            services[svc]["status"] = "running"
            subprocess.call(services[svc]["start_cmd"], shell=True)
            return f"Serviciul {svc} pornit"
        elif action == "stop":
            services[svc]["status"] = "stopped"
            subprocess.call(services[svc]["stop_cmd"], shell=True)
            return f"Serviciul {svc} oprit"
        else:
            return "Actiune necunoscuta"
    except Exception as e:
        return f"Eroare: {str(e)}"

def handle_client(conn, addr):
    with conn:
        print(f"[CONEXIUNE] {addr}")
        data = conn.recv(2048).decode()
        response = handle_command(data)
        conn.send(response.encode())

def server_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Pornit pe {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def connect_to_neighbors():
    for ip, port in NEIGHBORS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((ip, port))
            print(f"[RETEA] Conectat la nod vecin: {ip}:{port}")
            s.close()
            break  # doar prima conexiune reusita
        except:
            continue

if __name__ == "__main__":
    threading.Thread(target=server_loop).start()
    time.sleep(1)
    connect_to_neighbors()

