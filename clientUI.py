#!/usr/bin/env python

import curses
#import curses.textpad      #maybe use to get user supplied text input
from time import sleep      #here for test purposes only. will be removed
import string
from twisted.internet.protocol import Protocol

class StatusBar(object):
    def __init__(self,(row,col)=(0,0),length=80):
        self._statusHistory = []
        self._length = length
        self._row = row
        self._col = col
        self._window = curses.newwin(1,length,row,col)
        self.keypad(True)
        self.nodelay(True)
        self.bkgd(' ',curses.color_pair(1))
        self._index = 0         #history index, 0 == current message
        self._horizOffset = 0   #0 is as far left as possible

    def getCh(self):
        """Get a character that was typed, or -1 if no character was typed"""
        return self._window.getch()

    def setStatus(self,status,attrs=None):
        if attrs is None:
            attrs = curses.color_pair(1)
        self._statusHistory.append((status,attrs))
        self.erase()
        if self._index == 0:
            self._horizOffset = 0
            prefix = ''
        else:
            self._index += 1
            prefix = str(self._index) + ': '
        self._displayText(*self._statusHistory[-1],prefix=prefix)

    def setTempStatus(self,status,attrs=None):
        if attrs is None:
            attrs = curses.color_pair(1)
        self.erase()
        self._displayText(status,attrs)

    #history/scrolling functions
    def scrollHistory(self,step):
        self._index += step
        self._horizOffset = 0
        if self._index < 0:
            self._index = 0
        elif self._index > len(self._statusHistory)-1:
            self._index = len(self._statusHistory)-1
        self.erase()
        if len(self) > 0:
            if self._index == 0:
                prefix = ''
            else:
                prefix = str(self._index) + ': '
            self._displayText(*self._statusHistory[-self._index-1], \
                    prefix=prefix)

    #todo: finish
    def scrollCurrent(self,step):
        """Scroll the current message horizontally. The step parameter indicates
        how many characters to the right to view (negative values view left)."""
        self._horizOffset += step
        if self._horizOffset < 0:
            self._horizOffset = 0

    #Implementation Functions
    #todo: finish
    def _displayText(self,text,attrs,prefix=''):
        """Physically write the status as it should be displayed (including
        any offsets for scrolling. This also refreshes the curses window"""
        #i'm not really sure whats with the self._length-1, but its necessary
        text = prefix + text
        if len(text) >= self._length:
            text = text[0:self._length-4] + '...'
        self._window.addstr(0,0,text,attrs)
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

    def __getitem__(self,value):
        return self._statusHistory[-self._index-1][0]

    def __setitem__(self,value):
        self._statusHistory[-self._index-1] = value

class ColList(object):
    def __init__(self,columns,functions):
        if len(columns) == 0:
            raise ValueError
        if len(columns) != len(functions):
            raise ValueError
        self._columns = zip(functions,columns)
        self._index = 0

    def getCol(self,index=None):
        if index is None:
            return self._columns[self._index][1]
        if index >= len(self._columns) or index < 0:
            raise ValueError
        return self._columns[index][1]

    def getFunc(self,index=None):
        if index is None:
            return self._columns[self._index][0]
        if index >= len(self._columns) or index < 0:
            raise ValueError
        return self._columns[index][0]

    def setCurrent(self,index):
        if index >= len(self._columns) or index < 0:
            raise ValueError
        self._columns[self._index][1].setActive(False)
        self._index = index
        self._columns[self._index][1].setActive(True)

    def isActive(self,index):
        return index == self._index

    def __len__(self):
        return len(self._columns)

    def __getitem__(self,index):
        if index >= len(self._columns) or index < 0:
            raise ValueError
        return self._columns[index]

    def __iter__(self):
        return iter(self._columns)

