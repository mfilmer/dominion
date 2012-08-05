import random

#Any pile of cards
class Pile(object):
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

class store(Pile):
    """Stores are special piles that you can only take from and not ever add to.
    They represent the cards that players can purchase. Once purchased, a card
    is (usually) moved from the store to the player's discard pile."""
    def __init__(self,count,newCard,owner):
        Pile.__init__(self,owner)
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

    def addNew(self,newCard=None):
        raise Exception('cards cannot be added to a store')

    def __len__(self):
        if self._inf:
            return float('inf')
        else:
            return len(self._cards)

class deck(Pile):
    def __init__(self,player):
        self._player = player
        self._discard = Pile(player)
        self._hand = Pile(player)
        self._library = Pile(player)
        self._field = Pile(player)
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

