class phase(object):
    action = 0
    buy = 1
    cleanup = 2
    wait = 3

class Card(object):
    def __init__(self,startPile):
        self._pile = startPile
        self._inventory = 10
        self._expansion = 'Base' #money, starting kingdoms = ''
        self._storeSets = [] #money, kingdoms = 'Always'; Col, Plat = 'Chance'
        self._victoryPoints = 0
        self._cost = 0
        self._playablePhases = [phase.action]
        self._extraPrompts = []
        self._name = '<Unnammed>'
        self._types = ['Action']
        self._isWorking = True
        self._fullText = '<Blank>'
        self._expansion = 'Base'
        #things the card can do when played
        self._effects = {'money':0,'cards':0,'actions':0,'buys':0}

    def play(self,extraData):
        self.move(self._pile.getOwner().getDeck().getField())
        self._specialActions(extraData)

    def move(self,destPile):
        self._pile._cards.remove(self)
        destPile._cards.append(self)
        self._pile = destPile

    def isWorking(self):
        return self._isWorking

    def inSet(self,setName):
        return setName in self._storeSets

    def getInitInv(self):
        return self._inventory

    def getExpansion(self):
        return self._expansion

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

#Base Treasure
#todo: figure out how to make gold cards not use up actions
class gold1(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 40
        self._name = 'Copper'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 0
        self._effects['money'] = 1
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '1$'

class gold2(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 30
        self._name = 'Silver'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 3
        self._effects['money'] = 2
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '2$'

class gold3(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 30
        self._name = 'Gold'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 6
        self._effects['money'] = 3
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '3$'
        
class gold5(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 12 
        self._name = 'Platinum'
        self._expansion = ''
        self._storeSets = ['Chance']
        self._cost = 9
        self._effects['money'] = 5
        self._playablePhases = [phase.buy]
        self._types = ['Treasure']
        self._fullText = '5$'        

#Kingdom cards
#todo: figure out how ot make victory cards not playable
class victory1(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 8 #depends on number of players
        self._name = 'Estate'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 2
        self._victoryPoints = 1
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '1 VP'

class victory3(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 8 #depends on number of players
        self._name = 'Duchy'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 5
        self._victoryPoints = 2
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '3 VP'

class victory6(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 8 #depends on number of players
        self._name = 'Province'
        self._expansion = ''
        self._storeSets = ['Always']
        self._cost = 8
        self._victoryPoints = 3
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '6 VP'
        
class victory10(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 8 #depends on number of players
        self._name = 'Colony'
        self._expansion = ''
        self._storeSets = ['Chance']
        self._cost = 11
        self._victoryPoints = 10
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '10 VP'

class curse(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 10 #depends on number of players
        self._name = 'Curse'
        self._cost = 0
        self._victoryPoints = -1
        self._playablePhases = []
        self._types = ['Victory']
        self._fullText = '-1 VP'

### Base Set
class cellar(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Cellar'
        self._cost = 2
        self._storeSets = ['First']
        self._isWorking = False
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

class chapel(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Chapel'
        self._cost = 2
        self._isWorking = False
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

class moat(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Moat'
        self._storeSets = ['First']
        self._isWorking = False
        self._cost = 2
        self._playablePhases = [phase.action,phase.wait]
        self._type = ['Action','Reaction']
        self._effects['cards'] = 2
        self._fullText = 'Cost: 2\n+2 Cards\n\
        When another player plays an Attack card, you may reveal this \
        from your hand. If you do, you are unaffected by that Attack.'

        #todo: check the phase and act accordingly

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

class village(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Village'
        self._storeSets = ['First']
        self._cost = 3
        self._effects['cards'] = 1
        self._effects['actions'] = 2
        self._fullText = 'Cost: 3\n+1 Card\n+2 Actions'

class woodcutter(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Woodcutter'
        self._storeSets = ['First']
        self._cost = 3
        self._effects['buys'] = 1
        self._effects['money'] = 2
        self._fullText = 'Cost: 3\n+1 Buy\n+$2'

class workshop(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Workshop'
        self._storeSets = ['First']
        self._isWorking = False
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

class bureaucrat(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Bureaucrat'
        self._isWorking = False
        self._cost = 4
        self._types = ['Action','Attack']
        self._fullText = 'Cost: 4\nGain a silver card; put it on top of your \
        deck. Each other player reveals a Victory card from his hand and puts \
        it on his deck (or reveals a hand with no Victory cards).'

class feast(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Feast'
        self._cost = 4
        self._isWorking = False
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

class gardens(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._inventory = 8 #depends on number of players
        self._name = 'Gardens'
        self._cost = 4
        self._playablePhases = []
        self._fullText = 'Cost: 4\nWorth 1 VP for every 10 cards in your deck \
        (rounded down)'
    
    @property
    def _victoryPoints(self):
        return len(self.getPile.getPlayer.getDeck)//10
    @_victoryPoints.setter
    def _victoryPoints(self,value):
        pass

class militia(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Militia'
        self._storeSets = ['First']
        self._isWorking = False
        self._cost = 4
        self._effects['money'] = 2
        self._fullText = 'Cost: 4\n+$2\nEach other player discards down to 3 \
                cards in his hand.'

class moneylender(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Moneylender'
        self._cost = 4
        self._isWorking = False
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

class remodel(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Remodel'
        self._storeSets = ['First']
        self._isWorking = False
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

class smithy(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Smithy'
        self._storeSets = ['First']
        self._cost = 4
        self._effects['cards'] = 3
        self._fullText = 'Cost: 3\n+3 cards'

class spy(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Spy'
        self._isWorking = False
        self._cost = 4
        self._type = ['Action','Attack']
        self._effects['cards'] = 1
        self._effects['actions'] = 1
        self._fullText = 'Cost: 4\nEach player (including you) reveals the \
        top card of his deck and either discards it or puts it back, your choice'

class thief(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Thief'
        self._isWorking = False
        self._cost = 4
        self._type = ['Action','Attack']
        self._fullText = 'Cost: 4\n Each other player reveals the top 2 cards \
        of his deck. If they revealed any Treasure cards, they trash one of \
        them that you choose. You may gain any or all of these trashed cards. \
        They discard the other revealed cards.'

class throneRoom(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Throne Room'
        self._isWorking = False
        self._cost = 4
        self._fullText = 'Cost: 4\n Choose an Action card in your hand. Play \
                it twice'

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

class festival(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Festival'
        self._cost = 5
        self._effects['actions'] = 2
        self._effects['buys'] = 1
        self._effects['money'] = 2
        self._fullText = 'Cost: 5\n+2 actions\n+1 buy\n+2$'

class laboratory(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Laboratory'
        self._cost = 5
        self._effects['cards'] = 2
        self._effects['actions'] = 1
        self._fullText = 'Cost: 5\n+2 cards\n+1 action'

class library(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Library'
        self._isWorking = False
        self._cost = 5
        self._fullText = 'Cost: 5\nDraw until you have 7 cards in hand. You \
                may set aside any Action cards drawn this way, as you draw \
                them; discard the set aside cards after you finish drawing.'

class market(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Market'
        self._storeSets = ['First']
        self._cost = 5
        self._effects['money'] = 1
        self._effects['cards'] = 1
        self._effects['actions'] = 1
        self._effects['buys'] = 1
        self._fullText = 'Cost: 5\n+1 card\n+1 action\n+1 buy\n+1$'

class mine(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Mine'
        self._isWorking = False
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
        if cardToTrash != 'copper' and cardToTrash != 'silver' and cardToTrash != 'gold':
            raise ValueError
        if cardToTrash == 'copper':
            targetCardName = 'Silver'
        if cardToTrash == 'silver':
            targetCardName = 'Gold'
        else:
            targetCardName = 'Platinum'
        trashCard = hand.getCardByName(cardToTrash)
        targetStore = game.getStoreByName(targetCardName)
        trashCard.move(game.getTrash())
        targetStore.buy(player)
        card = deck.getDiscard().getCardByName(targetCardName)
        card.move(hand)


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
### Intrigue
class courtyard(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Courtyard'
        self._isWorking = False
        self._cost = 2
        self._extraPrompts = ['Card to put on top']
        self._effects['cards'] = 3
        self._expansion = 'Intrigue'
        self._fullText = 'Cost: 2\n+3 cards\nPut a card from your hand on top \
        of your deck'
        ### needs help
       
class pawn(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Pawn'
        self._isWorking = False
        self._cost = 2
        self._extraPrompts = ['Choose two']
        self._expansion = 'Intrigue'
        self._fullText = 'Cost: 2\nChoose two: +1 Card; +1 Action; +1 Buy; \
        +$1. (The choices must be different.)'
        ### needs help
      
class secretChamber(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Secret Chamber'
        self._isWorking = False
        self._cost = 2
        self._playablePhases = [phase.action,phase.wait]
        self._type = ['Action','Reaction']
        self._extraPrompts = ['Discard any number of cards']
        self._fullText = 'Discard any number of cards. +1$ per card discarded.\
         When another player plays an Attack card, you may reveal this from \
         your hand. If you do, +2 cards, then put 2 cards from your hand on \
         top of your deck.'
         ### needs help
    
class greatHall(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Great Hall'
        self._victoryPoints = 1
        self._cost = 3
        self._types = ['Action','Victory']
        self._expansion = 'Intrigue'
        self._effects['cards'] = 1
        self._effects['actions'] = 1
        self._fullText = '1 VP\n+1 card\n+1 action'
        
class masquerade(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Masquerade'
        self._isWorking = False
        self._cost = 3
        self._effects['cards'] = 2
        self._extraPrompts = ['Trash a card:']
        self._fullText = '+2 cards\nEach player passes a card in their hand \
        to the player on their left. You may trash a card from your hand.'
        ### needs help

class shantyTown(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Shanty Town'
        self._isWorking = False
        self._cost = 3
        self._effects['actions'] = 2
        self._fullText = '+2 actions\nReveal your hand. If you have no action \
        cards in hand, +2 cards.'
        ### needs help
        
class swindler(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Swindler'
        self._isWorking = False
        self._cost = 3
        self._type = ['Action','Attack']
        self._effects['money'] = 2
        self._fullText = '+2$\nEach other player trashes the top card of his \
        deck and gains a card with the same cost that you choose.'
        ### needs help
        
class wishingWell(Card):
    def __init__(self,pile):
        Card.__init__(self,pile)
        self._name = 'Wishing Well'
        self._isWorking = False
        self._cost = 3
        self._effects['actions'] = 1
        self._effects['cards'] = 1
        self._extraPrompts = ['Name a card']
        self._fullText = '+1 card\n+1 action\nName a card, then reveal the \
        top card of your deck. If it is the named card, put it in your hand.'
        ### needs help