class Column(object):
    def __init__(self,(row,col)=(0,0),title='',height=20,width=26):
        #row data
        self._rowData = []
        self._isActive = False

        #physical dimensions and location
        self._height = height
        self._visibleRows = height-2
        self._width = width
        self._row = row
        self._col = col

        #scrolling and item selection
        self._scrollOffset = 0
        self._selectedRow = 0
        self._markedRows = set()

        #Windows
        self._titleWindow = curses.newwin(1,width,row,col)
        self._titleWindow.bkgd(' ',curses.color_pair(1))
        self._borderWindow = curses.newwin(1,width,row+1,col)
        self._borderWindow.hline(0,0,curses.ACS_HLINE,self._width)
        self._newPad(0)
        
        #Set up the title
        self._title = (title,curses.color_pair(1))
        #self.setTitle(title)

    def refresh(self):
        self._borderWindow.hline(0,0,curses.ACS_HLINE | curses.color_pair(1), \
                self._width)
        self._borderWindow.refresh()
        self._titleWindow.addstr(0,0,*self._title)
        self._titleWindow.refresh()
        self._pad.refresh(self._scrollOffset,0,self._row + 2,self._col,\
                self._row + self._visibleRows + 1,self._width + self._col)

    def setTitle(self,title,attrs=None,tAlign='Left'):
        if attrs is None:
            attrs = curses.color_pair(1)
        title = title[0:self._width-1]
        if tAlign == 'Left':
            pass
        elif tAlign == 'Center':
            title = '{0:^{width}}'.format(title,width=self._width-1)
        elif tAlign == 'Right':
            title = '{0:>{width}}'.format(title,width=self._width-1)
        else:
            raise ValueError("tAlign must be 'Left','Center', or 'Right'")
        self._title = (title,attrs)
        self._titleWindow.addstr(0,0,*self._title)
        self.refresh()

    def isActive(self):
        return self._isActive

    def setActive(self,state):
        self._isActive = bool(state)
        if len(self._rowData) > 0:
            if self._isActive:
                self._touch(self._selectedRow)
            else:
                self._deselect(self._selectedRow)
            self.refresh()

    def setRowData(self,rowData,attrs=None,reset=True):
        if attrs is None:
            attrs = [curses.color_pair(1)]*len(rowData)
        self._rowData = zip(rowData,attrs)
        
        #clear the screen
        self._pad.erase()
        self.refresh()

        #clear marked and selected rows
        self._markedRows = set()
        if reset:
            self._selectedRow = 0
            self._scrollOffset = 0

        #make a new pad
        del(self._pad)
        self._newPad(len(self._rowData))
        for i,(text,attrs) in enumerate(self._rowData):
            if i == self._selectedRow and self._isActive:
                self._pad.addstr(i,0,text[0:self._width-1],attrs | \
                        curses.A_REVERSE)
            else:
                self._pad.addstr(i,0,text[0:self._width-1],attrs)
        
        self.refresh()

    #navigation functions
    def scroll(self,lines=1):
        if self._scrollOffset + lines < 0:
            self._scrollOffset = 0
        elif self._scrollOffset + lines + self._visibleRows > len(self._rowData):
            if len(self._rowData) < self._visibleRows:
                self._scrollOffset = 0
            else:
                self._scrollOffset = len(self._rowData) - self._visibleRows
        else:
            self._scrollOffset += lines
        self.refresh()

    def moveCursor(self,lines=1):
        self._deselect(self._selectedRow)
        if self._selectedRow + lines < 0:
            self._selectedRow = 0
        elif self._selectedRow + lines >= len(self._rowData):
            self._selectedRow = len(self._rowData) - 1
        else:
            self._selectedRow += lines
        self._touch(self._selectedRow)
        self.scroll(self._getSelectionOffset())

    #row marking
    def toggleMark(self,row):
        self._verifyRow(row)
        if row in self._markedRows:
            self._markedRows.remove(row)
        else:
            self._markedRows.add(row)
        self._touch(row)
        self.refresh()

    def setMark(self,row,marked=True):
        self._verifyRow(row)
        if marked:
            self._markedRows.add(row)
        else:
            self._markedRows.remove(row)
        self._touch(row)
        self.refresh()

    def getMarkedText(self):
        return [self._rowData[i] for i in range(len(self._rowData)) if i in \
                self._markedRows]

    def getSelectedText(self):
        if len(self._rowData) == 0:
            return ''
        return self._rowData[self._selectedRow][0]

    def getSelectedIndex(self):
        if len(self._rowData) == 0:
            return None
        return self._selectedRow

    #implementation functions
    def _newPad(self,rows):
        rows = 1 if rows == 0 else rows
        self._pad = curses.newpad(rows,self._width)
        self._pad.bkgd(' ',curses.color_pair(1))

    def _getSelectionOffset(self):
        if self._selectedRow < self._scrollOffset:
            return self._selectedRow - self._scrollOffset
        elif self._selectedRow >= self._scrollOffset + self._visibleRows:
            return self._selectedRow - self._visibleRows - \
                    self._scrollOffset + 1
        else:
            return 0

    def _touch(self,row):
        self._verifyRow(row)
        if row == self._selectedRow and self._isActive:
            self._pad.addstr(row,0,self._rowData[row][0], \
                    self._rowData[row][1] | curses.A_REVERSE)
        elif row in self._markedRows:
            self._pad.addstr(row,0,self._rowData[row][0],curses.color_pair(2))
        else:
            self._pad.addstr(row,0,*self._rowData[row])

    def _deselect(self,row):
        self._verifyRow(row)
        if row in self._markedRows:
            self._pad.addstr(row,0,self._rowData[row][0],curses.color_pair(2))
        else:
            self._pad.addstr(row,0,*self._rowData[row])

    def _verifyRow(self,row):
        if row >= len(self._rowData) or row < 0:
            raise ValueError

    #other functions
    def __len__(self):
        return len(self._rowData)

