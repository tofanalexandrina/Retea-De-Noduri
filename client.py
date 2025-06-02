import socket
import json

def interact_with_node(ip, port):
    with socket.create_connection((ip, port)) as s:
        while True:
            cmd = input(f"Comandă pentru {ip}:{port} (ex: status, start backup): ")
            if cmd.lower() == "exit":
                break
            s.send(cmd.encode())
            response = s.recv(4096).decode()
            try:
                parsed = json.loads(response)
                for name, info in parsed.items():
                    print(f"{name}: {'ON' if info['running'] else 'OFF'}")
            except:
                print(response)

if __name__ == "__main__":
    ip = input("IP nod: ") or "127.0.0.1"
    port = int(input("Port nod: "))
    interact_with_node(ip, port)
