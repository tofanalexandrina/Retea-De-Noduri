import socket
import json

#clientul citeste comenzi de la utilizator(start backup, stop monitoring, etc.)
#acesta le trimite nodului, nodul executa comenzile si returneaza rezultatul
def interact_with_node(ip, port):
    with socket.create_connection((ip, port)) as s:
        #cerinta 4: citire lista servicii si comenzi disponibile la pornire
        print("Citire servicii disponibile...")
        s.send("status".encode())
        response = s.recv(4096).decode()
        try:
            available_services = json.loads(response)
            print("Servicii disponibile:")
            for service, info in available_services.items():
                print(f"- {service} (currently {'ON' if info['running'] else 'OFF'})")
            print("Comenzi: status, start/stop <service>, remote <port> <command>")
        except:
            print("Eroare la citirea serviciilor disponibile.")
        
        while True:
            cmd = input(f"Comandă pentru {ip}:{port} (ex: status, start backup, remote 9002 status): ")
            if cmd.lower() == "exit":
                break
            #cerinta 5: din client se pot porni/opri servicii
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
