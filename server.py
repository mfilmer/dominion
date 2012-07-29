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

    def startGame(self):
        print('Starting Game...')
        self.factory.game = Dominion.game(self.users.keys())
        self.factory.turn = self.factory.game.next()
        players = self.factory.game.getPlayers()
        stores = self.factory.game.getStores()
        dStores = {}
        for store in stores:
            try:
                dStores[store.getName()]=(store.getCost(),len(store))
            except OverflowError:
                dStores[store.getName()]=(store.getCost(),u'\u221E')
        stores = repr(dStores)
        currentPlayerName = self.factory.turn.getPlayer().getName()
        print('starting player: ' + currentPlayerName)
        for name,protocol in self.users.iteritems():
            protocol.sendLine('starting')
            protocol.state = 'Waiting'
            protocol.player = [p for p in players if p.getName() == name][0]
            hand = protocol.player.getDeck().getHand()
            dHand = {}
            for card in hand:
                cardName = card.getName()
                dHand[cardName] = hand.countCardsByName(cardName)
            hand = repr(dHand)
            protocol.sendLine('data: hand: ' + hand)
            print(protocol.name + '\'s starting hand: ' + hand)
            protocol.sendLine('data: store: ' + stores)
            if name == currentPlayerName:
                protocol.sendLine('your turn')
            else:
                protocol.sendLine('turn: ' + currentPlayerName)

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
                    pass
                    for name,protocol in self.users.iteritems():
                        self.sendLine('existingPlayer: ' + name)
                else:
                    protocol.sendLine('newPlayer: ' + self.name)
            if len(self.users) == self.maxPlayers:
                self.startGame()

    def lineReceived(self,line):
        if self.state == 'New': #they sent their name. tell everyone about it
            self.registerNewPlayer(line)
        elif self.state == 'InLobby':
            print(line)
            pass    #perhaps this is a chat message. implement later
        else:       #sould not have received this line
            print('received bad line from ' + self.name + ': ')
            print(line)
            self.sendLine('what: ' + line)

class GameFactory(Factory):
    def __init__(self,maxPlayers = 2):
        self.users = {}
        self.game = None
        self.turn = None
        self.maxPlayers = maxPlayers

    def buildProtocol(self,addr):
        return Player(self,self.users,self.maxPlayers)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=6814)
    parser.add_argument('-P','--players',type=int,default=2)
    args = parser.parse_args()
    
    reactor.listenTCP(args.port,GameFactory(args.players))
    reactor.run()

if __name__ == '__main__':
    main()
