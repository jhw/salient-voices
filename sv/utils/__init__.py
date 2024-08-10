import socket

def is_online(hosts=None, port=53, timeout=3):
    if hosts is None:
        hosts = ["8.8.8.8", "1.1.1.1"]  # Google's and Cloudflare's DNS servers
    for host in hosts:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            continue
    return False

if __name__ == "__main__":
    pass
