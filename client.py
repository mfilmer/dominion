#!/usr/bin/env python

import curses
import curses.wrapper
import curses.textpad
from time import sleep
import string

class StatusBar(object):
    def __init__(self):
        self._window = curses.newwin(1,1,23,0)
        self._window.bkgd(' ',curses.color_pair(1))

class Column(object):
    def __init__(self,(rows,cols),x=0,y=0,title='Untitled'):
        self._rowData = []
        self._dataRow = 0
        self._rows = rows
        self._cols = cols
        self._x = x
        self._y = y
        self._title = title
        self._titleWindow = curses.newwin(2,cols,y,x)
        self._titleWindow.bkgd(' ',curses.color_pair(1))
        self._pad = curses.newpad(rows,cols)
        self._pad.bkgd(' ',curses.color_pair(1))
        self._pad.scrollok(True)
        self._pad.idlok(True)

    def redraw(self):
        title = self._title.center(self._cols)
        self._titleWindow.addstr(0,0,title,curses.color_pair(1) | curses.A_BOLD)
        self._titleWindow.hline(1,0,curses.ACS_HLINE,self._rows)
        self._titleWindow.refresh()
        self._pad.refresh(self._dataRow,0,self._y + 2,self._x,21,self._cols + \
                self._x)

    def setRowData(self,data):
        self._rowData = data
        self._pad.erase()
        for i,text in enumerate(data):
            self._pad.addstr(i,0,text,curses.color_pair(1))
        self._pad.clrtobot()

    def scrollUp(self,lines=1):
        self._dataRow += 1

    def scrollDown(self,lines=1):
        self._dataRow -= 1

class Display(object):
    def __init__(self,stdscr):
        curses.curs_set(0)
        if curses.COLORS == 8:
            curses.use_default_colors()
            curses.init_pair(1,-1,-1)
        elif curses.COLORS == 16:
            curses.init_pair(1,0,15)
        stdscr.bkgd(' ',curses.color_pair(1))
        self._stdscr = stdscr
        self._titleWin = curses.newwin(1,80,0,0)
        self._titleWin.bkgd(' ',curses.color_pair(1))
        self._titleWin.addstr(0,0,'Dominion',curses.color_pair(1) | \
                curses.A_BOLD)
        self._borderWin = curses.newwin(24,80,0,0)
        self._borderWin.bkgd(' ',curses.color_pair(1))
        self._borderWin.hline(1,0,curses.ACS_HLINE,80)
        self._borderWin.vline(2,26,curses.ACS_VLINE,20)
        self._borderWin.vline(2,53,curses.ACS_VLINE,20)
        self._borderWin.hline(22,0,curses.ACS_HLINE,80)
        self._leftColumn = Column((100,26),x=0,y=2,title='Test')
        self._centerColumn = Column((100,26),x=27,y=2,title='Test')
        self._rightColumn = Column((100,26),x=54,y=2,title='Test')

    def redraw(self):
        self._borderWin.refresh()
        self._titleWin.refresh()
        self._leftColumn.redraw()
        self._centerColumn.redraw()
        self._rightColumn.redraw()

def main(stdscr):
    #curses.use_default_colors()
    #curses.init_pair(1,0,15)
    #stdscr.bkgd(' ',curses.color_pair(1))
    #stdscr.refresh()
    #sleep(2)
    #curses.init_color(15,500,0,0)
    #curses.init_pair(1,0,15)
    #curses.init_pair(2,9,15)
    #curses.init_pair(3,12,15)
    #curses.init_pair(4,14,15)

    display = Display(stdscr)
    data = []
    for i in range(100):
        data.append('row ' + str(i))
    display._leftColumn.setRowData(data)
    for i in range(1):
        for i in range(10):
            display.redraw()
            sleep(.5)
            display._leftColumn.scrollUp()
        for i in range(10):
            display.redraw()
            sleep(.5)
            display._leftColumn.scrollDown()
        display.redraw()
        sleep(2)

if __name__ == '__main__':
    curses.wrapper(main)
