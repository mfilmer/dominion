from __future__ import print_function
#from __future__ import division    #division isnt actually used yet
import random

import errors

DEBUG = True

class game(object):
    def __init__(self,playerNames,mode='original'):
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
        self._stores.append(store(10,victory1,self))
        self._stores.append(store(10,victory3,self))
        self._stores.append(store(10,victory6,self))
        self._stores.append(store(10,gold1,self))
        self._stores.append(store(10,gold2,self))
        self._stores.append(store(10,gold3,self))
        self._stores.append(store(10,curse,self))

        #mode specific stores
        if mode == 'original':
            self._stores.append(store(10,village,self))
            self._stores.append(store(10,market,self))
            self._stores.append(store(10,smithy,self))

    def getPlayers(self):
        return self._players

    def getCurrentPlayer(self):
        return self._currentPlayer

    def genPlayerID(self):
        self._lastPlayerID += 1
        return self._lastPlayerID

    def getStores(self):
        return self._stores

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

    def playCard(self,card):
        """Try to play a card. If the card was successfully played playCard()
        returns True, if the card cannot be played, playCard() returns False"""
        if not card.isPlayable():
            return False
        card.play()
        return True

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

    def buy(self,store):
        if len(store) == 0:
            raise EmptyPile
        cost = store.getCost()
        if self._money < cost:
            raise InsufficientFunds
        self._money -= cost
        store.buy(self._player)

    def advancePhase(self):
        if self._phase + 1 > phase.wait:
            raise Exception('Phase advanced past last phase')
        self._phase += 1
        if self._phase == phase.buy:
            treasureList = []
            #todo: verify if doing the double loop is necessary
            for card in self._player.getDeck().getHand():
                if card.getType() == 'Treasure':
                    treasureList.append(card)
            while len(treasureList):
                treasureList.pop().play()
        if self._phase == phase.cleanup:
            self._player.getDeck().cleanup()
            self._phase += 1


    def _addActions(self,numActions):
        self._actions += numActions

    def _addMoney(self,money):
        self._money += money

    def _addBuys(self,buys):
        self._buys += buys

class card(object):
    def __init__(self,startPile):
        self._pile = startPile
        self._victoryPoints = 0
        self._cost = 0
        self._playablePhases = [phase.action]
        self._name = '<Unnammed>'
        self._type = 'Action'
        self._fullText = '<Blank>'
        #things the card can do when played
        self._effects = {'money':0,'cards':0,'actions':0,'buys':0}

    #play the card. only does basic card operations
    def play(self):
        if not self.isPlayable():
            return False
        player = self._pile.getOwner()
        for i in range(self._effects['cards']):
            player.drawCard()
        player.getTurn()._addActions(self._effects['actions'])
        player.getTurn()._addMoney(self._effects['money'])
        player.getTurn()._addBuys(self._effects['buys'])
        self._specialActions()
        self.move(self._pile.getOwner().getDeck().getField())
        return True

    def move(self,destPile):
        self._pile._cards.remove(self)
        destPile._cards.append(self)
        self._pile = destPile

    def getPile(self):
        return self._pile

    def getCost(self):
        return self._cost

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def getFullText(self):
        return self._fullText

    def isPlayable(self):
        #check that the card is owned by a player
        try:
            player = self._pile.getOwner()
        except:
            if DEBUG:
                print('unplayable because card not owned by player')
            return False
        #check that the card is in a player's hand
        if self._pile != player.getDeck().getHand():
            if DEBUG:
                print('unplayable because card not in a player\'s hand')
            return False
        #check that the card is playable during this phase
        if not player.getTurn().getPhase() in self._playablePhases:
            if DEBUG:
                print('unplayable due to phase')
            return False
        #check that the player has at least 1 remaining action
        if player.getTurn().getActions() > 0:
            return True
        else:
            if DEBUG:
                print('unplayable due to action count')
            return False

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

    def __len__(self):
        return len(self._cards)

    def __getitem__(self,i):
        return self._cards[i]

    def __setitem__(self,i,value):
        self._cards[i] = value

    def __contains__(self,item):
        return item in self._cards

class store(pile):
    """Stores are special piles that you can only take from and not ever add to.
    They represent the cards that players can purchase. Once purchased, a card
    is (usually) moved from the store to the player's discard pile."""
    def __init__(self,count,newCard,owner):
        pile.__init__(self,owner)
        for i in range(count):
            self._cards.append(newCard(self))
        self._cost = self._cards[0].getCost()
        self._name = self._cards[0].getName()

    def buy(self,player):
        self._cards[0].move(player.getDeck().getDiscard())

    def getCost(self):
        return self._cost

    def getName(self):
        return self._name

    def addNew(self,newCard=card):
        raise Exception('cards cannot be added to a store')

