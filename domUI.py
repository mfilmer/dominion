#!/usr/bin/env python
from __future__ import print_function

import CLI
import Dominion

class UI(object):
    def __init__(self):
        pass

    #Internal Commands

    def createGame(self,players):
        self._game = Dominion.game(players)

    def promptFCN(self):
        player = self._game.getCurrentPlayer()
        name = player.getName()
        pid = player.getID()
        self.listCards(player)
        return str(pid) + ': ' + name + '> '

    def listCards(self,player):
        for index,(count,name) in \
                enumerate(self.countCards(player.getDeck().getHand())):
            print(str(index + 1) + ': ' + '(' + str(count) + ') ' + name)

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

    #User (External) Commands
    def comListCards(command,varList):
        player = self._game.getCurrentPlayer()
        self.listCards(player)

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
    cli.addCommand('cards',gameUI.comListCards)

    cli.run()

    #todo: setup CLI
    #prompt should reflect current player name and ID

    #todo: setup players

if __name__ == '__main__':
    main()
