Contact Info
============

Group Members & Email Addresses:

    Christian Brewer, cebr276@uky.edu
    Caleb Burnett, cdbu246@uky.edu
    Ben Carey, bjca251@uky.edu

Versioning
==========

Github Link: https://github.com/ChristianB530/Pong-Game

General Info
============
This project uses simple socket programming to synchronize two clients playing
the classic game Pong together. By using a server, we can connect two players
an arbitrary distance away to the same server, provided its hosted on an
accessible IP address.

Install Instructions
====================

A few of us *nix users needed to create a virtual environment in order to run
the project. To do so, open a terminal and run the following lines:

```bash
python3 -m venv .venv/
source .venv/bin/activate
```

Now you should be able to run pip commands from the terminal without getting
pesky "externally managed environment" errors and without needing to mess with
path dependencies.

In any case, run the following line to install the required libraries for this
project:

```bash
pip3 install -r requirements.txt
```

The only requirement for this project is the latest `pygame`.

Known Bugs
==========
- It crashes when a client disconnects from the server.  
- The clients that are spectators have sync issues.  
