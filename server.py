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
        self.phase = 'New'

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
            self.phase = 'InLobby'
            self.users[name] = self
            for name,protocol in self.users.iteritems():
                if protocol == self:
                    pass
                    for name,protocol in self.users.iteritems():
                        self.sendLine('existingPlayer: ' + name)
                else:
                    protocol.sendLine('newPlayer: ' + self.name)
            if len(self.users) == self.maxPlayers:
                self.factory.startGame()

    def lineReceived(self,line):
        if self.phase == 'New': #they sent their name. tell everyone about it
            self.registerNewPlayer(line)
        elif self.phase == 'InLobby':
            #perhaps this is a chat message. implement later
            self.unrecognizedClientRequest(line) 
        elif self.phase == 'Action':
            if line[0:6] == 'play: ':
                print(self.name+' has played: ' + line[6:])
            else:
                self.unrecognizedClientRequest(line)
        else:
            self.unrecognizedClientRequest(line)

    def unrecognizedClientRequest(self,line):
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

    def startGame(self):
        print('Starting Game...')
        self.game = Dominion.game(self.users.keys())
        self.turn = self.game.next()
        players = self.game.getPlayers()
        stores = self.game.getStores()
        dStores = {}
        for store in stores:
            try:
                dStores[store.getName()]=(store.getCost(),len(store))
            except OverflowError:
                dStores[store.getName()]=(store.getCost(),u'\u221E')
        stores = repr(dStores)
        currentPlayerName = self.turn.getPlayer().getName()
        print('starting player: ' + currentPlayerName)
        for name,protocol in self.users.iteritems():
            protocol.sendLine('starting')
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
                protocol.phase = 'Action'
            else:
                protocol.sendLine('turn: ' + currentPlayerName)
                protocol.phase = 'Waiting'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=6814)
    parser.add_argument('-P','--players',type=int,default=2)
    args = parser.parse_args()
    
    reactor.listenTCP(args.port,GameFactory(args.players))
    reactor.run()

if __name__ == '__main__':
    main()
