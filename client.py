#!/usr/bin/env python

import curses
from clientUI import *

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver

import textwrap

import os           #check what os we are on for the windows twisted hack
os.putenv("ESCDELAY","25")  #also set ESCDELAY to 25ms
import getpass      #used to get logged in username
import argparse
from ast import literal_eval    #safer than eval()

class GameClient(LineReceiver):
    def __init__(self,factory,display):
        self.display = display
        self.factory = factory
        self.name = self.factory.name
        self.display.setClient(self)
        self.gameRunning = False
        self.myTurn = False
        self.phase = 'Wait'
        self.currentPlayer = ''

    def lineReceived(self,line):
        if line == 'name?':
            self.sendLine(self.factory.name)
        elif line == 'taken':
            raise Exception('name taken')
        elif line == 'okay':
            pass
        elif line == 'starting':
            self.display._columns = ColList([x[1] for x in \
                    self.display._columns],['Hand','Field','Store'])
            #self.display._columns = [(['Hand','Field','Store'][i],\
                    #self.display._columns[i][1]) for i in range(3)]
            for func,col in self.display._columns:
                col.setTitle(func,tAlign='Center')
            self.gameRunning = True
            self.display.setTitle('Dominion')
        elif line == 'your turn':
            self.display.setStatus('My Turn')
            self.myTurn = True
            self.phase = 'Action'
        elif line[0:6] == 'data: ':
            if line[6:12] == 'hand: ':
                self.display.hand = literal_eval(line[12:])
            elif line[6:13] == 'field: ':
                self.display.field = literal_eval(line[13:])
            elif line[6:15] == 'discard: ':
                self.display.discard = literal_eval(line[15:])
            elif line[6:13] == 'store: ':
                self.display.store = literal_eval(line[13:])
            elif line[6:13] == 'stash: ':
                self.display.setStash(*tuple(map(int,line[13:].split())))
            elif line[6:17] == 'full text: ':
                try:        #for some reason this makes windows happy
                    self.display.displayFullText(line[17:])
                except:
                    pass
            else:
                self.unrecognizedServerRequest(line)
        elif line[0:6] == 'turn: ':
            self.display.setStatus(line[6:] + '\'s turn')
            self.currentPlayer = line[6:]
            self.myTurn = False
        elif line[0:7] == 'phase: ':
            if self.myTurn:
                self.phase = line[7:]
                self.display.setStatus(self.phase + ' phase')
            else:
                self.display.setStatus(self.currentPlayer+' enters '+line[7:]+\
                        ' phase')
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
        self._popupWindow = None
        Display.__init__(self,stdscr)
        self._playerList = []
        self._hand = []
        self._field = []
        self._store = []
        self._discard = []
        self._inPopup = False
        self.setTitle('Dominion - In Lobby')
        self._columns.getCol(0).setTitle('Players',tAlign='Center')

    def doRead(self):           #called by twisted's reactor
        char = self.getCh()
        if char == -1:          #no key was pressed
            if os.name == 'nt':
                reactor.callLater(0.01,self.doRead)
            return

        if self._popupWindow is not None:
            self.handlePopupKey(char)
        elif char == ord('x'):
            self._popupWindow = YesNoWindow()
            #self._popupWindow = MultiSelectionDialogue((0,24),title='Choose',\
                    #height=self._termHeight-1,width=32)
            #self._popupWindow.setRowData(['row '+str(x)for x in range(25)])
        elif char == 27:            #ESC key
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
        elif char == ord('n'):
            self.client.sendLine('advance phase')
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
            cardName = self.getSelectedCardName()
            self.client.sendLine('get: full text: ' + cardName)
        elif os.name == 'nt':
            if char == 547:   #shift up (windows)
                self.statusHistory(1)
            elif char == 548:   #shift down (windows)
                self.statusHistory(-1)
        elif os.name == 'posix':
            if char == 337:   #shift up
                self.statusHistory(1)
            elif char == 336:   #shift down
                self.statusHistory(-1)

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
        
        if os.name == 'nt':
            reactor.callLater(0.01,self.doRead)

    def submit(self):       #handle the enter button press event
        client = self.client
        if client.gameRunning == True:
            #get selected column and its function
            function = self._columns.getFunc()
            column = self._columns.getCol()
            if client.myTurn:
                if client.phase == 'Action':
                    if function == 'Hand':
                        name = self.getSelectedCardName()
                        client.sendLine('play: ' + name)
                    else:
                        self.setStatus('Choose a card from your hand')
                elif client.phase == 'Buy':
                    if function == 'Store':
                        name = self.getSelectedCardName()
                        client.sendLine('buy: ' + name)
                    elif function == 'Hand':
                        name = self.getSelectedCardName()
                        client.sendLine('play: ' + name)
                    else:
                        self.setStatus('Invalid choice',True)
                elif client.phase == 'Cleanup':
                    pass
                elif client.phase == 'Wait':     
                    pass
            else:
                self.setStatus('Wait until your turn',True)

    def handlePopupKey(self,char):
        if char == 27:          #ESC key
            if self._popupWindow.escape():
                self._popupWindow = None
                self.refresh()
        elif char == curses.KEY_NPAGE:
            self._popupWindow.scrollVertical(1)
        elif char == curses.KEY_PPAGE:
            self._popupWindow.scrollVertical(-1)
        elif char == curses.KEY_UP:
            self._popupWindow.selectionVertical(-1)
        elif char == curses.KEY_DOWN:
            self._popupWindow.selectionVertical(1)
        elif char == ord('\n'):
            self.handlePopupSubmit(self._popupWindow.submit())
        elif char == ord(' '):
            self._popupWindow.toggleSelectedMark()

    def handlePopupSubmit(self,value):
        #do some stuff
        #probably end by closing the popup
        pass

    def getSelectedCardName(self):
        for func,col in self._columns:
            if col == self._columns.getCol():
                break
        if func == 'Hand' or func == 'Field':
            return self._columns.getCol().getSelectedText().split(' ',1)[1]
            #return self._columns[self._colIndex][1].getSelectedText().split()[1]
        elif func == 'Store':
            return self._columns.getCol().getSelectedText().split(' ',2)[2]
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

    def updateStashBar(self):
        for func,col in self._columns:
            if func == 'Field':
                B = '{0:<9}'.format('B:'+str(self._buys))
                A = '{0:^8}'.format('A:'+str(self._actions))
                M = '{0:>8}'.format('$:'+str(self._money))
                col.setStatus(B+A+M,curses.color_pair(1)|curses.A_BOLD)

    def setStash(self,buys,actions,money):
        self._buys = buys
        self._actions = actions
        self._money = money
        self.updateStashBar()

    def displayFullText(self,fullText):
        self._popupWindow = PopupColumn(title='Full Text',\
                height=self._termHeight-1)
        self._popupWindow.setRowData(textwrap.wrap(fullText,31))

    def refresh(self):
        Display.refresh(self)
        if self._popupWindow is not None:
            self._popupWindow.refresh()

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
                column.setRowData(data,reset=False)

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

    if os.name == 'nt':
        reactor.callLater(0.01,display.doRead)
    else:
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
