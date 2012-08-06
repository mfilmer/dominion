dominion
========

Implementation of the Dominion card game

Requirements
------------

### Windows

* Python 2.6-2.7 (may work on older versions, will probably not work in python 3)
* Curses Module: [Available Here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses)
* Twisted Module: [Available Here](http://twistedmatrix.com/trac/)
* zope.interface: [Needed for twisted](http://pypi.python.org/pypi/zope.interface#download)

### Linux

* Python 2.6-2.7 (may work on older versions, will probably not work in python 3)
* Twisted Module (should be in repositories)
* zope.interface (may not be needed if twisted is installed from the repositories)


Use - Description of Files
--------------------------

The two important files are client.py and server.py.

### Client

The client.py file should be run in order to connect to an existing server. Options can be 
specified in command line arguments

--help    Show all command line arguments  
--name    Name to play with  
--port    Port to connect to on the server  
--address Address of the server to connect to

These options have defaults as follows:

name:     Logged in username

port:     6814


### Server

The server.py file should be run in order to start a game server. Options can be specified in 
command line argumnets.

--help      Show all command line arguments
--players   Number of players that should be in the game
--port      Port to listen on
--workingCardsOnly    Only randomizes with cards that are flagged as working
--expansions  List expansions to be in the pool of possible cards to play with

The defaults are:

players:      2

expansions:   Base Intrigue

Use - Client Interface
----------------------

The client commands are as follows (they will probably eventually be in a config file)

n:                  advance phase

q:                  quit game

?:                  show full card text

esc:                close an open popup window

enter:              submit (play card if in hand or buy if in store)

arrow keys:         move the cursor around the screen

shif arrow keys:    scroll through the status bar history (only works on some systems)