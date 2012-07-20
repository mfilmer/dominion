#this just seems to contain a bunch of classes describing the game state
#yeah... that seems good


class game(object):
    def __init__(self,numPlayers=2):
        #create the initial starting piles of cards. 
        pass

#Any pile of cards
class pile(object):
    pass

class deck(pile):
    pass

class discard(pile):
    pass

class trash(pile):
    pass

class card(object):
    def __init__(self,deck):
        self._victoryPoints = 0
        self._cost = 0

    def activate(self):
        pass

    @property
    def victoryPoints(self):
        return self._victoryPoints

    @property
    def cost(self):
        return self._cost

#Gold cards
#Cost: 0
class gold1(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0
    

#Cost: 3
class gold2(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost 6
class gold3(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Land (or whatever their real name is) cards
#Cost: 2
class victory1(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
class victory3(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 8
class victory6(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 2
#+1 Action
#Discard n cards
#Draw n cards
class cellar(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 2
#Trash up to 4 cards from your hand
class chapel(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 2
#+2 Cards
#When another player plays an Attack card, you may reveal this from your hand.
#If you do, you are unaffected by that Attack
class moat(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 2
#+2
#You may immediately put your deck into your discard pile
class chancellor(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 3
#+1 Card
#+2 Actions
class village(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 3
#+1 Buy
#+$2
class woodcutter(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 3
#Gain a card costing up to $4
class workshop(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Gain a silver card; put it on top of your deck. Each other player reveals a
#Victory card from his hand and puts it on his deck (or reveals a hand with no
#Victory cards)
class bureaucrat(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Trash this card. Gain a card costing up to $5
class feast(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Worth 1 Victory for every 10 cards in your deck (rounded down)
class gardens(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Trash a Copper from your hand. If you do, +$3
class moneylender(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Trash a card from your hand. Gain a card costing up to $2 more than the trashed
#card
class remodel(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#+3 cards
class smithy(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#+1 card
#+1 action
#Each player (including you) reveals the top card of his deck and either
#discards it or puts it back, your choice
class spy(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Each other player reveals the top 2 cards of his deck. If they revealed any
#Treasure cards, they trash one of them that you choose. You may gain any or all
#of these trashed cards. They discard the other revealed cards.
class thief(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 4
#Choose an Action card in your hand. Play it twice
class throneRoom(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#+4 Cards
#+1 Buy
#Each other player draws a card
class councilRoom(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#+2 Actions
#+1 Buy
#+$2
class festival(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#+2 Cards
#+1 Action
class laboratory(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#Draw until you have 7 cards in hand. You may set aside any Action cards drawn
#this way, as you draw them; discard the set aside cards after you finish
#drawing.
class library(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#+1 Card
#+1 Action
#+1 Buy
#+$1
class market(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#Trash a Treasure card from your hand. Gain a Treasure card costing up to $3
#more; put it into your hand.
class mine(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 5
#+2 Cards
#Each other player gains a Curse card
class witch(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0

#Cost: 6
#Reveal cards from your deck until you reveal 2 Treasure cards. Put those
#Treasure cards in your hand and discard the other revealed cards
class adventurer(card):
    def __init__(self):
        card.__init__(self)
        self._cost = 0
