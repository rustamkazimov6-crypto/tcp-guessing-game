import socket
import threading
import sys
import time
import os

CHECKSUM_DB = {}
LOCK = threading.Lock()

def check_and_cleanup(file_id):
    if file_id in CHECKSUM_DB:
        if CHECKSUM_DB[file_id]['expiration_time'] < time.time():
            del CHECKSUM_DB[file_id]
            return True
        return False
    return True

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            return

        parts = data.strip().split('|')
        
        if parts[0] == 'BE':
            if len(parts) == 5:
                file_id = parts[1]
                validity = int(parts[2])
                csum_len = int(parts[3])
                checksum = parts[4]

                if len(checksum) == csum_len:
                    expiration = time.time() + validity
                    
                    with LOCK:
                        CHECKSUM_DB[file_id] = {
                            'checksum_length': csum_len,
                            'checksum': checksum,
                            'expiration_time': expiration
                        }
                    conn.sendall(b'OK')
                else:
                    conn.sendall(b'ERROR: INVALID CHECKSUM LENGTH')
            else:
                conn.sendall(b'ERROR: INVALID BE FORMAT')
        
        elif parts[0] == 'KI':
            if len(parts) == 2:
                file_id = parts[1]
                
                with LOCK:
                    check_and_cleanup(file_id)
                    
                    if file_id in CHECKSUM_DB:
                        csum_len = CHECKSUM_DB[file_id]['checksum_length']
                        checksum = CHECKSUM_DB[file_id]['checksum']
                        response = f"{csum_len}|{checksum}"
                        conn.sendall(response.encode('utf-8'))
                    else:
                        conn.sendall(b'0|')
            else:
                conn.sendall(b'ERROR: INVALID KI FORMAT')
        
        else:
            conn.sendall(b'ERROR: UNKNOWN COMMAND')

    except Exception as e:
        pass
    finally:
        conn.close()

def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((ip, port))
        server_socket.listen(5)
    except Exception as e:
        sys.exit(1)

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    
    ip = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        sys.exit(1)

    start_server(ip, port)
