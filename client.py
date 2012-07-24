#!/usr/bin/env python

import curses
import curses.wrapper
import curses.textpad
from time import sleep

def main(stdscr):
    if curses.has_colors():
        text = 'colors exist!'
    else:
        text = 'no colors for you'
    #curses.use_default_colors()
    stdscr.bkgd(' ',curses.color_pair(1))
    curses.init_color(15,500,0,0)
    curses.init_pair(1,0,15)
    curses.init_pair(2,9,15)
    curses.init_pair(3,12,15)
    curses.init_pair(4,14,15)
    stdscr.box()
    stdscr.addstr(1,1,'color content: ' + str(curses.color_content(7)),curses.color_pair(0))
    stdscr.addstr(2,1,'pair content: ' + str(curses.pair_content(3)))
    stdscr.addstr(3,1,text,curses.color_pair(2))
    stdscr.addstr(4,1,'can change color: ' + str(curses.can_change_color()),curses.color_pair(0))
    stdscr.addstr(5,1,'pairs: ' + str(curses.COLOR_PAIRS),curses.color_pair(3))
    stdscr.addstr(6,1,'colors: ' + str(curses.COLORS),curses.color_pair(4))
    #stdscr.border()
    stdscr.vline(1,40,curses.ACS_VLINE,23)
    stdscr.refresh()
    sleep(5)

if __name__ == '__main__':
    curses.wrapper(main)