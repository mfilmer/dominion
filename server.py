#!/usr/bin/env python

from __future__ import print_function

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import argparse

import Dominion

class Player(LineReceiver):
    def __init__(self,factory,users,maxPlayers=2):
        self.maxPlayers = maxPlayers
        self.users = users
        self.factory = factory
        self.name = None
        self.state = 'New'

    def connectionMade(self):
        self.sendLine('name?')

    def connectionLost(self,reason):
        if self.users.has_key(self.name):
            del self.users[self.name]
            for name,protocol in self.users.iteritems():
                protocol.sendLine('dropPlayer: ' + self.name)
            print(self.name + ' has left')

    def registerNewPlayer(self,name):
        if self.users.has_key(name):
            self.sendLine('taken')
            print(name + ' already taken')
        else:
            self.name = name
            self.sendLine('okay')
            print(name + ' has joined')
            self.state = 'InLobby'
            self.users[name] = self
            for name,protocol in self.users.iteritems():
                if protocol == self:
                    playerCount = len(self.users)
                    for name,protocol in self.users.iteritems():
                        self.sendLine('existingplayer: ' + name)
                else:
                    protocol.sendLine('newplayer: ' + name)
            if len(self.users) == self.maxPlayers:
                print('Starting Game...')
                self.factory.game = Dominion.game(self.users.keys())
                self.factoryturn = self.factory.game.next()
                players = self.factory.game.getPlayers()
                for name,protocol in self.users.iteritems():
                    protocol.sendLine('starting')
                    protocol.state = 'Waiting'
                    protocol.player = [p for p in players if p.getName() == \
                            name][0]
                    hand = protocol.player.getDeck().getHand()
                    dHand = {}
                    for card in hand:
                        name = card.getName()
                        dHand[name] = hand.countCardsByName(name)
                    hand = repr(dHand)
                    protocol.sendLine('cmd: hand: ' + hand)
                    print(hand)

    def lineReceived(self,line):
        if self.state == 'New': #they sent their name. tell everyone about it
            self.registerNewPlayer(line)
        elif self.state == 'InLobby':
            print(line)
            pass    #perhaps this is a chat message. implement later
        else:       #sould not have received this line
            print('received bad line from ' + self.name + ': ')
            print(line)

class GameFactory(Factory):
    def __init__(self):
        self.users = {}
        self.game = None
        self.turn = None

    def buildProtocol(self,addr):
        return Player(self,self.users)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=6814)
    parser.add_argument('-P','--players',type=int,default=2)
    args = parser.parse_args()
    
    reactor.listenTCP(args.port,GameFactory())
    reactor.run()

if __name__ == '__main__':
    main()
