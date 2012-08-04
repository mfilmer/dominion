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

The client.py file should be run in order to connect to an existing server. Command line 
options can be specified to do things... testing