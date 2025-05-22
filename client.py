import socket
import json

import socket
import json

def send_command(ip, port, service, action):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        cmd = json.dumps({
            "service": service,
            "action": action
        })
        s.send(cmd.encode())
        response = s.recv(4096).decode()
        print("[RĂSPUNS]", response)
    except Exception as e:
        print("Eroare:", e)
    finally:
        s.close()

def main():
    print("=== Client Retea Noduri ===")
    ip = input("IP Nod (ex: 127.0.0.1): ")
    port = int(input("Port Nod (ex: 9000): "))

    while True:
        print("\nComenzi disponibile:")
        print("1. status")
        print("2. start <serviciu>")
        print("3. stop <serviciu>")
        print("4. iesire")

        cmd = input("> ").strip().split()

        if cmd[0] == "status":
            send_command(ip, port, "any", "status")
        elif cmd[0] in ["start", "stop"] and len(cmd) == 2:
            send_command(ip, port, cmd[1], cmd[0])
        elif cmd[0] == "iesire":
            break
        else:
            print("Comanda invalida")

if __name__ == "__main__":
    main()

