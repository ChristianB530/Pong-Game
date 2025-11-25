# =================================================================================================
# Contributing Authors:	    Ben Carey, Christian Brewer, Caleb Burnett
# Email Addresses:          bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Date:                     11/23/2025
# Purpose:                  The server connects the players and pass information about the games to the players.
#                           Such as paddle locations, scores, player inputs, synchronization variables etc.. 
# =================================================================================================

import socket
import threading
from time import sleep

#Connection class for player
#Stores data for each player such as paddle position, score, and synchronization value.
class Connection:
    def __init__(self, conn, side_str) -> None:
        self.conn: socket.SocketType = conn
        self.sync: int = 0
        self.side_str: str = side_str
        self.x: int = 0
        self.y: int = 0
        self.score: int = 0

#Connection Class for spectator
#Spectator receive game information
#Spectator are not allow to send information to the server
class Spectator:
    def __init__(self, conn):
        self.conn = conn
        self.left_x = 0
        self.left_y = 0
        self.left_score = 0
        self.right_x = 0
        self.right_y = 0
        self.right_score = 0

#Multiplayer server
#Handles player assignment, game state, sync between clients
class Server:
    def __init__(self, port: int):
        #Window Size
        self.window_width = 800
        self.window_height = 600
        #Server Socket
        self.port = port
        self.leftPaddleState = ""
        self.rightPaddleState = ""
        self.sock = None
        self.ball_pos = [0, 0]

        #Player State
        self.left_connection = None
        self.left_flagged = False
        self.right_connection = None
        self.right_flagged = False

        #Spectators list
        self.spectators: list[Connection] = []
        # x,y coords for each
        # may be useful to pull out paddle states into classes, but might be too much

    #Start and listen to clients
    def start(self):
        # some kind of data initialization
        # main loop...
        #Create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #listen all network
        address = "0.0.0.0"
        self.sock.bind((address, self.port))
        self.sock.listen()
        print("Server started at " + address + ":" + str(self.port))
        #Background game update
        threading.Thread(target=Server.update, args=(self,0), daemon=True).start()

        #Always accept connections
        while True:
            conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            threading.Thread(target=Server.handleClient, args=(self, conn, addr), daemon=True).start()

        # what happens when one client wins? endgame state?
        # restart is extra credit... :D
    
    # handles message from a client
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
            #Player try to join
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
            #Sync logic for client
            elif args[0] == "sync":
                sync = int(args[1])
                if args[2] == "left":
                    self.left_connection.sync = sync
                    self.left_flagged = False
                else:
                    self.right_connection.sync = sync
                    self.right_flagged = False
            #Paddle info update
            #args = ["paddle",side, x, y, moving, lscore, rscore]
            elif args[0] == "paddle":
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
            elif args[0] == "restar":
                #Reset the position and score
                #This will reset if one party decide to do the reset.
                self.left_connection.x = 50
                self.left_connection.y = self.window_height // 2
                self.left_connection.score = 0
                self.right_connection.x = self.window_width - 50
                self.right_connection.y = self.window_height // 2
                self.right_connection.score = 0

                # Notify both players so they reset locally too
                self.left_connection.conn.send(b"reset_ack")
                self.right_connection.conn.send(b"reset_ack")



        #Handdle disconnection
        print(f"Closing {addr}")
        if side == "left":
            self.left_connection = None
        elif side == "right":
            self.right_connection = None
        else:
            #Remove all spectators
            for i in range(len(self.spectators)):
                if self.spectators[i].conn == conn:
                    self.spectators.remove(i)
                    break
        conn.close()

    #Main server update
    def update(self, foo):
        while True:
            sleep(0.01)

            # Only update is both player is connected
            if self.left_connection is None or self.right_connection is None:
                continue

            #Manage sync
            if self.left_connection.sync >= self.right_connection.sync and not self.left_flagged:
                self.greenFlag(self.right_connection, self.left_connection)
                self.left_flagged = True

            if self.left_connection.sync <= self.right_connection.sync and not self.right_flagged:
                self.greenFlag(self.left_connection, self.right_connection)
                self.right_flagged = True

            #Update spectator
            for tator in self.spectators:
                # message = "tator "
                '''
                # message structure = 
                [0] = "spectator"
                [1] = left x
                [2] = left y
                [3] = left score
                [4] = right x
                [5] = right y
                [6] = right score 
                '''
                message += "spectator " + str(self.left_connection.x) + " " + str(self.left_connection.y) + " " + str(self.left_connection.score) + " "
                message += str(self.right_connection.x) + " " + str(self.right_connection.y) + " " + str(self.right_connection.score)
                Connection.conn.send(bytes(message, "utf-8"))

    #Send sync info to clients
    def greenFlag(self, to_update: Connection, opponent: Connection):
        message = "sync " + str(opponent.sync) + " " + str(opponent.x) + " " + str(opponent.y) + " " + str(opponent.score)
        to_update.conn.send(bytes(message, "utf-8"))

if __name__ == "__main__":
    server = Server(65431)
    server.start()

