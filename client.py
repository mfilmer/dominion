import curses
from clientUI import *
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint

def main(stdscr):
    display = Display(stdscr)
    data = []
    for i in range(30):
        data.append('row ' + str(i))
    display._leftColumn.setRowData(data)
    display._centerColumn.setRowData(data)
    display._rightColumn.setRowData(data)
    #display._leftColumn.setTitle(' ')
    #display._centerColumn.setTitle(' ')
    #display._rightColumn.setTitle(' ')
    display._redraw()
    for i in range(1):
        for i in range(10):
            sleep(.05)
            display._currentCol.scroll(1)
        for i in range(10):
            sleep(.05)
            display._currentCol.scroll(-1)

    stdscr.nodelay(True)
    while True:
        char = display.getCh()
        if char == 27:
            display._statusBar.setStatus('exiting')
            sleep(.5)
            break
        elif char == curses.KEY_NPAGE:
            display.scroll(1)
            display._statusBar.setStatus('page down')
        elif char == curses.KEY_PPAGE:
            display.scroll(-1)
            display._statusBar.setStatus('page up')
        elif char == curses.KEY_UP:
            display.moveSelection(-1)
            display._statusBar.setStatus('up')
        elif char == curses.KEY_DOWN:
            display.moveSelection(1)
            display._statusBar.setStatus('down')
        elif char == curses.KEY_LEFT:
            display.changeColSelect(-1)
        elif char == curses.KEY_RIGHT:
            display.changeColSelect(1)
        elif char == ord('q'):
            break
        elif char == ord(' '):
            display.toggleMark()
        elif char == -1:
            pass
        #else:
            #raise Exception(char)

if __name__ == '__main__':
    curses.wrapper(main)