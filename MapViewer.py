#!/usr/bin/python
######################################################################
#                     Ascii TMS Viewer
#
#--------------------------------------------------------------------
#  Brian Hone   |     Initial Release
#--------------------------------------------------------------------
#                       
#--------------------------------------------------------------------
# Copyright (c) 2009 Brian Hone
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
######################################################################


import curses, time, sys, os, string, random, math
import pprint
from AsciiTileMap import AsciiTileMap
import KMLParser

false = 0
true = 1
colors  = range( 1, 8 )

splash = """             
         * ASCII *
      TMS Tile Viewing 
          System
      Because It's There
    -- Press Any Key --
"""

class MapViewer:
  def __init__(self, win):
    curses.curs_set(0)
    self.win         = win
    # turn the window's getch into a non-blocking call
    self.win.nodelay(1)
    self.logFile     = sys.stdout
    #self.logFile     = open( "MapViewer_log.txt", "w" )

    self.baseUrl     = "http://tile.openstreetmap.org"
    self.cacheUrl    = "tile.openstreetmap.org"
    self.kmlFiles    = "kml_files.txt"
    self.kmlPoints   = {}
    self.kmlShapes   = {}
    
    # get some dimensions
    self.maxY, self.maxX = self.win.getmaxyx()
    # map subwindow
    self.mainWin = self.win.subwin( self.maxY - 2, int(self.maxX), 0,0 )
    self.mainWin.box()
    self.mainWinMaxY, self.mainWinMaxX = self.mainWin.getmaxyx()
    self.mainMap = " " * self.mainWinMaxX * self.mainWinMaxY

    # instructions subwindow
    self.commandWin = self.win.subwin( 2, self.maxX, self.maxY-2, 0 )
    self.drawCommandWin()

    # tile will always point to north west corner of north west screen tile
    self.tileMap    = AsciiTileMap( (0,0,1), ( self.mainWinMaxX/2 -1, self.mainWinMaxY/2 -1 ), self.baseUrl, self.cacheUrl )

    # BTH TEST:
    #self.tileMap.makeFakeTile( "fake_tile.txt" )
    #self.fake_tile       = open( "fake_tile.txt", "r" ).read()

    self.mapLoaded  = None # optimization - don't load if you don't need to
    self.showCities = false
    self.showLines  = false
    self.showMap    = true
    self.dirty      = true

    self.getMap()
    self.loadKML()

    curses.start_color() 
    self.initColors()
    self.drawSplash()
  # end __init__

  def addColorString( self, map ):
    cmap = { '.' : curses.color_pair(0) ,
             ',' : curses.color_pair(0) ,
             ';' : curses.color_pair(0) ,
             'c' : curses.color_pair(2) ,
             'l' : curses.color_pair(2) ,
             'o' : curses.color_pair(2) ,
             'd' : curses.color_pair(2) ,
             'x' : curses.color_pair(3) ,
             'k' : curses.color_pair(3) ,
             'O' : curses.color_pair(4) ,
             'X' : curses.color_pair(2) ,
             'N' : curses.color_pair(5) ,
             'M' : curses.color_pair(6) ,
             'W' : curses.color_pair(7) 
           }
    x = 1
    y = 1
    for c in map:
      if c == "\n":
        x = 1
        y = y + 1
      elif c == " ":
        x = x + 1 
      else:
        color = cmap[ c ]
        self.mainWin.addch( y,x, ord(c), color )
        x = x + 1
  # end addColorStr
  
  def drawSplash( self ):
    self.splashWin = self.win.subwin( 7, 30 , self.maxY/3, int( self.maxX /3 ) )
    self.splashWin.clear()
    self.splashWin.addstr( 0,0, splash, curses.color_pair(3) )
    self.splashWin.box()
    self.win.nodelay(0)
    self.win.getch()
    self.splashWin.clear()
    self.win.nodelay(1)
  # end drawSplash

  def drawCommandWin( self ):
    self.commandWinMaxY, self.commandWinMaxX = self.commandWin.getmaxyx()
    helpString = "[+] Zoom in  [-]  Zoom out  [j] West [k] East [i] North [m] South [g] Jump to Location [c] Show Cities     [q] Quit" 
    self.commandWin.addstr( 0, 0, helpString, curses.A_BOLD )
  # end drawCommandWin


  def loadKML( self ):
    """ Load cities and countries from a kml file - ./kml_files.txt lists kml files to load"""
    kmlFiles = [ string.strip( line ) for line in open( self.kmlFiles, "r" ).readlines() ] 
    for line in kmlFiles:
      if line[0] == "#":
        pass
      else:
        lineParts = string.split( line, "," )
        reader = KMLParser.kmlReader( lineParts[1] )
        coords = reader.getCoordinates()  
        for c in coords:
          if c.has_point and c.point.lat and c.point.lon:
            self.kmlPoints[ c.name ] = { "LON" : c.point.lon, "LAT" : c.point.lat, "NAME": c.name, "ZOOMLEVEL" : int( lineParts[0] ) }
          if c.has_linear_ring:
            self.kmlShapes[ c.name ] = { "NAME" : c.name, "ZOOMLEVEL" : int( lineParts[0] ), "POINTS" : c.linear_ring.points }
  # end getCities

  def loadFile( self ):
    self.commandWin.clear()  
    prompt = "Enter Path to File: "
    valid_file = false
    self.commandWin.addstr( 0,0, prompt, curses.A_BOLD )
    curses.echo()
    self.commandWin.move( 0, len(prompt) )
    res = self.commandWin.getstr( 0, len(prompt) ) 
    # put in error handling here
    file = string.lstrip( res )
    try:
      self.logFile.write( "loaded: %s\n" % ( file ) )
    except:
      self.logFile.write( "error: can't load %s\n" % ( file ) )
    self.drawCommandWin()
  # end loadFile

  def getLocation( self ):
    self.commandWin.clear()
    prompt = "Enter Lat (-85:85), Lon (-180:180), Zoom (0:18) or [c]ancel: "
    prompt2 = "Enter Lat,Lon,Zoom or [c]ancel:"
    valid_lla = false
    self.commandWin.addstr(0,0, prompt, curses.A_BOLD )
    curses.echo()
    self.commandWin.move( 0,len(prompt) )
    res = self.commandWin.getstr( 0, len(prompt) ) 
    while not valid_lla:
      # First grab a cancel
      string.lstrip(res)
      if res[0] == "c" or res[0] == "C":
        self.commandWin.clear()
        self.drawCommandWin()
        return

      # 2. Try CSV
      if res.find( "," ) > 0:
        args = string.split( res, "," ) 
      # 3. Try Space delimited
      else:
        args = string.split( res )
  
      # 4. Bail on bad args
      if len(args) != 2 and len(args) != 3:
        valid_lla
      else:
        try:
          lat = float( args[0] )
          lon = float( args[1] )
          if len( args ) == 2:
            zoom = self.tileMap.z
          else:
            zoom = int( args[2] )
          valid_lla = true
          # TODO: test for valid ranges
        except:
          valid_lla = false
      if not valid_lla:
        self.commandWin.clear()  
        self.commandWin.addstr( 0, 0, prompt2, curses.A_BOLD )
        self.commandWin.move( 0, 0 + len(prompt2) )
        res = self.commandWin.getstr( 0, 0+len(prompt2) )
    self.tileMap.moveToPoint( lat, lon, zoom )
    self.drawCommandWin()
    
  #end getLocation

  def initColors( self ):
    colors          = [ curses.COLOR_BLUE,  
                        curses.COLOR_CYAN,  
                        curses.COLOR_GREEN,   
                        curses.COLOR_MAGENTA,   
                        curses.COLOR_RED,   
                        curses.COLOR_WHITE, 
                        curses.COLOR_YELLOW  ]
    self.color_pairs = []
    q = 2
    # this is the map color
    curses.init_pair( 12, curses.COLOR_BLUE, curses.COLOR_BLACK )
    self.highlightColor = 20
    curses.init_pair( self.highlightColor, curses.COLOR_BLACK, curses.COLOR_RED )
    # now set up all the other colors (against black background )
    for i in range( len( colors ) ):
      curses.init_pair( q, colors[i], curses.COLOR_BLACK )
      q = q + 1
  #end initColors

  def pixelIsShown( self, px, py ):
    self.mainWinMaxY, self.mainWinMaxX = self.mainWin.getmaxyx()
    if px > 0 and px < self.mainWinMaxX and py > 0 and py < self.mainWinMaxY:
      return true
    return false;
  # end pixelIsShown

  def drawLine( self, fromY, fromX, toY, toX, ch ):
    """ draw from YX to YX using the character ch """
    deltaY = toY - fromY
    deltaX = toX - fromX
    pts = []
    pts.append( [fromX, fromY] )
    direction = 1

    if abs(deltaX) > abs(deltaY):
      if toX - fromX < 0:
        direction = -1
      for x in range( fromX+1, toX, direction ):
        pts.append( [x, fromY + deltaY * (( x-fromX ) / float(deltaX))  ] )
    else:
      if toY - fromY < 0:
        direction = -1
      for y in range( fromY+1, toY, direction ):
        pts.append( [ fromX + deltaX * (( y-fromY ) / float(deltaY)), y ] )

    for pt in pts:
      if self.pixelIsShown( pt[0], pt[1] ):
        try:
          self.mainWin.addch( int(pt[1]), int(pt[0]), ord(ch), curses.color_pair(8) )
        except:
          pass
    self.mainWin.refresh()
  # end drawLine 

  def drawLatLonLine( self, latA, lonA, latB, lonB ):
    resA = self.tileMap.latlon2pixel( "A", latA, lonA, self.tileMap.z )
    resB = self.tileMap.latlon2pixel( "B", latB, lonB, self.tileMap.z ) 
    self.drawLine( resA[1], resA[0], resB[1], resB[0], '.' )    
  # end drawLatLonLine

  def drawLines( self ):
    if not self.showLines:
      return
    for shape in self.kmlShapes.items():
      shape = shape[1]
      points = shape["POINTS"]
      last_point = points[0]
      for point in shape["POINTS"][1:]:
        self.drawLatLonLine( last_point.lat,last_point.lon,point.lat,point.lon );
        last_point = point
  #end showLine

  def drawCities( self ):
    """ draw cities """
    # 1. Check if we have a kml overlay tile already created
    # 2. If so, go to the correct screen position and call addColorSting
    # 3. If not, create one, then load it and call addColorString
    # 123456
    if not self.showCities:
      return
    for key, value in self.kmlPoints.items():
      lat = float( value[ "LAT" ] )
      lon = float( value[ "LON" ] )
      if self.tileMap.z > value[ "ZOOMLEVEL" ]:
        res = self.tileMap.latlon2pixel( value["NAME" ], lat, lon, self.tileMap.z )

        # TODO: This logic relies on error handling to determine whether
        #       a point is "onscreen" - do something better
        if res != None:
          pixX, pixY = res[0], res[1]
          try:
            self.mainWin.addstr( pixY, pixX, value[ "NAME" ], curses.color_pair(7) )
          except:
            pass
  # end drawCities
    
  def drawMainWin( self ):
    """ draw a map in the map window """
    if self.showMap:
      self.addColorString( self.mainMap )
    else:
      self.mainWin.clear()
    # BTH Test
    #self.addColorString( self.fake_tile )
    self.drawLines()
    self.drawCities()
  # end drawMap

  def drawMainWindow(self):
    self.win.border()
    self.run()
  # end drawWindow

  def canFitString( self, s, pos ):
    if pos[1] > 0 and pos[1]+len(s) < self.mainWinMaxX and pos[0]>0 and pos[0] < self.mainWinMaxY:
      return 1
    else:
      return 0
  # end canFitString

  def getMap(self):
    self.mainMap = self.tileMap.getMap()
  # end getMap 

  def nextFrame( self ):
    pass
  # end nextFrame

  def run( self ):
    while 1:
      time.sleep(0.5)
      c = self.win.getch()
      if c == ord( 'q' ):
        break
      elif c == ord( 'g' ):
        self.getLocation()
      elif c == ord('+'):
        self.dirty = true
        self.tileMap.zoomIn()
      elif c == ord('-'):
        self.dirty = true
        self.tileMap.zoomOut()
      elif c == ord( 'j' ) or c == curses.KEY_LEFT:
        self.dirty = true
        self.tileMap.moveWest()
      elif c == ord( 'k' ) or c == curses.KEY_RIGHT:
        self.dirty = true
        self.tileMap.moveEast()
      elif c == ord( 'm' ) or c == curses.KEY_DOWN:
        self.dirty = true
        self.tileMap.moveSouth()
      elif c == ord( 'i' ) or c == curses.KEY_UP:
        self.dirty = true
        self.tileMap.moveNorth()
      elif c == ord( 'l' ):
        self.dirty = true
        if self.showLines:
          self.showLines   = false
        else:
          self.showLines   = true
      elif c == ord( 'c' ):
        self.dirty = true
        if ( self.showCities ):
          self.showCities = false
        else:
          self.showCities = true
      elif c == ord( 'M' ):
        self.dirty = true
        if self.showMap:
          self.showMap = false
        else:
          self.showMap = true
      elif c == ord( 'f' ):
        self.loadFile()
      elif c == ord( 'n' ):
        self.nextFrame()
      if self.dirty:
        self.getMap()    
        self.drawMainWin()
        self.mainWin.box()
        self.mainWin.refresh()
        self.commandWin.refresh()
      self.dirty = false
# end class MapViewer

def main( scr ):
  t = MapViewer( scr )
  t.drawMainWindow( )
# end main

if __name__=="__main__":
  curses.wrapper( main ) 


