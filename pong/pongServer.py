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

class Server:
    def __init__(self, port: int):
        self.window_width = 800
        self.window_height = 600
        self.port = port
        self.leftPaddleState = ""
        self.rightPaddleState = ""
        # x,y coords for each
        # may be useful to pull out paddle states into classes, but might be too much

    def start(self):
        # some kind of data initialization
        # main loop...

        # what happens when server receives connectClient?
        # what happens when client disconnects?
        # what happens when one client wins? endgame state?
        # restart is extra credit... :D

        if rightClient.sync < leftClient.sync:
            greenFlag(rightClient)
        else:
            greenFlag(leftClient)
        pass

    def greenFlag(client):

        send_packet_to_client(client, "you_can_update_now:), also here is opponent's info")

        pass
    def sendClientInitPacket(self):
        if leftAssigned:
            sendInitLeft()
        elif rightAssigned:
            sendInitLeft()
        else:
            sendInitSpectator()

if __name__ == "__main__":
    server = Server(8080)
    server.start()

