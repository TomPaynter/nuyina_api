import socket

nmea = b"$GPRMC,031431.00,A,5535.8818,S,07740.9686,E,8.6,311.96,291225,,,A*70"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(nmea, ("127.0.0.1", 1234))
sock.close()
