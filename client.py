import socket
import sys
import struct
import time

MSG_STRUCT = struct.Struct("ci")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <hostname> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    low, high = 1, 100
    found = False

    while not found and low <= high:
        mid = (low + high) // 2
        sock.sendall(MSG_STRUCT.pack(b'=', mid))
        data = sock.recv(MSG_STRUCT.size)
        c, i = MSG_STRUCT.unpack(data)
        response = c.decode()

        if response == 'Y':
            print(f"[CLIENT] Guessed correctly: {mid}")
            break
        elif response == 'K':
            sock.sendall(MSG_STRUCT.pack(b'<', mid))
            data = sock.recv(MSG_STRUCT.size)
            c, i = MSG_STRUCT.unpack(data)
            response = c.decode()
            if response == 'V':
                print("[CLIENT] Game already ended")
                break
            if response == 'I':
                high = mid - 1
            elif response == 'N':
                sock.sendall(MSG_STRUCT.pack(b'>', mid))
                data = sock.recv(MSG_STRUCT.size)
                c, i = MSG_STRUCT.unpack(data)
                response = c.decode()
                if response == 'V':
                    print("[CLIENT] Game already ended")
                    break
                if response == 'I':
                    low = mid + 1
        elif response == 'V':
            print("[CLIENT] Received End (V). Exiting.")
            break
        else:
            print(f"[CLIENT] Unexpected response: {response}")
            break

        time.sleep(0.1)

    sock.close()

if __name__ == "__main__":
    main()