class deck(pile):
    def __init__(self,player):
        self._player = player
        self._discard = pile(player)
        self._hand = pile(player)
        self._library = pile(player)
        self._field = pile(player)
        self._owner = player

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

#Gold cards
#todo: figure out how to make gold cards not use up actions
#Cost: 0
class gold1(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Copper'
        self._cost = 0
        self._effects['money'] = 1
        self._playablePhases = [phase.buy]
        self._type = 'Treasure'

#Cost: 3
class gold2(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Silver'
        self._cost = 0
        self._effects['money'] = 2
        self._playablePhases = [phase.buy]
        self._type = 'Treasure'

#Cost 6
class gold3(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Gold'
        self._cost = 0
        self._effects['money'] = 3
        self._playablePhases = [phase.buy]
        self._type = 'Treasure'

#Land (or whatever their real name is) cards
#todo: figure out how ot make victory cards not playable
#Cost: 2
class victory1(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Estate'
        self._cost = 2
        self._victoryPoints = 1
        self._playablePhases = []
        self._type = 'Victory'

#Cost: 5
class victory3(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Duchy'
        self._cost = 5
        self._victoryPoints = 2
        self._playablePhases = []
        self._type = 'Victory'

#Cost: 8
class victory6(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Province'
        self._cost = 8
        self._victoryPoints = 3
        self._playablePhases = []
        self._type = 'Victory'

class curse(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Curse'
        self._cost = 0
        self._victoryPoints = -1
        self._playablePhases = []
        self._type = 'Victory'

#Cost: 2
#+1 Action
#Discard n cards
#Draw n cards
class cellar(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Cellar'
        self._cost = 2
        self._fullText = 'Cost: 2\n+1 Action\nDiscard any number of cards.\n\
                +1 Card per card discarded.'

#Cost: 2
#Trash up to 4 cards from your hand
class chapel(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Chapel'
        self._cost = 2
        self._fullText = 'Cost: 2\nTrash up to 4 cards from your hand.'

#Cost: 2
#+2 Cards
#When another player plays an Attack card, you may reveal this from your hand.
#If you do, you are unaffected by that Attack
class moat(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Moat'
        self._cost = 2
        self._playablePhases = [phase.action,phase.wait]
        self._type = 'Reaction'
        self._fullText = 'Cost: 2\n+2 Cards\n\
                When another player plays an Attack card, you may reveal this \
                from your hand. If you do, you are unaffected by that Attack.'

    #todo: check the phase and act accordingly

#Cost: 2
#+2
#You may immediately put your deck into your discard pile
class chancellor(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Chancellor'
        self._cost = 2
        self._fullText = 'Cost: 3\n+$2\n\
                You may immediately put your deck into your discard pile.'

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
        self._fullText = 'Cost: 3\n+1 Card\n+2 Actions'

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
        self._fullText = 'Cost: 3\n+1 Buy\n+$2'

#Cost: 3
#Gain a card costing up to $4
class workshop(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Workshop'
        self._cost = 3
        self._fullText = 'Cost: 3\nGain a card costing up to $4'

#Cost: 4
#Gain a silver card; put it on top of your deck. Each other player reveals a
#Victory card from his hand and puts it on his deck (or reveals a hand with no
#Victory cards)
class bureaucrat(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Bureaucrat'
        self._cost = 4
        self._fullText = 'Cost: 4\nGain a silver card; put it on top of your \
        deck. Each other player reveals a Victory card from his hand and puts \
        it on his deck (or reveals a hand with no Victory cards).'

#Cost: 4
#Trash this card. Gain a card costing up to $5
class feast(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Feast'
        self._cost = 4
        self._fullText = 'Cost: 4\nTrash this card. Gain a card costing up to \
        $5'

#Cost: 4
#Worth 1 Victory for every 10 cards in your deck (rounded down)
class gardens(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Gardens'
        self._cost = 4
        self._playablePhases = []
    
    @property
    def _victoryPoints(self):
        return len(self.getPile.getPlayer.getDeck)//10

#Cost: 4
#Trash a Copper from your hand. If you do, +$3
class moneylender(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Moneylender'
        self._cost = 4

#Cost: 4
#Trash a card from your hand. Gain a card costing up to $2 more than the trashed
#card
class remodel(card):
    def __init__(self,pile):
        card.__init__(self,pile)
        self._name = 'Remodel'
        self._cost = 4

#Cost: 4
#+3 cards
class smithy(card):
    def __init__(self,pile):
        card.__init__(self,pile)
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
