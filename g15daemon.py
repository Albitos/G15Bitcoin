#    This file is part of pyg15daemon.
#
#    pyg15daemon is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    pyg15daemon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyg15daemon; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#    (c) 2006 Sven Ludwig
#
#    This is the python binding for the g15daemon written by Mike Lampard,
#    Philip Lawatsch, and others.

"""Python binding for g15daemon

available at http://g15daemon.sf.net

This script will be available at http://abraumhal.de/
"""

import socket,time

SCREEN_PIXEL=0
"""Setup a pixel buffer"""
SCREEN_TEXT=1
"""Setup a text buffer"""
SCREEN_WBMP=2
"""Setup a wbmp buffer"""

MAX_X=160
"""Maximum x axis resolution"""
MAX_Y=43
"""Maximum y axis resolution"""
MAX_BUFFER_LENGTH=MAX_X*MAX_Y
"""Maximum buffer length"""

PIXEL_ON=chr(1)
"""Pixel which is set or on"""
PIXEL_OFF=chr(0)
"""Pixel which is unset or off"""

def loader_ascii_10_format(file):
    """Loads data from file which is formated in the following way:
11101101011...

it the length must be 4800 chars
"""
    buf=open(file).read()
    nbuf=''
    for i in range(0,len(buf)):
        if buf[i] == '0' or buf[i] == '1':
            nbuf+=chr(ord(buf[i])-48)
    return nbuf

class g15screen:
    """G15daemon communication class"""

    def __init__(self,screentype,host='localhost',port=15550):
        """screentype uses these variables:
  SCREEN_PIXEL, SCREEN_TEXT and SCREEN_WBMP
host:
  g15daemon listening host
port:
  g15daemon listening port
"""
        if screentype == SCREEN_PIXEL:
            self.init_string="GBUF"
        elif screentype == SCREEN_TEXT:
            self.init_string="TBUF"
        elif screentype == SCREEN_WBMP:
            self.init_string="WBUF"
        self.remote_host=host
        self.remote_port=port
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.remote_host, self.remote_port))
        if self.socket.recv(16) != "G15 daemon HELLO":
            raise Exception("Communication error with server")
        self.socket.send(self.init_string)
        self.clear()

    def __del__(self):
        """Close socket"""
        self.socket.close()

    def __validate_buffer(self,buf, use_exceptions):
        """Validate given buffer"""
        if len(buf) != MAX_BUFFER_LENGTH:
            if use_exceptions:
                raise Exception("Buffer has wrong size(%d)" % len(buf))
            return False
        for i in range(0,MAX_BUFFER_LENGTH):
            if not self.__validate_pixel(buf[i]):
                if use_exceptions:
                    raise Exception("Buffer contains at position %d an invalid char" % i)
                return False
        self.screen=str(buf)
        return True

    def __validate_pixel(self,pixel):
        """Validate given pixel"""
        return pixel==PIXEL_OFF or pixel==PIXEL_ON

    def clear(self):
        self.screen=''
        for i in range(0,MAX_BUFFER_LENGTH):
            self.screen+=PIXEL_OFF
        
    def load(self, file,loader_function, use_exceptions=True):
        """Loads a pixmap from a file using a given loader funktion"""
        buf=loader_function(file)
        return self.__validate_buffer(buf,use_exceptions)

    def set_buffer(self, buf, use_exceptions=True):
        """Set a new buffer"""
        return self.__validate_buffer(buf,use_exceptions)

    def set_pixel(self, x, y, pixel):
        """Set a pixel in buffer"""
        if not self.__validate_pixel(pixel):
            return False
        if x < 0 or x >= MAX_X:
            return False
        if y < 0 or y >= MAX_Y:
            return False
        position=x+y*MAX_X
        if x == 0 and y == 0:
            self.screen='%s%s' % (pixel,self.screen[1:])
        elif y == MAX_Y - 1 and x == MAX_X -1:
            self.screen='%s%s' % (self.screen[:-1],pixel)
        else:
            self.screen='%s%s%s' % (
              self.screen[:position],
              pixel,
              self.screen[position+1:]
            )

    def display(self):
        """Show current buffer on display"""
        self.socket.send(self.screen)

if __name__ == "__main__":
    g15=g15screen(SCREEN_PIXEL)
    try:
        open('lcd.ascii')
        file=True
    except:
        file=False
    if file:
        g15.load('lcd.ascii',loader_ascii_10_format)
        g15.display()
        time.sleep(1)
        for y in range(MAX_Y):
            for x in range(MAX_X+1):
                g15.set_pixel(x,y, PIXEL_ON)
            g15.display()
            time.sleep(0.2)
    else:
        g15.clear()
        for i in range(MAX_X):
            g15.set_pixel(i,0, PIXEL_ON)
            g15.set_pixel(i,MAX_Y-1, PIXEL_ON)

            if i>4 and i<MAX_X-5:
                g15.set_pixel(i,5, PIXEL_ON)
                g15.set_pixel(i,MAX_Y-6, PIXEL_ON)

            if i < MAX_Y:
                g15.set_pixel(0,i, PIXEL_ON)
                g15.set_pixel(MAX_X-1,i, PIXEL_ON)

                if i > 5 and i < MAX_Y -5:
                    g15.set_pixel(5,i, PIXEL_ON)
                    g15.set_pixel(MAX_X-6,i, PIXEL_ON)
        g15.display()
    time.sleep(5)
    del(g15)
