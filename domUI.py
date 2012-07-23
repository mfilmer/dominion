#!/usr/bin/env python
from __future__ import print_function

import CLI
from errors import *
import Dominion
try:
    import readline
except ImportError:
    pass

class UI(object):
    def __init__(self):
        pass

    #Internal Commands
    def createGame(self,players):
        self._game = Dominion.game(players)
        self.nextTurn()

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
            try:
                count = len(store)
            except OverflowError:
                count = u'\u221E'
            else:
                count = str(count)
            print(str(i+1) + u': (' + count + u') $' + \
                    str(store.getCost()) + u' ' + \
                    store.getName())

    def nextPhase(self):
        if self._turn.isPhase('buy'):
            self._turn.advancePhase()
            self.nextTurn()
        else:
            self._turn.advancePhase()
        if self._turn.isPhase('action'):
            #if self.countCardType('Action') == 0:
            if self._hand.hasCardType('Action'):
                self.newTurnDisplay(False)
            else:
                self.newTurnDisplay(True)
                self.nextPhase()
        elif self._turn.isPhase('buy'):
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

    def getStoreByName(self,name):
        raise Exception('do not use this function')
        for store in self._game.getStores():
            if store.getName() == name:
                return store
        return None

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
    def _stores(self):
        return self._game.getStores()
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
        try:
            name = varList['name']
        except:
            name = varList['name1'] + ' ' + varList['name2']
        try:
            card = self._hand.getCardByName(name)
        except:
            print('Card is not in hand')
        else:
            try:
                self._turn.play(card)
            except InvalidPhase:
                print('This card cannot be played in this phase')
            except InsufficientActions:
                print('Not enough actions to play that card')
            if self._turn.hasRemainingActions():
                if self._hand.hasCardType('Action'):
                    self.actionPhaseDisplay()
                else:
                    self.nextPhase()
            else:
                self.nextPhase()

    def comBuyCard(self,command,varList):
        try:
            name = varList['name']
        except:
            name = varList['name1'] + ' ' + varList['name2']
        try:
            store = self._game.getStoreByName(name)
        except ValueError:
            print('That card does not exist')
        else:
            try:
                self._turn.buy(store)
            except InvalidPhase:
                print('Cannot buy cards during the action phase')
            except InsufficientFunds:
                print('Not enough money')
            except EmptyPile:
                print('Store is sold out')
            except InsufficientBuys:
                print('No remaining buys')
            else:
                if self._turn.hasRemainingBuys():
                    self.buyPhaseDisplay()
                else:
                    self.nextPhase()

    def comListStores(self,command,varList):
        self.buyPhaseDisplay()

    def comCardText(self,command,varList):
        print('card text not available at this time')

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
    cli.addCommand('text %sname',gameUI.comCardText)
    cli.addCommand('text %sname1 %sname2',gameUI.comCardText)
    cli.addCommand('buy %sname',gameUI.comBuyCard)
    cli.addCommand('buy %sname1 %sname2',gameUI.comBuyCard)
    cli.addCommand('play %sname',gameUI.comPlayName)
    cli.addCommand('play %sname1 %sname2',gameUI.comPlayName)

    #Start Game
    #if gameUI.countCardType('Action') == 0:
    if not gameUI._hand.hasCardType('Action'):
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
