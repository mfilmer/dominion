from __future__ import print_function
#from __future__ import division    #division isnt actually used yet
import random

DEBUG = True

class game(object):
    def __init__(self,numPlayers=2,mode='original'):
        self._players = []
        self._numPlayers = numPlayers
        for i in range(numPlayers):
            self._players.append(player(self))
        self._playerNum = random.randint(0,numPlayers-1)
        self._currentPlayer = self._players[self._playerNum]
        self._trash = trash(self)
        self._stores = []
        self._stores.append(store(10,victory1))

    def getPlayers(self):
        return self._players

    def getCurrentPlayer(self):
        return self._currentPlayer

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
    def __init__(self,game):
        self._deck = deck(self)
        self._game = game
        self._turn = turn(self,turn.wait)
        for i in range(7):
            self._deck.addNew(gold1)
        for i in range(3):
            self._deck.addNew(victory1)

    def playCard(self,card):
        if not card.isPlayable():
            raise Exception('card not currently playable')
        card.play()

    def drawCard(self):
        self._deck.draw()

    def getGame(self):
        return self._game

    def getDeck(self):
        return self._deck

    def getTurn(self):
        return self._turn

    def newTurn(self):
        self._turn = turn(self)
        return self._turn

class turn(object):
    action = 0
    buy = 1
    wait = 2
    def __init__(self,player,startPhase = turn.action):
        self._player = player
        self._phase = startPhase
        self._money = 0
        self._actions = 1
        self._buys = 1

    def buy(self,store):
        if len(store) == 0:
            if DEBUG:
                print('Store has no remaining cards')
            return False
        if self._phase != self.buy:
            if DEBUG:
                print('Cards must be purchased during the buy phase')
            return False
        store[0].move(self._player.getDeck().getLibrary())
        return True

    def getPlayer(self):
        return self._player

    def getPhase(self):
        return self._phase

    def advancePhase(self):
        self._phase += 1
        if self._phase > self.wait:
            raise Exception('Phase advanced past last phase')

    def _addActions(self,numActions):
        self._actions += numActions

    def _addMoney(self,money):
        self._money += money

    def _addBuys(self,buys):
        self._buys += buys

class card(object):
    def __init__(self,pile):
        self._pile = pile
        self._victoryPoints = 0
        self._cost = 0
        self._playablePhases = []
        self._name = 'unnammed card'
        #things the card can do when played
        self._effects = {'money':0,'cards':0,'actions':0,'buys':0}

    #play the card. only does basic card operations
    def play(self):
        player = self._pile.getPlayer()
        for i in range(self._effects['cards']):
            player.drawCard()
        player.getTurn._addActions(self._effects['actions'])
        player.getTurn._addMoney(self._effects['money'])
        player.getTurn._addBuys(self._effects['buys'])
        self._specialActions()

    def move(self,destPile):
        destPile._cards.append(self)
        self._pile._cards.remove(self)

    def getPile(self):
        return self._pile

    def getName(self):
        return self._name

    #todo: finish
    def isPlayable(self):
        if self._pile.getPlayer().getTurn().getPhase() in self._

    def _specialActions(self):
        """Dummy method that should be overridden in child classes who do 
        something other than cause the player to draw cards, gain money, gain 
        extra actions, or gain extra buys."""
        pass

    @property
    def victoryPoints(self):
        return self._victoryPoints

    @property
    def cost(self):
        return self._cost

#Any pile of cards
class pile(object):
    def __init__(self):
        self._cards = []

    def addNew(self,newCard):
        """Add a new card. The card must not have existed before adding it to 
        the pile. If the card already exists somewhere, use card.move() instead"""
        #todo: make sure the newCard is actually a card
        self._cards.append(newCard(self))

    def __len__(self):
        len(self._cards)

    def __getitem__(self,i):
        return self._cards[i]

    def __contains__(self,item):
        return item in self._cards

class store(pile):
    """Stores are special piles that you can only take from and not ever add to.
    They represent the cards that players can purchase. Once purchased, a card 
    is (usually) moved from the store to the player's discard pile."""
    def __init__(self,count,newCard):
        pile.__init__(self)
        for i in range(count):
            self._cards.append(newCard(self))

    def addNew(self,newCard=card):
        raise Exception('cards cannot be added to a store')

class deck(pile):
    def __init__(self,player):
        self._player = player
        self._discard = pile()
        self._hand = pile()
        self._library = pile()

    def draw(self):
        if len(self._library) == 0:
            self._refreshLibrary(self)
        #you can't draw if your out of cards
        if len(self._library) != 0:
            self._library[0].move(self._hand)

    def addNew(self,newCard):
        self._discard.addNew(newCard)

    def getPlayer(self):
        return self._player

    def _refreshLibrary(self):
        if len(self._library) == 0:
            for card in self._discard:
                card.move(self._library)
            self._discard = pile()
            random.shuffle(self._library)

    def getLibrary(self):
        return self._library

    def getHand(self):
        return self._hand

    def getDiscard(self):
        return self._discard

    @property
    def _cards(self):
        return self._discard + self._hand + self._library