class StatusColumn(Column):
    def __init__(self,(row,col)=(0,0),title='',height=20,width=26):
        Column.__init__(self,(row,col),title,height,width)
        self._visibleRows -= 2
        self._statBar = curses.newwin(1,self._width,row+self._height-2,col)
        self._statBar.bkgd(' ',curses.color_pair(1))
        self._statBar.hline(0,0,curses.ACS_HLINE,self._width)
        self._statusBar = StatusBar((row+self._height-1,col),self._width)

    def setStatus(self,status):
        self._statusBar.setTempStatus(status)

    def refresh(self):
        Column.refresh(self)
        self._statusBar.refresh()
        self._statBar.refresh()

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
        self._termHeight = stdscr.getmaxyx()[0]
        self._titleWin = curses.newwin(1,80,0,0)
        self._titleWin.bkgd(' ',curses.color_pair(1))
        #self._titleWin.addstr(0,0,'Dominion',curses.color_pair(1) | \
                #curses.A_BOLD)
        self._borderWin = curses.newwin(self._termHeight,80,0,0)
        self._borderWin.bkgd(' ',curses.color_pair(1))
        self._borderWin.hline(1,0,curses.ACS_HLINE,80)
        self._borderWin.vline(2,26,curses.ACS_VLINE,self._termHeight-4)
        self._borderWin.vline(2,53,curses.ACS_VLINE,self._termHeight-4)
        self._borderWin.hline(self._termHeight-2,0,curses.ACS_HLINE,80)
        colHeight = self._termHeight - 4
        self._columns = ColList([Column((2,0),height=colHeight),\
                StatusColumn((2,27),height=colHeight),\
                Column((2,54),height=colHeight)],['Players','Mesg',None])
        #self._columns = [('Players',Column((2,0),height=self._termHeight-4)),\
                #('Mesg',StatusColumn((2,27),height=self._termHeight-4)),\
                #(None,Column((2,54),height=self._termHeight-4))]
        self._statusBar = StatusBar((self._termHeight-1,0))
        self._columns.setCurrent(0)
        self.refresh()

    def refresh(self):
        self._borderWin.refresh()
        self._titleWin.refresh()
        for func,col in self._columns:
            col.refresh()
        self._statusBar.refresh()

    def scroll(self,lines=1):
        self._columns.getCol().scroll(lines)

    def moveSelection(self,lines=1):
        self._columns.getCol().moveCursor(lines)

    def changeColSelect(self,num):
        if num == 0:
            raise ValueError
        start = self._columns._index
        step = 1 if num > 0 else -1
        end = 2 if num > 0 else 0
        for i in range(start+step,end+step,step):
            if len(self._columns[i][1]) > 0:
                self._columns.setCurrent(i)
                break

    def setTitle(self,title):
        self._titleWin.erase()
        self._titleWin.addstr(0,0,title,curses.color_pair(1) | curses.A_BOLD)
        self._titleWin.refresh()

    def toggleMark(self):
        col = self._columns.getCol()
        col.toggleMark(col.getSelectedIndex())

    def getCh(self):
        return self._statusBar.getCh()

    def setStatus(self,status):
        self._statusBar.setStatus(status)

    def statusHistory(self,step):
        self._statusBar.scrollHistory(step)

