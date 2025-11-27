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
from typing import Tuple

# =====================================================
# Author: Ben Carey, Caleb Burnett
# Email Address: bjca251@uky.edu, cdbu246@uky.edu
# Uses and Invariants:
# - Used to serialize game state received from a client. Also used to "green
#   flag" clients once they are synced.
# - Connection remains active to client during its lifetime.
# - side_str never changes.
# =====================================================
class Connection:
    def __init__(self, conn: socket.SocketType, side_str: str) -> None:
        self.conn: socket.SocketType = conn
        self.sync: int = 0
        self.side_str: str = side_str
        self.x: int = 0
        self.y: int = 0
        self.score: int = 0

# =====================================================
# Author: Ben Carey
# Email Address: bjca251@uky.edu
# Uses and Invariants:
# - Used to update game state sent to a spectator.
# =====================================================
class Spectator:
    def __init__(self, conn: socket.SocketType) -> None:
        self.conn: socket.SocketType = conn
        self.left_x: int = 0
        self.left_y: int = 0
        self.left_score: int = 0
        self.right_x: int = 0
        self.right_y: int = 0
        self.right_score: int = 0

# =====================================================
# Author: Ben Carey, Caleb Burnett, Christian Brewer
# Email Address: bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Uses and Invariants:
# - Synchronizes clients connected and playing pong together.
# - Distributes client information to opponents and spectators.
# - Relays important game state information from the main client (the left
#   client) to the other clients.
# =====================================================
class Server:
    def __init__(self, port: int) -> None:
        #Window Size
        self.window_width: int = 800
        self.window_height: int = 600
        #Server Socket
        self.port: int = port
        self.leftPaddleState: str = ""
        self.rightPaddleState: str = ""
        self.sock: socket.SocketType | None = None
        self.ball_pos: list[int] = [0, 0]

        self.left_connection: Connection | None = None
        self.left_flagged: bool = False
        self.right_connection: Connection | None = None
        self.right_flagged: bool = False

        #Spectators list
        self.spectators: list[Spectator] = []
        # x,y coords for each
        # may be useful to pull out paddle states into classes, but might be too much

# =====================================================
# Author: Ben Carey, Caleb Burnett, Christian Brewer
# Email Address: bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Uses and Invariants:
# - Begins running the server. Should only be called once, and will block until
#   the server closes.
# =====================================================
    def start(self) -> None:
        # Create a new socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set configuration so that we free the port once the server closes.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # We host on the local machine.
        address = "0.0.0.0"
        self.sock.bind((address, self.port))
        # Begin listening for connections.
        self.sock.listen()
        print("Server started at " + address + ":" + str(self.port))
        # Start server game update thread (will synchronize clients).
        threading.Thread(target=Server.update, args=(self,0), daemon=True).start()

        # Loop forever, spawning new threads for connected clients as they join.
        while True:
            conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            threading.Thread(target=Server.handleClient, args=(self, conn, addr), daemon=True).start()

# =====================================================
# Author: Ben Carey, Caleb Burnett, Christian Brewer
# Email Address: bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Uses and Invariants: - Called in a newly spawned thread for each client that connects to the server. - Processes all packets sent by the client until the client disconnects.
# =====================================================
    def handleClient(self, conn: socket.SocketType, addr: str) -> None:
        print("connection get!")
        side = ""
        recv = None
        while True:
            recv = conn.recv(1024).decode()
            if not recv:
                break

            args = recv.split(' ')
            # Handle client connection establishment.
            if args[0] == "get_rekt":
                if self.left_connection is None:
                    side_str = "left"
                    self.left_connection = Connection(conn, side_str)
                elif self.right_connection is None:
                    side_str = "right"
                    self.right_connection = Connection(conn, side_str)
                else:
                    side_str = "spectator"
                    self.spectators.append(Spectator(conn))

                # Let client prepare itself.
                response = "no_u 800 600 " + side_str
                conn.send(bytes(response, "utf-8"))
                side = side_str
            # Handle if client sends a sync packet, updating local game state.
            elif args[0] == "sync":
                sync = int(args[1])
                if args[2] == "left":
                    self.left_connection.sync = sync
                    self.left_flagged = False
                    self.ball_pos[0] = int(args[3])
                    self.ball_pos[1] = int(args[4])
                else:
                    self.right_connection.sync = sync
                    self.right_flagged = False

            # Handle if client sends current paddle information.
            elif args[0] == "paddle":
                #args = ["paddle",side, x, y, moving, lscore, rscore]
                side = args[1]
                if side == "left":
                    self.left_connection.x = int(args[2])
                    self.left_connection.y = int(args[3])
                    self.left_connection.moving = args[4]
                elif side == "right":
                    self.right_connection.x = int(args[2])
                    self.right_connection.y = int(args[3])
                    self.right_connection.moving = args[4]

                if self.left_connection:
                    self.left_connection.score = int(args[5])
                if self.right_connection:
                    self.right_connection.score = int(args[6])
            # Handle if client requests a restart.
            elif args[0] == "restart":
                #Reset the position and score
                #This will reset if one party decide to do the reset.
                self.left_connection.x = 50
                self.left_connection.y = self.window_height // 2
                self.left_connection.score = 0
                self.right_connection.x = self.window_width - 50
                self.right_connection.y = self.window_height // 2
                self.right_connection.score = 0

                # Notify both players so they reset locally too
                self.left_connection.conn.send(b"restart 0 0 0 0 0 0 0 \n")
                self.right_connection.conn.send(b"restart 0 0 0 0 0 0 0 \n")


        #Handle disconnection
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

# =====================================================
# Author: Ben Carey, Caleb Burnett, Christian Brewer
# Email Address: bjca251@uky.edu, cdbu246@uky.edu, cebr276@uky.edu
# Uses and Invariants:
# - Updates all spectators with full game state information.
# - Syncs clients by "flagging" which clients can proceed to update. In doing
#   so, we ensure that clients have the opportunity to catch up by a frame to
#   the opponents state.
# - NOTE: foo has no use; it is required for ensuring that we can bind
#   parameters to member functions properly when calling the Thread
#   constructor.
# =====================================================
    def update(self, foo: int) -> None:
        while True:
            sleep(0.01)

            # update spectators.
            for tator in self.spectators:
                message = "tator "
                message += str(self.left_connection.x) + " " + str(self.left_connection.y) + " " + str(self.left_connection.score) + " "
                message += str(self.right_connection.x) + " " + str(self.right_connection.y) + " " + str(self.right_connection.score) + " " + str(self.ball_pos[0]) + " " + str(self.ball_pos[1]) + " "
                tator.conn.send(bytes(message, "utf-8"))

            if self.left_connection is None or self.right_connection is None:
                continue

            if self.left_connection.sync >= self.right_connection.sync and not self.left_flagged:
                self.greenFlag(self.right_connection, self.left_connection, send_ball = True)
                self.left_flagged = True

            if self.left_connection.sync <= self.right_connection.sync and not self.right_flagged:
                self.greenFlag(self.left_connection, self.right_connection)
                self.right_flagged = True

    def greenFlag(self, to_update: Connection, opponent: Connection, send_ball = False) -> None:
        message = "sync " + str(opponent.sync) + " " + str(opponent.x) + " " + str(opponent.y) + " " + str(self.left_connection.score) + " " + str(self.right_connection.score)
        if send_ball:
            message += " " + str(self.ball_pos[0]) + " " + str(self.ball_pos[1])
        to_update.conn.send(bytes(message, "utf-8"))

if __name__ == "__main__":
    server = Server(65431)
    server.start()