class trash(pile):
    def __init__(self,game):
        self._game = game

#Gold cards
#todo: figure out how to make gold cards not use up actions
#Cost: 0
class gold1(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Copper'
        self._cost = 0
        self._effects['money'] = 1

#Cost: 3
class gold2(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Silver'
        self._cost = 0
        self._effects['money'] = 2

#Cost 6
class gold3(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Gold'
        self._cost = 0
        self._effects['money'] = 3

#Land (or whatever their real name is) cards
#todo: figure out how ot make victory cards not playable
#Cost: 2
class victory1(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Estate'
        self._cost = 2
        self._victoryPoints = 1

#Cost: 5
class victory3(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Duchy'
        self._cost = 5
        self._victoryPoints = 2

#Cost: 8
class victory6(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Province'
        self._cost = 8
        self._victoryPoints = 3

#Cost: 2
#+1 Action
#Discard n cards
#Draw n cards
class cellar(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Cellar'
        self._cost = 2

#Cost: 2
#Trash up to 4 cards from your hand
class chapel(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Chapel'
        self._cost = 2

#Cost: 2
#+2 Cards
#When another player plays an Attack card, you may reveal this from your hand.
#If you do, you are unaffected by that Attack
class moat(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Moat'
        self._cost = 2

    #todo: check the phase and act accordingly

#Cost: 2
#+2
#You may immediately put your deck into your discard pile
class chancellor(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Chancellor'
        self._cost = 2

#Cost: 3
#+1 Card
#+2 Actions
class village(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Village'
        self._cost = 3
        self._effects['cards'] = 1
        self._effects['actions'] = 2

#Cost: 3
#+1 Buy
#+$2
class woodcutter(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Woodcutter'
        self._cost = 3
        self._effects['buys'] = 1
        self._effects['gold'] = 2

#Cost: 3
#Gain a card costing up to $4
class workshop(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Workshop'
        self._cost = 3

#Cost: 4
#Gain a silver card; put it on top of your deck. Each other player reveals a
#Victory card from his hand and puts it on his deck (or reveals a hand with no
#Victory cards)
class bureaucrat(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Bureaucrat'
        self._cost = 4

#Cost: 4
#Trash this card. Gain a card costing up to $5
class feast(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Feast'
        self._cost = 4

#Cost: 4
#Worth 1 Victory for every 10 cards in your deck (rounded down)
class gardens(card,pile):
    def __init__(self,pile):
        card.__init__(self)
        self._name = 'Gardens'
        self._cost = 4
    
    @property
    def _victoryPoints(self):
        return len(self.getPile.getPlayer.getDeck)//10

#Cost: 4
#Trash a Copper from your hand. If you do, +$3
class moneylender(card,pile):
    def __init__(self,pile):
        card.__init__(self)
        self._name = 'Moneylender'
        self._cost = 4

#Cost: 4
#Trash a card from your hand. Gain a card costing up to $2 more than the trashed
#card
class remodel(card,pile):
    def __init__(self,pile):
        card.__init__(self)
        self._name = 'Remodel'
        self._cost = 4

#Cost: 4
#+3 cards
class smithy(card,pile):
    def __init__(self,pile):
        card.__init__(self)
        self._name = 'Smithy'
        self._cost = 4

#Cost: 4
#+1 card
#+1 action
#Each player (including you) reveals the top card of his deck and either
#discards it or puts it back, your choice
class spy(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Spy'
        self._cost = 4

#Cost: 4
#Each other player reveals the top 2 cards of his deck. If they revealed any
#Treasure cards, they trash one of them that you choose. You may gain any or all
#of these trashed cards. They discard the other revealed cards.
class thief(card):
    def __init__(self,pile):
        card.__init__(self)
        self._name = 'Thief'
        self._cost = 4

#Cost: 4
#Choose an Action card in your hand. Play it twice
class throneRoom(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Throne Room'
        self._cost = 4

#Cost: 5
#+4 Cards
#+1 Buy
#Each other player draws a card
class councilRoom(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Council Room'
        self._cost = 5

#Cost: 5
#+2 Actions
#+1 Buy
#+$2
class festival(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Festival'
        self._cost = 5

#Cost: 5
#+2 Cards
#+1 Action
class laboratory(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Laboratory'
        self._cost = 5

#Cost: 5
#Draw until you have 7 cards in hand. You may set aside any Action cards drawn
#this way, as you draw them; discard the set aside cards after you finish
#drawing.
class library(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Library'
        self._cost = 5

#Cost: 5
#+1 Card
#+1 Action
#+1 Buy
#+$1
class market(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Market'
        self._cost = 5

#Cost: 5
#Trash a Treasure card from your hand. Gain a Treasure card costing up to $3
#more; put it into your hand.
class mine(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Mine'
        self._cost = 5

#Cost: 5
#+2 Cards
#Each other player gains a Curse card
class witch(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Witch'
        self._cost = 5

#Cost: 6
#Reveal cards from your deck until you reveal 2 Treasure cards. Put those
#Treasure cards in your hand and discard the other revealed cards
class adventurer(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Adventurer'
        self._cost = 6
