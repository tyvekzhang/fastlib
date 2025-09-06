import socket


def get_real_ip():
    """
    Get the real IP address of the local machine.
    
    This function attempts to determine the real (non-localhost) IP address
    of the local machine by creating a UDP connection to a public DNS server
    (8.8.8.8) and then checking which local IP address was used for this connection.
    
    Returns:
        str: The real IP address of the local machine if successful, 
             otherwise the loopback address '127.0.0.1'.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
