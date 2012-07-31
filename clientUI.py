#!/usr/bin/env python

import curses
#import curses.textpad      #maybe use to get user supplied text input
from time import sleep      #here for test purposes only. will be removed
import string
from twisted.internet.protocol import Protocol

class StatusBar(object):
    def __init__(self,(row=0,col=0),len=80):
        self._statusHistory = []
        self._length = len
        self._window = curses.newwin(1,len,row,col)
        self.keypad(True)
        self.nodelay(True)
        self.bkgd(' ',curses.color_pair(1))
        self._index = 0         #history index, 0 == current message
        self._horizOffset = 0   #as far left as possible

    def getCh(self):
        """Get a character that was typed, or -1 if no character was typed"""
        return self._window.getch()

    #todo: finish
    def setStatus(self,status,attrs=curses.color_pair(1)):
        self._statusHistory.append((status,attrs))
        self.erase()
        if self._index == 0:
            self._horizOffset = 0
            self._displayText(*self._statusHistory[-1])
        else:
            self._displayText(str(-self._index+2)+': ' + \
                    self._statusHistory[-self._index-1])
            self._index += 1

    #history/scrolling functions
    #todo: finish
    def scrollHistory(self,step):
        pass

    #todo: finish
    def scrollCurrent(self,step):
        """Scroll the current message horizontally. The step parameter indicates
        how many characters to the right to view (negative values view left)."""
        pass

    #Implementation Functions
    #todo: finish
    def _displayText(self,text,attrs):
        """Physically write the status as it should be displayed (including
        any offsets for scrolling. This also refreshes the curses window"""
        #i'm not really sure whats with the length-1, but its necessary
        if len(text) > self._length-1:
            self._window.addstr(0,0,status[0:76]+'...',attrs)
        else:
            self._window.addstr(0,0,status,attrs)
        self.refresh()

    #curses window functions
    def refresh(self):
        self._window.refresh()

    def bkgd(self,character,attrs):
        self._window.bkgd(character,attrs)

    def nodelay(self,value):
        self._window.nodelay(value)

    def keypad(self,value):
        self._window.keypad(value)

    def erase(self):
        self._window.erase()

    #other functions
    def __len__(self):
        return len(self._statusHistory)

class StatusBar(object):
    def __init__(self):
        self._statusHistory = []
        self._window = curses.newwin(1,80,23,0)
        self._window.keypad(True)
        self._window.nodelay(True)
        self._window.bkgd(' ',curses.color_pair(1))
        self._index = -1

    def setStatus(self,newStatus):
        self._statusHistory.append(newStatus)
        self._window.erase()
        if self._index == -1:
            self._printStatus(self._statusHistory[-1])
        else:
            self._printStatus(str(-self._index-1)+': ' + \
                    self._statusHistory[self._index])
            self._index -= 1

    def getCh(self):
        return self._window.getch()

    def refresh(self):
        self._window.refresh()

    def scrollHistory(self,step):
        self._index += step
        if self._index > -1:
            self._index = -1
        elif self._index < -len(self._statusHistory):
            self._index = -len(self._statusHistory)
        self._window.erase()
        if self._index == -1:
            self._printStatus(self._statusHistory[-1])
        else:
            self._printStatus(str(-self._index-1)+': ' + \
                    self._statusHistory[self._index])

    def _printStatus(self,status):
        if len(status) > 79:
            self._window.addstr(0,0,status[0:76]+'...',curses.color_pair(1))
        else:
            self._window.addstr(0,0,status,curses.color_pair(1))
        self.refresh()

