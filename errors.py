#exceptions from curses ui

#exceptions from base game or cli UI
class EmptyPile(Exception):
    pass

class InsufficientFunds(Exception):
    pass

class InsufficientBuys(Exception):
    pass

class InsufficientActions(Exception):
    pass

class MissingCards(Exception):
    pass

#card is played in the wrong phase
class InvalidPhase(Exception):
    pass

#try to advance phase past last phase
class PhaseError(Exception):
    pass
