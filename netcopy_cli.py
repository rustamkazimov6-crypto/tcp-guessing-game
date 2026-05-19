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

def run_client(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, filepath):
    checksum = calculate_checksum(filepath)
    if checksum is None:
        sys.exit(1)


    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as netcopy_sock:
            netcopy_sock.connect((srv_ip, srv_port))
            
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    netcopy_sock.sendall(data)
            
    except Exception as e:
        sys.exit(1)


    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as csum_sock:
            csum_sock.connect((chsum_srv_ip, chsum_srv_port))
            
            validity = 60
            csum_len = len(checksum)
            
            message = f"BE|{file_id}|{validity}|{csum_len}|{checksum}"
            csum_sock.sendall(message.encode('utf-8'))
            
            response = csum_sock.recv(1024).decode('utf-8').strip()
            if response != 'OK':
                pass
                
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(1)

    try:
        srv_ip = sys.argv[1]
        srv_port = int(sys.argv[2])
        chsum_srv_ip = sys.argv[3]
        chsum_srv_port = int(sys.argv[4])
        file_id = sys.argv[5]
        filepath = sys.argv[6]
    except ValueError:
        sys.exit(1)

    run_client(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, filepath)
