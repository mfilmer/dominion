from piles import pile
from cards import *

class CardList(object):
    def __init__(self):
        self._cards = set()
        self._populate()

    def add(self,card):
        self._cards.add(card)

    def remove(self,card):
        self._cards.remove(card)

    def getCardText(self,cardName):
        for card in self._cards:
            testCard = card(pile(self))
            if testCard.getName() == cardName:
                break
        return testCard.getFullText()

    def getCost(self,cardName):
        for card in self._cards:
            testCard = card(pile(self))
            if testCard.getName() == cardName:
                break
        return testCard.getCost()

    def getVictoryPoints(self,cardName):
        for card in self._Cards:
            testCard = card(pile(self))
            if testCard.getName() == cardName:
                break
        return testCard.getVictoryPoints()

    def getEffects(self,cardName):
        for card in self._cards:
            testCard = card(pile(self))
            if testCard.getName() == cardName:
                break
        return testCard.getEffects()

    def getCardByName(self,name):
        for card in cards:
            if card(pile(self)).getName() == name:
                return card

    def getCardsInSet(self,setName):
        return set([x for x in self._cards if x(pile(self)).inSet(setName)])

    def getCardsInStoreSet(self,setName):
        pass

    def getCardsInExpansion(self,expName):
        return set([x for x in self._cards if x(pile(self)).getExpansion() \
                == expName])

    def getWorkingCards(self):
        return set([x for x in self._cards if x(pile(self)).isWorking()])

    def _populate(self):
        self.add(gold1)
        self.add(gold2)
        self.add(gold3)
        self.add(gold5)
        self.add(victory1)
        self.add(victory3)
        self.add(victory6)
        self.add(curse)
        self.add(cellar)
        self.add(chapel)
        self.add(moat)
        self.add(chancellor)
        self.add(village)
        self.add(woodcutter)
        self.add(workshop)
        self.add(bureaucrat)
        self.add(feast)
        self.add(gardens)
        self.add(militia)
        self.add(moneylender)
        self.add(remodel)
        self.add(smithy)
        self.add(spy)
        self.add(thief)
        self.add(throneRoom)
        self.add(councilRoom)
        self.add(festival)
        self.add(laboratory)
        self.add(library)
        self.add(market)
        self.add(mine)
        self.add(witch)
        self.add(adventurer)
        self.add(courtyard)
        self.add(pawn)
        self.add(secretChamber)
        self.add(greatHall)
        self.add(masquerade)
        self.add(shantyTown)
        self.add(swindler)
        self.add(wishingWell)

