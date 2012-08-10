from __future__ import print_function
#from __future__ import division    #division isnt actually used yet
import random

from errors import *
#from cards import *    #pretty sure we don't need this import
from cardList import *
from piles import *

DEBUG = False

class game(object):
    def __init__(self,playerNames,onlyWorking=True,expansions=['Base'],\
            useChance=False):
        self._players = []
        self._numPlayers = len(playerNames)
        self._lastPlayerID = 0
        for i in range(self._numPlayers):
            self._players.append(player(self,playerNames[i]))
        self._playerNum = random.randint(0,self._numPlayers-1)
        self._currentPlayer = self._players[self._playerNum]
        self._trash = Pile(self)

        #create initial stores
        cardList = CardList()

        potentialStores = set()
        for exp in expansions:
            potentialStores.update(cardList.getCardsInExpansion(exp))
        if onlyWorking:
            potentialStores.intersection_update(cardList.getWorkingCards())
        potentialStores = list(potentialStores)
        potentialStores = set(random.sample(potentialStores,10))
        potentialStores.update(cardList.getCardsInStoreSet('Always'))
        if useChance:
            potentialStores.update(cardList.getCardsInStoreSet('Chance'))
        self._stores = [store(x(self).getInitInv(),x,self) for x in \
                potentialStores]

    def getPlayers(self):
        return self._players

    def getStoreByName(self,name):
        for store in self._stores:
            if store.getName().lower() == name.lower():
                return store
        raise ValueError

    def getCurrentPlayer(self):
        return self._currentPlayer

    def genPlayerID(self):
        self._lastPlayerID += 1
        return self._lastPlayerID

    def getStores(self):
        return self._stores

    def getTrash(self):
        return self._trash

    #todo: implement
    def _isGameOver(self):
        count = 0
        for store in self._stores:
            if store.__len__() == 0:
                if store.getName() == 'Province':
                    return True
                count += 1
        if count >= 3:
            return True
        return False

    #iterate over each turn stopping when the game is over
    def next(self):
        if self._isGameOver():
            raise StopIteration
        self._playerNum = (self._playerNum + 1) % self._numPlayers
        self._currentPlayer = self._players[self._playerNum]
        return self._currentPlayer.newTurn()

    def __iter__(self):
        return self

class player(object):
    def __init__(self,game,name):
        self._name = name
        self._ID = game.genPlayerID()
        self._deck = deck(self)
        self._game = game
        self._turn = turn(self,phase.wait)
        for i in range(7):
            self._deck.addNew(gold1)
        for i in range(3):
            self._deck.addNew(victory1)
        self._deck.cleanup()

    def drawCard(self):
        self._deck.draw()

    def getGame(self):
        return self._game

    def getDeck(self):
        return self._deck

    def getTurn(self):
        return self._turn

    def getName(self):
        return self._name

    def getID(self):
        return self._ID

    def newTurn(self):
        self._turn = turn(self)
        return self._turn

class phase(object):
    action = 0
    buy = 1
    cleanup = 2
    wait = 3

class turn(object):
    def __init__(self,player,startPhase = phase.action):
        self._player = player
        self._phase = startPhase
        self._money = 0
        self._actions = 1
        self._buys = 1

    def getPlayer(self):
        return self._player

    def getPhase(self):
        return self._phase

    def getActions(self):
        return self._actions

    def getBuys(self):
        return self._buys

    def getMoney(self):
        return self._money

    def hasRemainingActions(self):
        return self._actions > 0

    def hasRemainingBuys(self):
        return self._buys > 0

    def hasRemainingMoney(self):
        return self._money > 0

    def isPhase(self,phase):
        if phase.lower() == 'action':
            return self._phase == 0
        elif phase.lower() == 'buy':
            return self._phase == 1
        elif phase.lower() == 'cleanup':
            return self._phase == 2
        elif phase.lower() == 'wait':
            return self._phase == 3
        else:
            raise ValueError(phase + ' is not a valid phase')

    def play(self,card,extraData):
        if self.isPhase('action'):
            if self._actions < 1:
                raise InsufficientActions
            if not card.isType('Action'):
                raise InvalidPhase
        if self.isPhase('buy'):
            if not card.isType('Treasure'):
                raise InvalidPhase
        player = self.getPlayer()
        try:
            card.play(extraData)
        except ValueError:
            card.move(self._player.getDeck().getHand())
            raise
        else:
            for i in range(card._effects['cards']):
                player.drawCard()
            self._addActions(card._effects['actions'])
            self._addMoney(card._effects['money'])
            self._addBuys(card._effects['buys'])
            if self.isPhase('action'):
                self._actions -= 1

    def buy(self,store):
        if self.isPhase('action'):
            raise InvalidPhase
        if self._buys == 0:
            raise InsufficientBuys
        cost = store.getCost()
        if self._money < cost:
            raise InsufficientFunds
        store.buy(self._player)
        self._money -= cost
        self._buys -= 1

    def advancePhase(self):
        if self._phase + 1 > phase.wait:
            raise PhaseError('Phase advanced past last phase')
        self._phase += 1
        if self.isPhase('buy'):
            treasureList = []
            #todo: verify if doing the double loop is necessary
            for card in self._player.getDeck().getHand():
                if card.isType('Treasure'):
                    treasureList.append(card)
            while len(treasureList):
                self.play(treasureList.pop(),[])
        if self.isPhase('cleanup'):
            self._player.getDeck().cleanup()
            self._phase += 1
            self._money = 0
            self._actions = 0
            self._buys = 0

    def _addActions(self,numActions):
        self._actions += numActions

    def _addMoney(self,money):
        self._money += money

    def _addBuys(self,buys):
        self._buys += buys

