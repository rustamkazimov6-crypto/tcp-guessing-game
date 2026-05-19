import socket
import hashlib
import sys
import os
import time


def calculate_checksum(filepath):
    hasher = hashlib.md5()
    blocksize = 65536
    try:
        with open(filepath, 'rb') as f:
            while True:
                buffer = f.read(blocksize)
                if not buffer:
                    break
                hasher.update(buffer)
        return hasher.hexdigest()
    except FileNotFoundError:
        return None


def check_file_integrity(file_id, local_filepath, chsum_srv_ip, chsum_srv_port):
    local_checksum = calculate_checksum(local_filepath)
    if local_checksum is None:
        return 'CSUM CORRUPTED'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as csum_sock:
            csum_sock.connect((chsum_srv_ip, chsum_srv_port))

            message = f"KI|{file_id}"
            csum_sock.sendall(message.encode('utf-8'))

            response = csum_sock.recv(1024).decode('utf-8').strip()

            parts = response.split('|')
            if len(parts) == 2 and parts[0] != '0':
                expected_checksum = parts[1]
            else:
                expected_checksum = None

    except Exception as e:
        return 'CSUM CORRUPTED'

    if expected_checksum and local_checksum == expected_checksum:
        return 'CSUM OK'
    else:
        return 'CSUM CORRUPTED'


def run_server(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, local_filepath):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((srv_ip, srv_port))
        server_socket.listen(1)
    except Exception as e:
        sys.exit(1)

    conn, addr = server_socket.accept()
    server_socket.close()

    try:
        with open(local_filepath, 'wb') as f:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                f.write(data)
    except Exception as e:
        conn.close()
        sys.exit(1)
    finally:
        conn.close()

    result = check_file_integrity(file_id, local_filepath, chsum_srv_ip, chsum_srv_port)
    print(result)


if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(1)

    try:
        srv_ip = sys.argv[1]
        srv_port = int(sys.argv[2])
        chsum_srv_ip = sys.argv[3]
        chsum_srv_port = int(sys.argv[4])
        file_id = sys.argv[5]
        local_filepath = sys.argv[6]
    except ValueError:
        sys.exit(1)

    run_server(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, local_filepath)
