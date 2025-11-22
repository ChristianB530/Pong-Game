# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client

# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

class Connection:
    def __init__(self, conn, side_str):
        self.conn = conn
        self.sync = 0
        self.side_str = side_str

class Server:
    def __init__(self, port: int):
        self.window_width = 800
        self.window_height = 600
        self.port = port
        self.leftPaddleState = ""
        self.rightPaddleState = ""
        self.sock = None

        # (ass)
        self.left_connection = None
        self.left_flagged = False
        self.right_connection = None
        self.right_flagged = False

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
                    self.left_connection = [conn, 0]
                elif self.right_connection is None:
                    side_str = "right"
                    self.right_connection = [conn, 0]
                else:
                    side_str = "spectator"

                response = "no_u 800 600 " + side_str
                conn.send(bytes(response, "utf-8"))
                side = side_str

            elif args[0] == "sync":
                sync = int(args[1])
                if args[2] == "left":
                    self.left_connection[1] = sync
                    self.left_flagged = False
                else:
                    self.right_connection[1] = sync
                    self.right_flagged = False

            elif args[0] == "paddle":
                #args = ["paddle", x, y, moving]
                x = int(args[1])
                y = int(args[2])
                moving = args[3]
                #This should tell you paddle, location, and movement
                print(f"Paddle info from {addr}. {x},{y},{moving}")

        print(f"Closing {addr}")
        if side == "left":
            self.left_connection = None
        elif side == "right":
            self.right_connection = None
        conn.close()

    def update(self, foo):
        while True:
            if self.left_connection is None or self.right_connection is None:
                continue

            print("we are now updating")
            if self.left_connection[1] >= self.right_connection[1] and not self.left_flagged:
                self.greenFlag(self.right_connection[0], self.right_connection[1])
                self.left_flagged = True
            if self.left_connection[1] <= self.right_connection[1] and not self.right_flagged:
                self.greenFlag(self.left_connection[0], self.left_connection[1])
                self.right_flagged = True

    def greenFlag(self, cli, sync):
        message = "sync " + str(sync)
        cli.send(bytes(message, "utf-8"))

if __name__ == "__main__":
    server = Server(65431)
    server.start()

