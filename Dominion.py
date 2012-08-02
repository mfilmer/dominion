from __future__ import print_function
#from __future__ import division    #division isnt actually used yet
import random

from errors import *
from cards import *

DEBUG = False

class game(object):
    def __init__(self,playerNames,mode='all'):
        self._players = []
        self._numPlayers = len(playerNames)
        self._lastPlayerID = 0
        for i in range(self._numPlayers):
            self._players.append(player(self,playerNames[i]))
        self._playerNum = random.randint(0,self._numPlayers-1)
        self._currentPlayer = self._players[self._playerNum]
        self._trash = pile(self)
        #create initial stores
        self._stores = []
        self._stores.append(store('inf',gold1,self))
        self._stores.append(store('inf',gold2,self))
        self._stores.append(store('inf',gold3,self))
        self._stores.append(store(8,victory1,self))
        self._stores.append(store(8,victory3,self))
        self._stores.append(store(8,victory6,self))
        self._stores.append(store('inf',curse,self))

        #mode specific stores
        if mode == 'all':
            self._stores.append(store(10,village,self))
            self._stores.append(store(10,market,self))
            self._stores.append(store(10,smithy,self))
            self._stores.append(store(10,cellar,self))
            self._stores.append(store(10,moat,self))
            self._stores.append(store(10,militia,self))
            self._stores.append(store(10,woodcutter,self))
            self._stores.append(store(10,workshop,self))
            self._stores.append(store(10,remodel,self))
            self._stores.append(store(10,mine,self))
            self._stores.append(store('inf',councilRoom,self))
            self._stores.append(store('inf',adventurer,self))
            self._stores.append(store('inf',chapel,self))
            self._stores.append(store('inf',chancellor,self))
            self._stores.append(store('inf',moneylender,self))
            self._stores.append(store('inf',feast,self))
            self._stores.append(store('inf',witch,self))

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
        pass

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

#Any pile of cards
class pile(object):
    def __init__(self,owner):
        self._cards = []
        self._owner = owner

    def addNew(self,newCard):
        """Add a new card. The card must not have existed before adding it to
        the pile. If the card already exists somewhere, use card.move()
        instead"""
        #todo: make sure the newCard is actually a card
        self._cards.append(newCard(self))

    def getOwner(self):
        return self._owner

    def getCards(self):
        return self._cards

    def getCardByName(self,name):
        for card in self:
            if card.getName().lower() == name.lower():
                return card
        raise ValueError

    def hasCardType(self,type):
        for card in self:
            if card.isType(type):
                return True
        return False

    def hasCardName(self,name):
        for card in self:
            if card.getName() == name:
                return True
        return False

    def countCardsByType(self,type):
        count = 0
        for card in self:
            if card.isType(type):
                count += 1
        return count

    def countCardsByName(self,name):
        count = 0
        for card in self:
            if card.getName().lower() == name.lower():
                count += 1
        return count

    def __len__(self):
        return len(self._cards)

    def __getitem__(self,i):
        return self._cards[i]

    def __setitem__(self,i,value):
        self._cards[i] = value

    def __contains__(self,name):
        for card in self:
            if card.getName().lower() == name.lower():
                return True
        return False

class store(pile):
    """Stores are special piles that you can only take from and not ever add to.
    They represent the cards that players can purchase. Once purchased, a card
    is (usually) moved from the store to the player's discard pile."""
    def __init__(self,count,newCard,owner):
        pile.__init__(self,owner)
        self._inf = False
        self._newCard = newCard
        if float(count) == float('inf'):
            self._inf = True
            self._cards.append(newCard(self))
        else:
            for i in range(count):
                self._cards.append(newCard(self))
        self._cost = self._cards[0].getCost()
        self._name = self._cards[0].getName()

    def buy(self,player):
        if not self._inf:
            if len(self) == 0:
                raise EmptyPile
        self._cards[0].move(player.getDeck().getDiscard())
        if self._inf:
            self._cards.append(self._newCard(self))

    def getCost(self):
        return self._cost

    def getName(self):
        return self._name

    def addNew(self,newCard=Card):
        raise Exception('cards cannot be added to a store')

    def __len__(self):
        if self._inf:
            return float('inf')
        else:
            return len(self._cards)

class deck(pile):
    def __init__(self,player):
        self._player = player
        self._discard = pile(player)
        self._hand = pile(player)
        self._library = pile(player)
        self._field = pile(player)
        self._owner = player
        self._extraPrompts = []

    def draw(self):
        if len(self._library) == 0:
            self._refreshLibrary()
        #you can't draw if your out of cards
        if len(self._library) != 0:
            self._library[0].move(self._hand)

    def addNew(self,newCard):
        self._discard.addNew(newCard)

    def getPlayer(self):
        return self._player

    def cleanup(self):
        while len(self._hand):
            self._hand[0].move(self._discard)
        while len(self._field):
            self._field[0].move(self._discard)
        for i in range(5):
            self.draw()

    def _refreshLibrary(self):
        if len(self._library) == 0:
            while len(self._discard):
                self._discard[0].move(self._library)
            random.shuffle(self._library)

    def getLibrary(self):
        return self._library

    def getHand(self):
        return self._hand

    def getDiscard(self):
        return self._discard

    def getField(self):
        return self._field

    def __len__(self):
        return len(self._hand) + len(self._library) + len(self._discard) + \
                len(self._field)

    @property
    def _cards(self):
        return self._hand

