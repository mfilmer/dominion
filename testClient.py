#!/usr/bin/env python

from clientUI import *

class TheClient(Display):
    def __init__(self,stdscr):
        Display.__init__(self,stdscr)
        data = ['row: ' + str(x) for x in range(30)]
        for func,col in self._columns:
            col.setRowData(data)
            if func == 'Mesg':
                col.setStatus('aoe')

    def checkForInput(self):           #called by twisted's reactor
        char = self.getCh()
        if char == -1:          #no key was pressed
            pass
        elif char == 27:          #ESC key
            #will eventually clear selection
            pass
        elif char == curses.KEY_NPAGE:
            self.scroll(1)
        elif char == curses.KEY_PPAGE:
            self.scroll(-1)
        elif char == curses.KEY_UP:
            self.moveSelection(-1)
        elif char == curses.KEY_DOWN:
            self.moveSelection(1)
        elif char == curses.KEY_LEFT:
            self.changeColSelect(-1)
        elif char == curses.KEY_RIGHT:
            self.changeColSelect(1)
        elif char == ord('n'):
            self.setStatus('advance phase')
        elif char == ord('a'):
            theCol = PopupColumn((1,24),title='Ahh',height=21,width=32)
            theCol.setRowData(['row: ' + str(x) for x in range(20)])
        elif char == ord('q'):
            return True
        elif char == ord(' '):
            self.toggleMark()
        #elif char == curses.KEY_ENTER: #for some reason this doesnt work
        elif char == ord('\n'):
            self.submit()
        elif char == ord('\t'):
            #will eventually switch between different player's screens
            pass
        elif char == ord('?'):
            #will eventually give card info
            pass
        elif char == 337:   #shift up (linux)
            self.statusHistory(1)
        elif char == 336:   #shift down (linux)
            self.statusHistory(-1)
        elif char == 547:   #shift up (windows)
            self.statusHistory(1)
        elif char == 548:   #shift down (windows)
            self.statusHistory(-1)
        #else:
            #raise Exception(char)
        return False

def main(stdscr):
    display = TheClient(stdscr)
    #display._leftColumn.setTitle('test',curses.A_BOLD | curses.color_pair(1), \
            #tAlign='Center')
    while not display.checkForInput():
        pass
    for i in xrange(25):
        print ''

if __name__ == '__main__':
    curses.wrapper(main)
