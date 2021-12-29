import os
import sys
import socket
import struct
import time
from scapy.all import *
import ipaddress
import getch
from threading import Thread
import selectors
import termios
import tty


class QuickMathClient:
    def __init__(self):
        self.UDPip = self.getIP()
        self.teamName = "Chebyshev"
        self.host = None
        self.port = None
        self.udpPort = 13117
        self.udpClientSocket = None
        self.clientSocket = None
        self.inputListener = None
        self.gameOn = False
        self.colorReset = "\033[0m"
        self.red = "\033[31m"
        self.magenta = "\033[35m"
        self.underline = '\033[4m'
        self.cyan = "\033[36m"

    def run(self):
        while True:
            try:
                self.getOffer()
                self.connecting_to_a_server()
                self.game_mode()
            except:
                pass

    def unpackPort(self, msg):
        if len(msg) == 4 + 1 + 2:
            try:
                cookie, msgType, port = struct.unpack('<4sbH', msg)
                if (cookie == b'\xba\xdc\xcd\xab') and (msgType == int.from_bytes(b'\x02', "little")):
                    return port
            except:
                pass
            try:
                cookie, msgType, port = struct.unpack('>4sbH', msg)
                if (cookie == b'\xab\xcd\xdc\xba') and (msgType == int.from_bytes(b'\x02', "big")):
                    return port
            except:
                pass

        else:
            try:
                cookie, msgType, port = struct.unpack('IbH', msg)
                if (cookie == 0xabcddcba) and (msgType == 0x2):
                    return port
            except:
                pass
        return None

    def getIP(self):
        try:
            ip = int(input("press 1 for eth1 or 2 for eth2:    -     \t"))
            if ip == 1 or ip == 2:
                ip = get_if_addr("eth" + str(ip))

            else:
                ip = get_if_addr("eth1")
        except :
            return self.getIP()
        return ip

    def getOffer(self):
        try:
            self.udpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.udpClientSocket.setblocking(True)

            self.udpClientSocket.bind(
                ("", self.udpPort))  # (str(ipaddress.ip_network( self.UDPip  + '/21', False).broadcast_address)
            print(self.magenta, "Client started, listening for offer requests...", self.colorReset)
            while True:
                msg, (ip, _) = self.udpClientSocket.recvfrom(2048)

                port = self.unpackPort(msg)
                # print(f"recive from {str(ip)} /  {str(port)}")
                if port is not None:
                    break

            self.host, self.port = ip, port
        except:
            pass
        finally:
            self.udpClientSocket.close()

    def connecting_to_a_server(self):
        try:
            print(self.magenta, f"Received offer from {self.host}, attempting to connect...", self.colorReset)
            self.clientSocket = socket.socket()
            self.clientSocket.setblocking(True)
            self.clientSocket.connect((self.host, self.port))
            self.clientSocket.send(str.encode(self.teamName + '\n'))
        except:
            pass

    def game_mode(self):
        try:
            response = self.clientSocket.recv(2048)
            if response == b'':
                return
            try:
                sys.stdin.open()
            except:
                pass
            print(response.decode(), "\n")

            # if self.inputListener is None:
            #     self.inputListener = Thread(target=self._getMessegeC, daemon=True)
            #     self.inputListener.start()
            try:
                self.gameOn = True
                selector = selectors.DefaultSelector()
                selector.register(sys.stdin, selectors.EVENT_READ, self._getMessegeC)
                selector.register(self.clientSocket, selectors.EVENT_READ, self._handle_write)
                setings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
            except:
                pass

            while self.clientSocket is not None:
                sys.stdin.flush()
                events = selector.select()
                for event, _ in events:
                    event.data()

            selector.close()
            self.clientSocket.close()
            self.gameOn = False

            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, setings)

        except :
            pass

    def _handle_write(self):
        try:
            msg = self.clientSocket.recv(2048)
            print(self.underline,self.cyan,msg.decode(),self.colorReset)
            sys.stdout.flush()
        except socket.error as e:
            pass

        self.clientSocket.close()
        self.clientSocket = None

    def _getMessegeC(self):
        try:
            msg = sys.stdin.read(1)  # input()   #  os.read(sys.stdin ,1)  #
            if self.gameOn:
                self.clientSocket.send(str.encode(msg))
        except:
            pass


QuickMathClient().run()
