#!/usr/bin/env python
from __future__ import print_function

import CLI
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
        for i,store in enumerate(self._stores):
            print(str(i+1) + ': (' + str(len(store)) + ') $' + \
                    str(store.getCost()) + ' ' + store.getName())

    def nextPhase(self):
        self._turn.advancePhase()
        self._phase = self._turn.getPhase()
        if self._phase == 0:
            if self.countCardType('Action') == 0:
                self.actionPhaseDisplay(True)
                self.nextPhase()
            else:
                self.actionPhaseDisplay(False)
        elif self._phase == 1:
            if self._turn.getMoney() == 0:
                self.buyPhaseDisplay(True)
                self.nextPhase()
            else:
                self.buyPhaseDisplay(False)
        elif self._phase == 3:
            self.nextTurn()
            self._phase = self._turn.getPhase()

    def nextTurn(self):
        self._turn = self._game.next()
        self._phase = self._turn.getPhase()
        self._player = self._turn.getPlayer()
        self._deck = self._player.getDeck()
        self._hand = self._deck.getHand()

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

    def getCardIndex(self,name):
        for i,card in enumerate(self._hand):
            if card.getName() == name:
                return i
        return None

    def countCardType(self,type):
        count = 0
        for card in self._hand:
            if card.getType == type:
                count += 1
        return count

    def actionPhaseDisplay(self,skip):
        print(chr(27) + '[2J')
        print(self._player.getName() + '\'s Turn:')
        self.listCards(self._hand)
        if skip:
            print('No action cards in hand, skipping action phase')
            self.nextPhase()
        else:
            print('Action Phase:')

    def buyPhaseDisplay(self,skip):
        if skip:
            print('No money, skipping buy phase')
        else:
            print('Buy Phase:')
            self.listStores()
            print('Remaining Money: ' + str(self._turn.getMoney()))

    #User (External) Commands
    def comListHand(self,command,varList):
        print('Cards in Hand:')
        self.listCards(self._player.getDeck().getHand())

    def comListDiscard(self,command,varList):
        print('Cards in Discard:')
        self.listCards(self._player.getDeck().getDiscard())

    def comNextPhase(self,command,varList):
        self.nextPhase()

    def comPlayName(self,command,varList):
        index =  self.getCardIndex(varList['name'])
        if index is None:
            print('Card is not in hand')
        else:
            self._hand[index].play()

    #todo: finish
    def comBuyCard(self,command,varList):
        pass

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
    cli.addCommand('next',gameUI.comNextPhase)
    cli.addCommand('buy %sname',gameUI.comBuyCard)
    cli.addCommand('play %sname',gameUI.comPlayName)

    #Start Game
    gameUI.actionPhaseDisplay(False)
    cli.run()

    #todo: setup CLI
    #prompt should reflect current player name and ID

    #todo: setup players

if __name__ == '__main__':
    main()
