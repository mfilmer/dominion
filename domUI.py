#!/usr/bin/env python
from __future__ import print_function

import CLI
from errors import *
import Dominion
import readline

class UI(object):
    def __init__(self):
        pass

    #Internal Commands

    def createGame(self,players):
        self._game = Dominion.game(players)
        self.nextTurn()
        self._stores = self._game.getStores()

    def promptFCN(self):
        name = self._player.getName()
        pid = self._player.getID()
        return str(pid) + ': ' + name + '> '

    def listCards(self,cards):
        for index,(count,name) in \
                enumerate(self.countCards(cards)):
            print(str(index + 1) + ': ' + '(' + str(count) + ') ' + name)

    def listStores(self):
        print('Store Inventory:')
        for i,store in enumerate(self._stores):
            print(str(i+1) + ': (' + str(len(store)) + ') $' + \
                    str(store.getCost()) + ' ' + store.getName())

    def nextPhase(self):
        if self._phase == 1:
            self._turn.advancePhase()
            self.nextTurn()
            print('now entering phase: ' + str(self._phase))
        else:
            self._turn.advancePhase()
        if self._phase == 0:
            if self.countCardType('Action') == 0:
                self.newTurnDisplay(True)
                self.nextPhase()
            else:
                self.newTurnDisplay(False)
        elif self._phase == 1:
            if self._turn.getMoney() == 0:
                self.buyPhaseDisplay(True)
                self.nextPhase()
            else:
                self.buyPhaseDisplay(False)

    def nextTurn(self):
        self._turn = self._game.next()

    def countCards(self,cards):
        counts = []
        names = []
        for card in cards:
            name = card.getName()
            if name in names:
                index = names.index(name)
                counts[index] += 1
            else:
                names.append(name)
                counts.append(1)
        return zip(counts,names)

    def getCardByName(self,name):
        for card in self._hand:
            if card.getName() == name:
                return card
        return None

    def getStoreByName(self,name):
        for store in self._game.getStores():
            if store.getName() == name:
                return store
        return None

    def countCardType(self,type):
        count = 0
        for card in self._hand:
            if card.getType() == type:
                count += 1
        return count

    def newTurnDisplay(self,skip=False):
        print(chr(27) + '[2J')
        print(self._player.getName() + '\'s Turn:')
        self.actionPhaseDisplay(skip)

    def actionPhaseDisplay(self,skip=False):
        self.listCards(self._hand)
        self.displayStash(True)
        print('Action Phase:')
        if skip:
            print('No action cards in hand, skipping action phase')

    def buyPhaseDisplay(self,skip=False):
        if skip:
            print('No money, skipping buy phase')
        else:
            self.listStores()
            self.displayStash()
            print('Buy Phase:')

    def displayStash(self,showActions=False):
        print('Remaining Buys: ' + str(self._turn.getBuys()))
        print('Remaining Money: ' + str(self._turn.getMoney()))
        if showActions:
            print('Remaining Actions: ' + str(self._turn.getActions()))


    @property
    def _phase(self):
        return self._turn.getPhase()
    @property
    def _player(self):
        return self._game.getCurrentPlayer()
    @property
    def _deck(self):
        return self._player.getDeck()
    @property
    def _hand(self):
        return self._deck.getHand()
    @property
    def _discard(self):
        return self._deck.getDiscard()
    @property
    def _field(self):
        return self._deck.getField()
    @property
    def _library(self):
        return self._deck.getLibrary()

    #User (External) Commands
    def comListHand(self,command,varList):
        print('Cards in Hand:')
        self.listCards(self._player.getDeck().getHand())

    def comListDiscard(self,command,varList):
        print('Cards in Discard:')
        self.listCards(self._player.getDeck().getDiscard())

    def comListField(self,command,varList):
        print('Cards on the Field:')
        self.listCards(self._deck.getField())

    def comListDeck(self,command,varList):
        print('Cards in the Deck:')
        cards = self._hand.getCards()[:]
        cards.extend(self._field)
        cards.extend(self._discard)
        cards.extend(self._library)
        self.listCards(cards)

    def comNextPhase(self,command,varList):
        self.nextPhase()

    def comPlayName(self,command,varList):
        card =  self.getCardByName(varList['name'])
        if card is None:
            print('Card is not in hand')
        else:
            self._turn.play(card)
            self.actionPhaseDisplay()

    def comBuyCard(self,command,varList):
        store = self.getStoreByName(varList['name'])
        if store is None:
            print('Cannot buy that card')
        else:
            try:
                self._turn.buy(store)
            except InsufficientFunds:
                print('Not enough money')
            except EmptyPile:
                print('Store is sold out')
            except InsufficientBuys:
                print('No remaining buys')
            finally:
                if self._turn.getBuys() == 0:
                    self.nextPhase()
                else:
                    self.buyPhaseDisplay()

    def comListStores(self,command,varList):
        self.buyPhaseDisplay()

def main():
    cli = CLI.cli()
    gameUI = UI()

    players = []
    newPlayer = raw_input('Player Name: ')
    while newPlayer:
        players.append(newPlayer)
        newPlayer = raw_input('Player Name: ')
    gameUI.createGame(players)
    cli.setPrompt(gameUI.promptFCN)
    cli.addCommand('hand',gameUI.comListHand)
    cli.addCommand('discard',gameUI.comListDiscard)
    cli.addCommand('field',gameUI.comListField)
    cli.addCommand('deck',gameUI.comListDeck)
    cli.addCommand('store',gameUI.comListStores)
    cli.addCommand('stores',gameUI.comListStores)
    cli.addCommand('next',gameUI.comNextPhase)
    cli.addCommand('buy %sname',gameUI.comBuyCard)
    cli.addCommand('play %sname',gameUI.comPlayName)

    #Start Game
    if gameUI.countCardType('Action') == 0:
        gameUI.actionPhaseDisplay(True)
        gameUI.nextPhase()
    else:
        gameUI.actionPhaseDisplay(False)
    cli.run()

    #todo: setup CLI
    #prompt should reflect current player name and ID

    #todo: setup players

if __name__ == '__main__':
    main()
