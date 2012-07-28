#!/usr/bin/env python

import curses
from clientUI import *
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver

import argparse

import getpass      #used to get logged in username

class GameClient(LineReceiver):
    def __init__(self):
        self.state = 'New'

    def lineReceived(self,line):
        if line == 'name?':
            self.sendLine(self.factory.name)
        if line == 'taken':
            raise Exception('name taken')

    def connectionLost(self,reason):
        reactor.stop()

class GameFactory(ClientFactory):
    protocol = GameClient

    def __init__(self,name):
        self.name = name

class TwistedDisplay(Display):
    def doRead(self):           #called by twisted's reactor
        char = self.getCh()
        if char == 27:
            self._statusBar.setStatus('exiting')
            sleep(.5)
            reactor.stop()
        elif char == curses.KEY_NPAGE:
            self.scroll(1)
            self._statusBar.setStatus('page down')
        elif char == curses.KEY_PPAGE:
            self.scroll(-1)
            self._statusBar.setStatus('page up')
        elif char == curses.KEY_UP:
            self.moveSelection(-1)
            self._statusBar.setStatus('up')
        elif char == curses.KEY_DOWN:
            self.moveSelection(1)
            self._statusBar.setStatus('down')
        elif char == curses.KEY_LEFT:
            self.changeColSelect(-1)
        elif char == curses.KEY_RIGHT:
            self.changeColSelect(1)
        elif char == ord('q'):
            reactor.stop()
        elif char == ord(' '):
            self.toggleMark()
        # elif char == -1:
            # pass
        # else:
            # raise Exception(char)

    def logPrefix(self): return 'CursesClient'

    def connectionLost(self,reason):
        pass

    def fileno(self):
        return 0

def main(stdscr):
    parser = argparse.ArgumentParser()
    parser.add_argument('name',type=str,default=getpass.getuser())
    parser.add_argument('-p','--port',default=6814,type=int)
    parser.add_argument('-a','--address',type=str, \
            default='mattfilmer.student.rit.edu') 
    args = parser.parse_args()
    
    display = TwistedDisplay(stdscr)

    factory = GameFactory(args.name)

    reactor.addReader(display)
    reactor.connectTCP(args.address,args.port,factory)
    reactor.run()

if __name__ == '__main__':
    curses.wrapper(main)
