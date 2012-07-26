#!/usr/bin/env python

import curses
import curses.wrapper
import curses.textpad
from time import sleep
import string

class StatusBar(object):
    def __init__(self):
        self._window = curses.newwin(1,80,23,0)
        self._window.keypad(True)
        self._window.bkgd(' ',curses.color_pair(1))
        self._status = ''
        self.setStatus('test status')

    def setStatus(self,newStatus):
        self._status = newStatus
        self._window.erase()
        self._window.addstr(0,0,newStatus,curses.color_pair(1))
        self._window.refresh()

    def getCh(self):
        return self._window.getch()

    def refresh(self):
        self._window.refresh()

class Column(object):
    def __init__(self,cols,x=0,y=0,title='Untitled',height=21):
        self._rowData = []
        self._numRows = 0
        self._scrollOffset = 0
        self._selectedRow = 5
        self._isActiveColumn = False
        self._cols = cols
        self._x = x
        self._y = y
        self._height = 18
        self._titleWindow = curses.newwin(2,cols,y,x)
        self._titleWindow.bkgd(' ',curses.color_pair(1))
        self.setTitle(title[:])
        self._newPad(5)

    def redraw(self):
        title = self._title.center(self._cols)
        self._titleWindow.addstr(0,0,title,curses.color_pair(1) | curses.A_BOLD)
        self._titleWindow.hline(1,0,curses.ACS_HLINE,self._cols)
        self._titleWindow.refresh()
        self._pad.refresh(self._scrollOffset,0,self._y + 2,self._x,\
                self._height + 3,self._cols + self._x)

    def setTitle(self,newTitle):
        self._title = newTitle[:]
        self._titleWindow.erase()
        title = self._title.center(self._cols)
        self._titleWindow.addstr(0,0,title,curses.color_pair(1) | curses.A_BOLD)
        self._titleWindow.hline(1,0,curses.ACS_HLINE,self._cols)
        self._titleWindow.refresh()

    def _newPad(self,rows):
        self._pad = curses.newpad(rows,self._cols)
        self._pad.bkgd(' ',curses.color_pair(1))
        self._numLines = rows

    def setRowData(self,data):
        self._rowData = data[:] #make a copy of the data
        del(self._pad)
        self._numRows = len(self._rowData)
        self._newPad(self._numRows)
        for i,text in enumerate(self._rowData):
            if i == self._selectedRow:
                if self._isActiveColumn:
                    self._pad.addstr(i,0,text,curses.color_pair(1) | \
                            curses.A_REVERSE)
                else:
                    self._pad.addstr(i,0,text,curses.color_pair(1) | \
                            curses.A_REVERSE)
            else:
                self._pad.addstr(i,0,text,curses.color_pair(1))

    def scroll(self,lines=1):
        if self._scrollOffset + lines < 0:
            self._scrollOffset = 0
        elif self._scrollOffset + lines + self._height > self._numRows:
            self._scrollOffset = self._numRows - self._height
        else:
            self._scrollOffset += lines
        self.redraw()

    def _deselect(self,row):
        self._pad.addstr(row,0,self._rowData[row],curses.color_pair(1))

    def _select(self,row):
        self._pad.addstr(row,0,self._rowData[row], \
                curses.color_pair(1) | curses.A_REVERSE)

    def getSelectionOffset(self):
        if self._selectedRow < self._scrollOffset:
            return self._selectedRow - self._scrollOffset
        elif self._selectedRow >= self._scrollOffset + self._height:
            return self._selectedRow - self._height - self._scrollOffset + 1
        else:
            return 0

    def moveSelection(self,lines=1):
        self._deselect(self._selectedRow)
        if self._selectedRow + lines < 0:
            self._selectedRow = 0
        elif self._selectedRow + lines > self._numRows - 1:
            self._selectedRow = self._numRows - 1
        else:
            self._selectedRow += lines
        self._select(self._selectedRow)
        #scroll if needed
        self.scroll(self.getSelectionOffset())
        self.redraw()

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
        self._leftColumn = Column(26,x=0,y=2,title='Test')
        self._centerColumn = Column(26,x=27,y=2,title='Test')
        self._rightColumn = Column(26,x=54,y=2,title='Test')
        self._statusBar = StatusBar()
        self._currentCol = self._leftColumn
        self._redraw()

    def _redraw(self):
        self._borderWin.refresh()
        self._titleWin.refresh()
        self._leftColumn.redraw()
        self._centerColumn.redraw()
        self._rightColumn.redraw()

    def scroll(self,lines=1):
        self._currentCol.scroll(lines)

    def moveSelection(self,lines=1):
        self._currentCol.moveSelection(lines)

    def getCh(self):
        return self._statusBar.getCh()

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
    for i in range(10):
        data.append('row ' + str(i))
    display._leftColumn.setRowData(data)
    for i in range(1):
        for i in range(10):
            sleep(.05)
            display._currentCol.scroll(1)
        for i in range(10):
            sleep(.05)
            display._currentCol.scroll(-1)

    stdscr.nodelay(True)
    display._currentCol.setTitle('aoeu')
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
        elif char == ord('q'):
            break
        elif char == -1:
            pass
        # else:
            # raise Exception(char)
        #display.redraw()

if __name__ == '__main__':
    curses.wrapper(main)
