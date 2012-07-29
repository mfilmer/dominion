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
        self.display = display
        self.factory = factory
        self.name = self.factory.name
        self.display.setClient(self)
        self.gameRunning = False
        self.myTurn = False
        self.phase = 3

    def lineReceived(self,line):
        if line == 'name?':
            self.sendLine(self.factory.name)
        elif line == 'taken':
            raise Exception('name taken')
        elif line == 'okay':
            pass
        elif line == 'starting':
            self.display._columns = zip(['Hand','Field','Store'],\
                    [self.display._leftColumn,self.display._centerColumn,\
                    self.display._rightColumn])
            self.display._leftColumn.setTitle('Hand')
            self.display._centerColumn.setTitle('Field')
            self.display._rightColumn.setTitle('Store')
            self.gameRunning = True
            self.display.setTitle('Dominion')
        elif line == 'your turn':
            self.display.setStatus('My Turn')
            self.myTurn = True
            self.phase = 0
        elif line[0:6] == 'data: ':
            if line[6:12] == 'hand: ':
                self.display.hand = eval(line[12:])
            elif line[6:13] == 'field: ':
                self.display.field = eval(line[13:])
            elif line[6:15] == 'discard: ':
                self.display.discard = eval(line[15:])
            elif line[6:13] == 'store: ':
                self.display.store = eval(line[13:])
            else:
                self.unrecognizedServerRequest(line)
        elif line [0:6] == 'turn: ':
            self.display.setStatus(line[6:] + '\'s turn')
            self.myTurn = False
        elif line[0:16] == 'existingPlayer: ':
            self.display.addPlayer(line[16:])
        elif line[0:11] == 'newPlayer: ':
            self.display.addPlayer(line[11:])
            self.display.setStatus(line[11:] + ' has joined')
        elif line[0:12] == 'dropPlayer: ':
            self.display.setStatus(line[12:] + ' has dropped')
            self.display.dropPlayer(line[12:])
        elif line[0:6] == 'what: ':
            self.display.setStatus('Server didn\'t recognize: ' + line[6:])
        else:
            self.unrecognizedServerRequest(line)

    def connectionLost(self,reason):
        pass
        #raise Exception('connection lost')
        #reactor.stop()

    def unrecognizedServerRequest(self,line):
        self.display.setStatus('Unrecognized Server Request: '+line)
        with open(self.name+'.log','a') as f:
            f.write('Unknown Message: ' + line)
        #raise Exception('Unknown Message: ' + line)

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
    def __init__(self,stdscr):
        Display.__init__(self,stdscr)
        self._playerList = []
        self._hand = []
        self._field = []
        self._store = []
        self._discard = []
        self.setTitle('Dominion - In Lobby')

    def doRead(self):           #called by twisted's reactor
        char = self.getCh()
        if char == 27:          #ESC key
            #will eventually clear selection
            pass
        elif char == curses.KEY_NPAGE:
            self.scroll(1)
        elif char == curses.KEY_PPAGE:
            self.scroll(-1)
        elif char == curses.KEY_UP:
            self.moveSelection(-1)
        elif char == curses.KEY_DOWN:
            self.moveSelection(1)
        elif char == curses.KEY_LEFT:
            self.changeColSelect(-1)
        elif char == curses.KEY_RIGHT:
            self.changeColSelect(1)
        elif char == ord('q'):
            reactor.stop()
        elif char == ord(' '):
            self.toggleMark()
        #elif char == curses.KEY_ENTER: #for some reason this doesnt work
        elif char == ord('\n'):
            self.submit()
        elif char == ord('\t'):
            #will eventually switch between different player's screens
            pass
        elif char == ord('?'):
            #will eventually give card info
            pass
        elif char == 337:   #shift up
            self.client.display.statusHistory(-1)
        elif char == 336:   #shift down
            self.client.display.statusHistory(1)

        #perhaps implement these two to allow horizontal scrolling in the status
        #bar area
        #elif char == SHIFT RIGHT:
            #pass
        #elif char == SHIFT LEFT:
            #pass
        #elif char == -1:
            #pass
        #else:
            #raise Exception(char)

    def submit(self):       #handle the enter button press event
        client = self.client
        if client.gameRunning == True:
            #get selected column and its function
            for function,column in self._columns:
                if column == self._currentCol:
                    break
            if client.myTurn:
                if client.phase == 0:       #action phase
                    if function == 'Hand':
                        name = self.getSelectedCardName()
                        client.sendLine('play: ' + name)
                    else:
                        self.setStatus('Choose a card from your hand')
                elif client.phase == 1:     #buy phase
                    if function == 'Store':
                        name = self.getSelectedCardName()
                        client.sendLine('buy: ' + name)
                    else:
                        self.setStatus('Choose a card from the store')
                elif client.phase == 2:     #cleanup phase
                    pass
                #wait phase (other player's turns)
                elif client.phase == 3:     
                    pass
            else:
                self.setStatus('Wait until your turn')

    def getSelectedCardName(self):
        for func,col in self._columns:
            if col == self._currentCol:
                break
        if func == 'Hand' or func == 'Field':
            return self._currentCol.getSelectedText().split()[1]
        elif func == 'Store':
            return self._currentCol.getSelectedText().split()[2]
        else:
            self.setStatus('You tried to select a card from a column with an '+\
                    'unrecognized function')

    def setClient(self,client):
        self.client = client

    def addPlayer(self,player):
        if not player in self._playerList:
            self._playerList.append(player)
            for contents,column in self._columns:
                if contents == 'Players':
                    column.setRowData(self._playerList)
    def dropPlayer(self,player):
        if player in self._playerList:
            del(self._playerList[self._playerList.index(player)])
            for contents,column in self._columns:
                if contents == 'Players':
                    column.setRowData(self._playerList)

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

    @property
    def field(self):
        return self._field
    @field.setter
    def field(self,value):
        self._field = value
        for contents,column in self._columns:
            if contents == 'Field':
                data = ['('+str(c)+') ' + n for n,c in self._field.items()]
                column.setRowData(data)

    @property
    def discard(self):
        return self._discard
    @discard.setter
    def discard(self,value):
        self._discard = value
        for contents,column in self._columns:
            if contents == 'Discard':
                data = ['('+str(c)+') '+n for n,c in self._discard.items()]
                column.setRowData(data)

    @property
    def store(self):
        return self._discard
    @store.setter
    def store(self,value):
        self._store = value
        for contents,column in self._columns:
            if contents == 'Store':
                for name in self._store:
                    cost,count = self._store[name]
                    if count == u'\u221e':
                        self._store[name] = (cost,float('inf'))
                data = ['('+str(count)+') $'+str(cost)+' '+name \
                        for name,(cost,count) in self._store.items()]
                for i,row in enumerate(data):
                    if row[1:4] == 'inf':
                        data[i] = data[i][0:1] + '*' + data[i][4:]
                column.setRowData(data)

    #twisted stuff that is necessary but not really helpful
    def logPrefix(self): return 'CursesClient'

    def connectionLost(self,reason):
        pass
        #raise Exception('connection lost')
        #reactor.stop()

    def fileno(self):
        return 0

def main(stdscr,args):
    display = TwistedDisplay(stdscr)

    factory = GameFactory(args.name,display)

    reactor.addReader(display)
    reactor.connectTCP(args.address,args.port,factory)
    reactor.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--name',type=str,default=getpass.getuser())
    parser.add_argument('-p','--port',default=6814,type=int)
    parser.add_argument('-a','--address',type=str, \
            default='mattfilmer.student.rit.edu') 
    args = parser.parse_args()

    curses.wrapper(main,args)
