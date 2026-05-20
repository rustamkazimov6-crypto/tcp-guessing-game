import socket
import sys
import random
import struct
import select

MSG_STRUCT = struct.Struct("ci")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    server_sock.setblocking(False)

    sockets = [server_sock]
    clients = {}

    number = random.randint(1, 100)
    print(f"[SERVER] Secret number chosen: {number}")
    game_over = False

    while True:
        readable, _, exceptional = select.select(sockets, [], sockets)

        for s in readable:
            if s is server_sock:
                conn, addr = server_sock.accept()
                conn.setblocking(False)
                sockets.append(conn)
                clients[conn] = addr
                print(f"[SERVER] New client from {addr}")
            else:
                try:
                    data = s.recv(MSG_STRUCT.size)
                except ConnectionResetError:
                    data = None

                if not data:
                    print(f"[SERVER] Client {clients[s]} disconnected")
                    sockets.remove(s)
                    del clients[s]
                    s.close()
                    continue

                try:
                    c, i = MSG_STRUCT.unpack(data)
                    guess_type = c.decode()
                except Exception as e:
                    print("[SERVER] Failed to unpack:", e)
                    continue

                print(f"[SERVER] Received from {clients[s]}: ({guess_type}, {i})")

                if game_over:
                    s.sendall(MSG_STRUCT.pack(b'V', 0))
                    continue

                response = None

                if guess_type == '<':
                    response = b'I' if number < i else b'N'
                elif guess_type == '>':
                    response = b'I' if number > i else b'N'
                elif guess_type == '=':
                    if number == i:
                        response = b'Y'
                        game_over = True
                    else:
                        response = b'K'

                if response is not None:
                    s.sendall(MSG_STRUCT.pack(response, 0))
                    print(f"[SERVER] Sent ({response.decode()}, 0) to {clients[s]}")

        for s in exceptional:
            sockets.remove(s)
            s.close()
            del clients[s]

if __name__ == "__main__":
    main()
