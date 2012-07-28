#!/usr/bin/env python

import curses
from clientUI import *
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver

import argparse

import getpass      #used to get logged in username

class GameClient(LineReceiver):
    def __init__(self,factory,display):
        self.state = 'New'
        self._hand = []
        self.display = display
        self.factory = factory
        self.name = self.factory.name
        self.display.setClient(self)

    def lineReceived(self,line):
        if line == 'name?':
            self.sendLine(self.factory.name)
        if line == 'taken':
            raise Exception('name taken')
        if line[0:11] == 'cmd: hand: ':
            self.display.hand = eval(line[11:])

    def connectionLost(self,reason):
        pass
        #raise Exception('connection lost')
        #reactor.stop()

    @property
    def hand(self):
        return self._hand
    @hand.setter
    def hand(self,value):
        self._hand = value

class GameFactory(ClientFactory):
    protocol = GameClient

    def __init__(self,name,display):
        self.name = name
        self.display = display

    def buildProtocol(self,addr):
        return GameClient(self,self.display)

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

    def setClient(self,client):
        self.client = client

    @property
    def hand(self):
        return self._hand
    @hand.setter
    def hand(self,value):
        self._hand = value
        for contents,column in self._columns:
            if contents == 'Hand':
                data = ['('+str(c)+') ' + n for n,c in self._hand.items()]
                column.setRowData(data)

    #twisted stuff that is necessary but not really helpful
    def logPrefix(self): return 'CursesClient'

    def connectionLost(self,reason):
        raise Exception('connection lost')
        #reactor.stop()

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

    factory = GameFactory(args.name,display)

    reactor.addReader(display)
    reactor.connectTCP(args.address,args.port,factory)
    reactor.run()

if __name__ == '__main__':
    curses.wrapper(main)
