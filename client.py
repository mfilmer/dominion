#!/usr/bin/env python

import curses
from clientUI import *
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory

import argparse

import getpass      #used to get logged in username

class TwistedDisplay(Display):
    def doRead(self):           #called by twisted's reactor
        char = self.getCh()
        if char == 27:
            self._statusBar.setStatus('exiting')
            sleep(.5)
            raise Exception('Quit')
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
            raise Exception('Quit')
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
    
    reactor.addReader(display)
    #reactor.connectTCP(args.address,args.port,factory)
    reactor.run()

if __name__ == '__main__':
    curses.wrapper(main)

# class Interface(Protocol):
    # def dataReceived(self,data):
        # pass

# class GameClientFactory(ClientFactory):
    # def buildProtocol(self,addr):
        # return Interface()

# class Reaction(object):
    # def __init__(self,stdscr):
        # pass

# class Main(object):
    # def __init__(self,stdscr,display):
        # self._display = display
        # data = []
        # for i in range(30):
            # data.append('row ' + str(i))
        # self._display._leftColumn.setRowData(data)
        # self._display._centerColumn.setRowData(data)
        # self._display._rightColumn.setRowData(data)
        ##self._display._leftColumn.setTitle(' ')
        ##self._display._centerColumn.setTitle(' ')
        ##self._display._rightColumn.setTitle(' ')
        # self._display._redraw()
        # for i in range(1):
            # for i in range(10):
                # sleep(.05)
                # self._display._currentCol.scroll(1)
            # for i in range(10):
                # sleep(.05)
                # self._display._currentCol.scroll(-1)
    
        # stdscr.nodelay(True)

        # def doRead(self):
            # char = self._display.getCh()
            # if char == 27:
                # self._display._statusBar.setStatus('exiting')
                # sleep(.5)
                # raise Exception('Quit')
            # elif char == curses.KEY_NPAGE:
                # self._display.scroll(1)
                # self._display._statusBar.setStatus('page down')
            # elif char == curses.KEY_PPAGE:
                # self._display.scroll(-1)
                # self._display._statusBar.setStatus('page up')
            # elif char == curses.KEY_UP:
                # self._display.moveSelection(-1)
                # self._display._statusBar.setStatus('up')
            # elif char == curses.KEY_DOWN:
                # self._display.moveSelection(1)
                # self._display._statusBar.setStatus('down')
            # elif char == curses.KEY_LEFT:
                # self._display.changeColSelect(-1)
            # elif char == curses.KEY_RIGHT:
                # self._display.changeColSelect(1)
            # elif char == ord('q'):
                # raise Exception('Quit')
            # elif char == ord(' '):
                # self._display.toggleMark()
            # elif char == -1:
                # pass
            ##else:
                ##raise Exception(char)

# def setup(stdscr):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('name')
    # parser.add_argument('-a','--address',default='mattfilmer.student.rit.edu')
    # parser.add_argument('-p','--port',default=6814)
    # args = parser.parse_args()

    # display = Display(stdscr)
    # main = Main(stdscr,display)
    # reactor.addReader(main)
    # reactor.connectTCP(args.address,args.port,GameClientFactory)
    # reactor.run()

# if __name__ == '__main__':
    # curses.wrapper(setup)
