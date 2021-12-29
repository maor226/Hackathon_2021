import os
import socket
import threading
import struct
from scapy.all import *
from _thread import *
import time
import ipaddress


class QuickMathServer:

    def __init__(self):
        self.hostIP = 172.1.0.21
        self.host = None
        self.UDPport = 13117
        self.clientCount = 0
        self.players = []
        self.lockTCP = threading.Lock()
        self.gameStart = threading.Condition()
        self.gameAns = threading.Condition()
        self.gameEnd = threading.Condition()
        self.serverTCPSocket = None
        self.startGameMSG = None
        self.gameAnsMSG = None
        self.gameWinMSG = None

    def connectClientTCP(self, conn):

        def getMessege():
            buffer = ""
            while buffer.count('\n') == 0:
                buffer += conn.recv(2048).decode()
            msg, buffer = buffer.split('\n', 1)
            return msg

        try:
            teamName = getMessege()
            if self.addPlayer(teamName):
                self.gameStart.acquire()
                self.gameStart.wait()  # for waiting to the game to start
                self.gameStart.notify_all()
                self.gameStart.release()

                conn.sendall(self.startGameMSG)
                print(" sent to " + teamName)

                def _getMessege(conn):
                    try:
                        msg = conn.recv(2048)
                        self.gameAns.acquire()
                        self.gameAnsMSG = msg.decode(), self.players.index(teamName)
                        self.gameAns.notify_all()
                        self.gameAns.release()
                    except:
                        pass

                t = threading.Thread(target=_getMessege, args=(conn,), daemon=True)
                t.start()
                self.gameEnd.acquire()
                self.gameEnd.wait()  # for waiting to the game to end
                conn.sendall(self.gameWinMSG)
                self.gameEnd.release()
                conn.close()
            else:
                conn.close()
        except:
            try:
                conn.close()
            except:
                pass

    def addPlayer(self, name):
        self.lockTCP.acquire()
        if self.clientCount >= 2:
            self.lockTCP.release()
            return False
        self.clientCount += 1
        self.players.append(name)
        self.lockTCP.release()
        return True

    def beginGame(self):
        question = "2+2-1"
        anser = "3"
        self.startGameMSG = str.encode(f"""Welcome to Quick Maths.
        Player 1: {self.players[0]}
        Player 2: {self.players[1]}
        ==
        Please answer the following question as fast as you can:
        {question}""")
        time.sleep(10)
        self.gameStart.acquire()
        self.gameStart.notify_all()  # for waiting to the game to start
        self.gameStart.release()

        self.gameAns.acquire()
        self.gameAns.wait(timeout=10)
        self.gameAns.release()

        self.gameEnd.acquire()
        self.gameWinMSG = str.encode(f"""       Game over!
        The correct answer was {anser}!

        {f"Congratulations to the winner: {self.players[self.gameAnsMSG[1]] if self.gameAnsMSG[0] == anser else self.players[1 - self.gameAnsMSG[1]]} !" if self.gameAnsMSG is not None else "You such a baby"} """)
        self.gameEnd.notify_all()
        self.gameEnd.release()



    def run(self):
        while True:
            try:

                try:
                    self.serverTCPSocket = socket.socket()
                    self.serverTCPSocket.bind(("", 0))  # create the TCP listening socket
                except socket.error as e:
                    print(str(e))

                self.host, self.port = self.serverTCPSocket.getsockname()

                udpThread = threading.Thread(target=self.sendOffers)
                udpThread.start()

                thr = []
                self.players = []

                self.serverTCPSocket.listen()
                print(f"Server started, listening on IP address {self.hostIP}...")  # todo : in UDP
                while self.clientCount < 2:
                    try:
                        self.serverTCPSocket.settimeout(0.5)
                        conn, x = self.serverTCPSocket.accept()
                        print(str(x) + " attempting to connect ")
                        thr.append(threading.Thread(target=self.connectClientTCP, args=(conn,)))
                        thr[-1].start()
                    except:
                        pass

                self.beginGame()

                for t in thr:
                    t.join()
                self.serverTCPSocket.close()
                self.clientCount = 0
            except error as e:
                print(str(e))


QuickMathServer().run()
