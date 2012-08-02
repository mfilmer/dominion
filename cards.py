class phase(object):
    action = 0
    buy = 1
    cleanup = 2
    wait = 3

class Card(object):
    def __init__(self,startPile):
        self._pile = startPile
        self._victoryPoints = 0
        self._cost = 0
        self._playablePhases = [phase.action]
        self._extraPrompts = []
        self._name = '<Unnammed>'
        self._types = ['Action']
        self._fullText = '<Blank>'
        #things the card can do when played
        self._effects = {'money':0,'cards':0,'actions':0,'buys':0}

    def play(self,extraData):
        self.move(self._pile.getOwner().getDeck().getField())
        self._specialActions(extraData)

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

    def getPrompts(self):
        return self._extraPrompts

    def isType(self,type):
        return type in self._types

    def getFullText(self):
        return self._fullText

    def _specialActions(self,extraData):
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

#Gold cards
#todo: figure out how to make gold cards not use up actions
#Cost: 0
class gold1(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Copper'
        self._cost = 0
        self._effects['money'] = 1
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '1$'

#Cost: 3
class gold2(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Silver'
        self._cost = 3
        self._effects['money'] = 2
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '2$'

#Cost 6
class gold3(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Gold'
        self._cost = 6
        self._effects['money'] = 3
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '3$'

#Land (or whatever their real name is) cards
#todo: figure out how ot make victory cards not playable
#Cost: 2
class victory1(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Estate'
        self._cost = 2
        self._victoryPoints = 1
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '1 VP'

#Cost: 5
class victory3(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Duchy'
        self._cost = 5
        self._victoryPoints = 2
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '3 VP'

#Cost: 8
class victory6(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Province'
        self._cost = 8
        self._victoryPoints = 3
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '6 VP'

class curse(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Curse'
        self._cost = 0
        self._victoryPoints = -1
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '-1 VP'

#Cost: 2
#+1 Action
#Discard n cards
#Draw n cards
class cellar(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Cellar'
        self._cost = 2
        self._effects['actions'] = 1
        self._extraPrompts = ['Cards to Discard']
        self._fullText = 'Cost: 2\n+1 Action\nDiscard any number of cards.\n\
        +1 Card per card discarded.'

    def _specialActions(self,extraData):
        discardCards = map(str.strip,extraData[0].split(','))
        tmpPile = pile(self)
        deck = self._pile.getOwner().getDeck()
        hand = deck.getHand()
        discard = deck.getDiscard()
        try:
            for name in discardCards:
                card = hand.getCardByName(name)
                card.move(tmpPile)
        except ValueError:
            while len(tmpPile):
                tmpPile[0].move(hand)
            raise
        cardsToDraw = len(tmpPile)
        while len(tmpPile):
            tmpPile[0].move(discard)
        for i in range(cardsToDraw):
            deck.draw()


#Cost: 2
#Trash up to 4 cards from your hand
class chapel(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Chapel'
        self._cost = 2
        self._extraPrompts = ['Cards to Trash']
        self._fullText = 'Cost: 2\nTrash up to 4 cards from your hand.'

    def _specialActions(self,extraData):
        trashCards = map(str.strip,extraData[0].split(','))
        if len(trashCards) > 4:
            raise ValueError
        tmpPile = pile(self)
        deck = self._pile.getOwner().getDeck()
        hand = deck.getHand()
        trash = self._pile.getOwner().getGame().getTrash()
        try:
            for name in trashCards:
                card = hand.getCardByName(name)
                card.move(tmpPile)
        except ValueError:
            while len(tmpPile):
                tmpPile[0].move(hand)
            raise
        while len(tmpPile):
            tmpPile[0].move(trash)

#Cost: 2
#+2 Cards
#When another player plays an Attack card, you may reveal this from your hand.
#If you do, you are unaffected by that Attack
class moat(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Moat'
        self._cost = 2
        self._playablePhases = [phase.action,phase.wait]
        self._type = ['Action','Reaction']
        self._effects['cards'] = 2
        self._fullText = 'Cost: 2\n+2 Cards\n\
        When another player plays an Attack card, you may reveal this \
        from your hand. If you do, you are unaffected by that Attack.'

        #todo: check the phase and act accordingly

#Cost: 2
#+2
#You may immediately put your deck into your discard pile
class chancellor(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Chancellor'
        self._cost = 2
        self._effects['money'] = 2
        self._extraPrompts = ['Put deck in discard pile [y/n]']
        self._fullText = 'Cost: 3\n+$2\n\
        You may immediately put your deck into your discard pile.'

    def _specialActions(self,extraData):
        response = map(str.strip,extraData[0].split(','))[0].lower()
        if response == 'y' or response == 'yes':
            deck = self._pile.getOwner().getDeck()
            discard = deck.getDiscard()
            library = deck.getLibrary()
            while len(library):
                library[0].move(discard)
        elif response == 'n' or response == 'no':
            pass
        else:
            raise ValueError

#Cost: 3
#+1 Card
#+2 Actions
class village(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Village'
        self._cost = 3
        self._effects['cards'] = 1
        self._effects['actions'] = 2
        self._fullText = 'Cost: 3\n+1 Card\n+2 Actions'

#Cost: 3
#+1 Buy
#+$2
class woodcutter(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Woodcutter'
        self._cost = 3
        self._effects['buys'] = 1
        self._effects['money'] = 2
        self._fullText = 'Cost: 3\n+1 Buy\n+$2'

#Cost: 3
#Gain a card costing up to $4
class workshop(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Workshop'
        self._cost = 3
        self._extraPrompts = ['Card to Gain']
        self._fullText = 'Cost: 3\nGain a card costing up to $4'

    def _specialActions(self,extraData):
        cardsToGain = map(str.strip,extraData[0].split(','))
        if len(cardsToGain) != 1:
            raise ValueError
        cardToGain = cardsToGain[0].lower()
        game = self._pile.getOwner().getGame()
        store = game.getStoreByName(cardToGain)
        if store.getCost() > 4:
            raise ValueError
        player = self._pile.getOwner()
        store.buy(player)

#Cost: 4
#Gain a silver card; put it on top of your deck. Each other player reveals a
#Victory card from his hand and puts it on his deck (or reveals a hand with no
#Victory cards)
class bureaucrat(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Bureaucrat'
        self._cost = 4
        self._types = ['Action','Attack']
        self._fullText = 'Cost: 4\nGain a silver card; put it on top of your \
        deck. Each other player reveals a Victory card from his hand and puts \
        it on his deck (or reveals a hand with no Victory cards).'

#Cost: 4
#Trash this card. Gain a card costing up to $5
class feast(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Feast'
        self._cost = 4
        #self._cost = 0
        self._extraPrompts = ['Card to Gain']
        self._fullText = 'Cost: 4\nTrash this card. Gain a card costing up to \
        $5'

    def _specialActions(self,extraData):
        cardsToGain = map(str.strip,extraData[0].split(','))
        if len(cardsToGain) != 1:
            raise ValueError
        cardToGain = cardsToGain[0].lower()
        player = self._pile.getOwner()
        game = player.getGame()
        store = game.getStoreByName(cardToGain)
        cost = store.getCost()
        if cost > 5:
            raise ValueError
        store.buy(player)
        self.move(game.getTrash())

#Cost: 4
#Worth 1 Victory for every 10 cards in your deck (rounded down)
class gardens(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Gardens'
        self._cost = 4
        self._playablePhases = []
        self._fullText = 'Cost: 4\nWorth 1 VP for every 10 cards in your deck \
        (rounded down)'
    
    @property
    def _victoryPoints(self):
        return len(self.getPile.getPlayer.getDeck)//10

#Cost: 4
#Each other player discards down to 3 cards in his hand.
class militia(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Militia'
        self._cost = 4
        self._effects['money'] = 2
        self._fullText = 'Cost: 4\n+$2\nEach other player discards down to 3 \
                cards in his hand.'

#Cost: 4
#Trash a Copper from your hand. If you do, +$3
class moneylender(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Moneylender'
        self._cost = 4
        self._fullText = 'Cost: 4\nTrash a Copper from your hand. If you do, \
                +$3'

    def _specialActions(self,extraData=[]):
        player = self._pile.getOwner()
        game = player.getGame()
        turn = player.getTurn()
        trash = game.getTrash()
        deck = player.getDeck()
        hand = deck.getHand()
        copper = hand.getCardByName('Copper')
        copper.move(trash)
        turn._addMoney(3)

#Cost: 4
#Trash a card from your hand. Gain a card costing up to $2 more than the trashed
#card
class remodel(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Remodel'
        self._cost = 4
        self._extraPrompts = ['Card to Trash','Card to Gain']
        self._fullText = 'Cost: 4\nTrash a card from your hand. Gain a card \
        costing up to $2 more than the trashed card'

    def _specialActions(self,extraData):
        cardsToTrash = map(str.strip,extraData[0].split(','))
        cardsToGain = map(str.strip,extraData[1].split(','))
        if len(cardsToTrash) != 1:
            raise ValueError
        if len(cardsToGain) != 1:
            raise ValueError
        cardToTrash = cardsToTrash[0].lower()
        cardToGain = cardsToGain[0].lower()
        player = self._pile.getOwner()
        game = player.getGame()
        trash = game.getTrash()
        store = game.getStoreByName(cardToGain)
        deck = player.getDeck()
        hand = deck.getHand()
        trashCard = hand.getCardByName(cardToTrash)
        maxCost = trashCard.getCost() + 2
        if store.getCost() > maxCost:
            raise ValueError
        store.buy(player)
        trashCard.move(trash)

#Cost: 4
#+3 cards
class smithy(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Smithy'
        self._cost = 4
        self._effects['cards'] = 3
        self._fullText = 'Cost: 3\n+3 cards'

#Cost: 4
#+1 card
#+1 action
#Each player (including you) reveals the top card of his deck and either
#discards it or puts it back, your choice
class spy(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Spy'
        self._cost = 4
        self._type = ['Action','Attack']
        self._effects['cards'] = 1
        self._effects['actions'] = 1
        self._fullText = 'Cost: 4\nEach player (including you) reveals the \
        top card of his deck and either discards it or puts it back, your choice'

#Cost: 4
#Each other player reveals the top 2 cards of his deck. If they revealed any
#Treasure cards, they trash one of them that you choose. You may gain any or all
#of these trashed cards. They discard the other revealed cards.
class thief(Card):
    def __init__(self,pile):
        Card.__init__(self)
        self._name = 'Thief'
        self._cost = 4
        self._type = ['Action','Attack']
        self._fullText = 'Cost: 4\n Each other player reveals the top 2 cards \
        of his deck. If they revealed any Treasure cards, they trash one of \
        them that you choose. You may gain any or all of these trashed cards. \
        They discard the other revealed cards.'

#Cost: 4
#Choose an Action card in your hand. Play it twice
class throneRoom(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Throne Room'
        self._cost = 4
        self._fullText = 'Cost: 4\n Choose an Action card in your hand. Play \
                it twice'

#Cost: 5
#+4 Cards
#+1 Buy
#Each other player draws a card
class councilRoom(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Council Room'
        self._cost = 5
        self._effects['cards'] = 4
        self._effects['buys'] = 1
        self._fullText = 'Cost: 5\n+4 cards\n+1 buy\nEach other player draws a \
        card'
        
    def _specialActions(self,extraData=[]):
        owner = self._pile.getOwner()
        players = owner.getGame().getPlayers()
        for player in players:
            if player != owner:
                player.drawCard()

#Cost: 5
#+2 Actions
#+1 Buy
#+$2
class festival(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Festival'
        self._cost = 5
        self._effects['actions'] = 2
        self._effects['buys'] = 1
        self._effects['money'] = 2
        self._fullText = 'Cost: 5\n+2 actions\n+1 buy\n+2$'

#Cost: 5
#+2 Cards
#+1 Action
class laboratory(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Laboratory'
        self._cost = 5
        self._effects['cards'] = 2
        self._effects['actions'] = 1
        self._fullText = 'Cost: 5\n+2 cards\n+1 action'

#Cost: 5
#Draw until you have 7 cards in hand. You may set aside any Action cards drawn
#this way, as you draw them; discard the set aside cards after you finish
#drawing.
class library(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Library'
        self._cost = 5
        self._fullText = 'Cost: 5\nDraw until you have 7 cards in hand. You \
                may set aside any Action cards drawn this way, as you draw \
                them; discard the set aside cards after you finish drawing.'

#Cost: 5
#+1 Card
#+1 Action
#+1 Buy
#+$1
class market(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Market'
        self._cost = 5
        self._effects['money'] = 1
        self._effects['cards'] = 1
        self._effects['actions'] = 1
        self._effects['buys'] = 1
        self._fullText = 'Cost: 5\n+1 card\n+1 action\n+1 buy\n+1$'

#Cost: 5
#Trash a Treasure card from your hand. Gain a Treasure card costing up to $3
#more; put it into your hand.
class mine(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Mine'
        self._cost = 5
        self._extraPrompts = ['Card to Trash']
        self._fullText = 'Cost: 5\nTrash a Treasure card from your hand. Gain \
        a Treasure card costing up to $3 more; put it into your hand.'

    def _specialActions(self,extraData):
        cardsToTrash = map(str.strip,extraData[0].split(','))
        if len(cardsToTrash) != 1:
            raise ValueError
        cardToTrash = cardsToTrash[0].lower()
        player = self._pile.getOwner()
        deck = player.getDeck()
        hand = deck.getHand()
        game = player.getGame()
        if cardToTrash != 'copper' and cardToTrash != 'silver':
            raise ValueError
        if cardToTrash == 'copper':
            targetCardName = 'Silver'
        else:
            targetCardName = 'Gold'
        trashCard = hand.getCardByName(cardToTrash)
        targetStore = game.getStoreByName(targetCardName)
        trashCard.move(game.getTrash())
        targetStore.buy(player)
        card = deck.getDiscard().getCardByName(targetCardName)
        card.move(hand)


#Cost: 5
#+2 Cards
#Each other player gains a Curse card
class witch(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Witch'
        self._cost = 5
        self._type = ['Action','Attack']
        self._effects['cards'] = 2
        self._fullText = 'Cost: 5\n+2 cards\nEach other player gains a Curse \
                card'

    def _specialActions(self,extraData=[]):
        owner = self._pile.getOwner()
        game = owner.getGame()
        store = game.getStoreByName('Curse')
        for player in game.getPlayers():
            if player != owner:
                store.buy(player)

#Cost: 6
#Reveal cards from your deck until you reveal 2 Treasure cards. Put those
#Treasure cards in your hand and discard the other revealed cards
class adventurer(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Adventurer'
        self._cost = 6
        self._fullText = 'Cost: 6\nReveal cards from your deck until you \
                reveal 2 Treasure cards. Put those Treasure cards in your hand \
                and discard the other revealed cards'

    def _specialActions(self,extraData=[]):
        deck = self._pile.getOwner().getDeck()
        library = deck.getLibrary()
        discard = deck.getDiscard()
        hand = deck.getHand()
        tmpPile = pile(self)
        
        while tmpPile.countCardsByType('Treasure') < 2:
            if len(library) == 0:
                deck._refreshLibrary()
            if len(library) > 0:
                library[0].move(tmpPile)
            else:
                break
        
        #move those cards to either hand or discard
        while len(tmpPile):
            card = tmpPile[0]
            if card.isType('Treasure'):
                card.move(hand)
            else:
                card.move(discard)