class Column(object):
    def __init__(self,cols,x=0,y=0,title='Untitled',height=21):
        self._rowData = []
        self._numRows = 0
        self._markedRows = set()
        self._scrollOffset = 0
        self._selectedRow = 0
        self.__isActive = False
        self._cols = cols
        self._x = x
        self._y = y
        self._height = 18
        self._titleWindow = curses.newwin(2,cols,y,x)
        self._titleWindow.bkgd(' ',curses.color_pair(1))
        self.setTitle(title[:])
        self._newPad(5)

    @property
    def _isActive(self):
        return self.__isActive
    @_isActive.setter
    def _isActive(self,value):
        if value:
            self.__isActive = True
            self._select(self._selectedRow)
        else:
            self.__isActive = False
            self._deselect(self._selectedRow)

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
        if rows == 0:
            rows = 1
        self._pad = curses.newpad(rows,self._cols)
        self._pad.bkgd(' ',curses.color_pair(1))
        self._numLines = rows

    def setRowData(self,data):
        self._rowData = data[:] #make a copy of the data
        self._pad.erase()
        self.redraw()
        del(self._pad)
        self._numRows = len(self._rowData)
        self._newPad(self._numRows)
        for i,text in enumerate(self._rowData):
            if i == self._selectedRow and self._isActive:
                if self._isActive:
                    self._pad.addstr(i,0,text,curses.color_pair(1) | \
                            curses.A_REVERSE)
            else:
                self._pad.addstr(i,0,text,curses.color_pair(1))
        self._markedRows = set()
        self.redraw()

    def scroll(self,lines=1):
        if self._scrollOffset + lines < 0:
            self._scrollOffset = 0
        elif self._scrollOffset + lines + self._height > self._numRows:
            if self._numRows < self._height:
                self._scrollOffset = 0
            else:
                self._scrollOffset = self._numRows - self._height
        else:
            self._scrollOffset += lines
        self.redraw()

    def getSelectedText(self):
        return self._rowData[self._selectedRow]

    def getMarkedText(self):
        return [self._rowData[i] for i in range(len(self._rowData)) if i in \
                self._markedRows]

    def _deselect(self,row):
        if row in self._markedRows:
            self._pad.addstr(row,0,self._rowData[row],curses.color_pair(2))
        else:
            self._pad.addstr(row,0,self._rowData[row],curses.color_pair(1))

    def _select(self,row):
        if len(self._rowData):
            self._pad.addstr(row,0,self._rowData[row], \
                    curses.color_pair(1) | curses.A_REVERSE)

    def getSelectionOffset(self):
        if self._selectedRow < self._scrollOffset:
            return self._selectedRow - self._scrollOffset
        elif self._selectedRow >= self._scrollOffset + self._height:
            return self._selectedRow - self._height - self._scrollOffset + 1
        else:
            return 0

    def toggleMark(self,row):
        if row in self._markedRows:
            self._markedRows.remove(row)
        else:
            self._markedRows.add(row)
        self._deselect(row)
        self.redraw()

    def moveSelection(self,lines=1):
        self._deselect(self._selectedRow)
        if self._selectedRow + lines < 0:
            self._selectedRow = 0
        elif self._selectedRow + lines > self._numRows - 1:
            self._selectedRow = self._numRows - 1
        else:
            self._selectedRow += lines
        self._select(self._selectedRow)
        self.scroll(self.getSelectionOffset())
        self.redraw()

    def __len__(self):
        return len(self._rowData)

class Display(object):
    def __init__(self,stdscr):
        curses.curs_set(0)
        if curses.COLORS == 8:          #gnome-terminal
            curses.use_default_colors()
            curses.init_pair(1,-1,-1)
            curses.init_pair(2,4,-1)    #marked
        elif curses.COLORS == 16:       #windows command prompt
            curses.init_pair(1,0,15)
            curses.init_pair(2,9,15)    #marked (blue on white)
        stdscr.bkgd(' ',curses.color_pair(1))
        self._stdscr = stdscr
        self._stdscr.nodelay(True)
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
        self._leftColumn = Column(26,x=0,y=2,title='Players')
        self._centerColumn = Column(26,x=27,y=2,title='')
        self._rightColumn = Column(26,x=54,y=2,title='')
        self._statusBar = StatusBar()
        self._currentCol = self._leftColumn
        self._currentCol._isActive = True
        #self._leftColumn.setRowData(map(str,range(50)))
        #self._centerColumn.setRowData(map(str,range(50)))
        #self._rightColumn.setRowData(map(str,range(50)))
        self._columns = zip(['Players',None,None],[self._leftColumn,\
                self._centerColumn,self._rightColumn])
        self._redraw()

    def _redraw(self):
        self._borderWin.refresh()
        self._titleWin.refresh()
        self._leftColumn.redraw()
        self._centerColumn.redraw()
        self._rightColumn.redraw()
        self._statusBar.refresh()

    def scroll(self,lines=1):
        self._currentCol.scroll(lines)

    def moveSelection(self,lines=1):
        self._currentCol.moveSelection(lines)

    def changeColSelect(self,num):
        if num == 0:
            raise ValueError
        if num < 0:
            if self._currentCol == self._centerColumn:
                if len(self._leftColumn):
                    self._centerColumn._isActive = False
                    self._currentCol = self._leftColumn
                    self._centerColumn.redraw()
            elif self._currentCol == self._rightColumn:
                if len(self._centerColumn):
                    self._rightColumn._isActive = False
                    self._currentCol = self._centerColumn
                    self._rightColumn.redraw()
                elif len(self._leftColumn):
                    self._rightColumn._isActive = False
                    self._currentCol = self._leftColumn
                    self._rightColumn.redraw()
        elif num > 0:
            if self._currentCol == self._centerColumn:
                if len(self._rightColumn):
                    self._centerColumn._isActive = False
                    self._currentCol = self._rightColumn
                    self._centerColumn.redraw()
            elif self._currentCol == self._leftColumn:
                if len(self._centerColumn):
                    self._leftColumn._isActive = False
                    self._currentCol = self._centerColumn
                    self._leftColumn.redraw()
                elif len(self._rightColumn):
                    self._leftColumn._isActive = False
                    self._currentCol = self._rightColumn
                    self._leftColumn.redraw()
        self._currentCol._isActive = True
        self._currentCol.redraw()

    def setTitle(self,title):
        self._titleWin.erase()
        self._titleWin.addstr(0,0,title,curses.color_pair(1) | curses.A_BOLD)
        self._titleWin.refresh()

    def toggleMark(self):
        self._currentCol.toggleMark(self._currentCol._selectedRow)

    def getCh(self):
        return self._statusBar.getCh()

    def setStatus(self,status):
        self._statusBar.setStatus(status)

    def statusHistory(self,step):
        self._statusBar.scrollHistory(step)

