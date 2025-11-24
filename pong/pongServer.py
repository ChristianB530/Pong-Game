# =================================================================================================
# Contributing Authors:	    Ben Carey, Christian Bruwer, Caleb Burnett
# Email Addresses:          bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Date:                     11/23/2025
# Purpose:                  The server connects the players and pass information about the games to the players.
#                           Such as paddle locations, scores, player inputs, synchronization variables etc.. 
# =================================================================================================

import socket
import threading
from time import sleep

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client

# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

#Initiate the connection to players
class Connection:
    def __init__(self, conn, side_str) -> None:
        self.conn: socket.SocketType = conn
        self.sync: int = 0
        self.side_str: str = side_str
        self.x: int = 0
        self.y: int = 0
        self.score: int = 0

#Initiate the connection to spectators
class Spectator:
    def __init__(self, conn):
        self.conn = conn
        self.left_x = 0
        self.left_y = 0
        self.left_score = 0
        self.right_x = 0
        self.right_y = 0
        self.right_score = 0

class Server:
    def __init__(self, port: int):
        self.window_width = 800
        self.window_height = 600
        self.port = port
        self.leftPaddleState = ""
        self.rightPaddleState = ""
        self.sock = None
        self.ball_pos = [0, 0]

        self.left_connection = None
        self.left_flagged = False
        self.right_connection = None
        self.right_flagged = False

        self.spectators: list[Connection] = []
        # x,y coords for each
        # may be useful to pull out paddle states into classes, but might be too much

    def start(self):
        # some kind of data initialization
        # main loop...
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        address = "0.0.0.0"
        self.sock.bind((address, self.port))
        self.sock.listen()
        print("Server started at " + address + ":" + str(self.port))
        threading.Thread(target=Server.update, args=(self,0), daemon=True).start()

        while True:
            conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            threading.Thread(target=Server.handleClient, args=(self, conn, addr), daemon=True).start()

        # what happens when one client wins? endgame state?
        # restart is extra credit... :D

    def handleClient(self, conn, addr):
        print("connection get!")
        side = ""
        recv = None
        while True:
            recv = conn.recv(1024).decode()
            if not recv:
                break

            print(f"Received from {addr}: {recv}")

            args = recv.split(' ')
            if args[0] == "get_rekt":
                if self.left_connection is None:
                    side_str = "left"
                    self.left_connection = Connection(conn, 0)
                    #self.left_connection.x = 10
                    #self.left_connection.y = (self.screenHeight/2) - (25)
                elif self.right_connection is None:
                    side_str = "right"
                    self.right_connection = Connection(conn, 0)
                    #self.right_connection.x = self.screenWidth - 20
                    #self.right_connection.y = (self.screenHeight/2) - (25)
                else:
                    side_str = "spectator"
                    self.spectators.append(Spectator(conn))

                response = "no_u 800 600 " + side_str
                conn.send(bytes(response, "utf-8"))
                side = side_str

            elif args[0] == "sync":
                sync = int(args[1])
                if args[2] == "left":
                    self.left_connection.sync = sync
                    self.left_flagged = False
                else:
                    self.right_connection.sync = sync
                    self.right_flagged = False

            elif args[0] == "paddle":
                #args = ["paddle",side, x, y, moving, lscore, rscore]
                side = args[1]
                if side == "left":
                    self.left_connection.x = int(args[2])
                    self.left_connection.y = int(args[3])
                    self.left_connection.moving = args[4]
                    self.left_connection.score = args[5]
                elif side == "right":
                    self.right_connection.x = int(args[2])
                    self.right_connection.y = int(args[3])
                    self.right_connection.moving = args[4]
                    self.right_connection.score = args[6]

        print(f"Closing {addr}")
        if side == "left":
            self.left_connection = None
        elif side == "right":
            self.right_connection = None
        else:
            for i in range(len(self.spectators)):
                if self.spectators[i].conn == conn:
                    self.spectators.remove(i)
                    break
        conn.close()

    def update(self, foo):
        while True:
            sleep(0.01)

            for tator in self.spectators:
                message = "tator "
                message += str(self.left_connection.x) + " " + str(self.left_connection.y) + " " + str(self.left_connection.score) + " "
                message += str(self.right_connection.x) + " " + str(self.right_connection.y) + " " + str(self.right_connection.score)


            if self.left_connection is None or self.right_connection is None:
                continue

            if self.left_connection.sync >= self.right_connection.sync and not self.left_flagged:
                self.greenFlag(self.right_connection, self.left_connection)
                self.left_flagged = True

            if self.left_connection.sync <= self.right_connection.sync and not self.right_flagged:
                self.greenFlag(self.left_connection, self.right_connection)
                self.right_flagged = True

    def greenFlag(self, to_update: Connection, opponent: Connection):
        message = "sync " + str(opponent.sync) + " " + str(opponent.x) + " " + str(opponent.y) + " " + str(opponent.score)
        to_update.conn.send(bytes(message, "utf-8"))

if __name__ == "__main__":
    server = Server(65431)
    server.start()

