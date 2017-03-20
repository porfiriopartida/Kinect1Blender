# import bpy
import socket
import sys
import threading

port = 8907;
address = "localhost";
packetSize = 1024

class KinectServer:
    global address, port, packetSize
    def __init__(self, address, port):
        self.address = address
        self.port = port
    def toString(self):
        return ("[address=%s, port=%s]" % self.address, self.port)

    def start(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = (address, port)
        print ('starting up on %s port %s' % server_address)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(0)

        while True:
            # Wait for a connection
            print ('waiting for a connection')
            connection, client_address = sock.accept()
            threading.Thread(target = self.listenToClient,args = (connection, client_address)).start()

    def listenToClient(self, connection, client_address):
        try:
            print ('connection from', client_address)
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(packetSize)
                print ('received "%s"' % data)
                if data:
                    print('sending data back to the client')
                    connection.sendall(data)
                else:
                    print ('no more data from', client_address)
                    break
        except:
            print ("Closing Client %s" % client_address)
            client.close()
            return False

def main():
    global address, port
    kinectServer = KinectServer(address, port)
    print("Hello World 2")
    kinectServer.start()
    print("Hello World 3")

if __name__ == "__main__":
    main()