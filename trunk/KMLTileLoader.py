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

import time, sys, os, string, random, math
import pprint
from TileLoader import TileLoader
import KMLParser

false = 0
true = 1
debug = 1

class KMLTileLoader( TileLoader ):
  def __init__(self, (sizeX, sizeY), kmlFile, cacheUrl, zoomlevel ):
    TileLoader.__init__( self, (sizeX, sizeY), cacheUrl )
    self.zoomLevel    = zoomlevel # minzoomlevel
    self.kmlFile      = kmlFile
    self.kmlPoints    = {}
    self.kmlShapes    = {}
    self.initKML()
    #self.tileUtils    = TileUtils()
  # end __init__

  def fetchTile( self, x, y, z ):
    tileArr = self.getEmptyTile()
    #print tileStr
    for key, value in self.kmlPoints.items():
      lat = float( value[ "LAT" ] )
      lon = float( value[ "LON" ] )
      # returns None if point does not intersect
      res = self.tileUtils.latlon2pixel( value["NAME" ], lat, lon, self.sizeX, self.sizeY, x,y, z )

      # TODO: This logic relies on error handling to determine whether
      #       a point is "onscreen" - do something better
      if res != None:
          pixX, pixY = res[0], res[1]
          tileArr = self.addTextToTile( pixX, pixY, value[ "NAME" ], tileArr )
    return tileArr
  # end createTile

  def initKML( self ):
    """ Load cities and countries from a kml file - ./kml_files.txt lists kml files to load"""
    reader = KMLParser.kmlReader( self.kmlFile )
    coords = reader.getCoordinates()  
    for c in coords:
        if c.has_point and c.point.lat and c.point.lon:
            self.kmlPoints[ c.name ] = { "LON" : c.point.lon, "LAT" : c.point.lat, "NAME": c.name, "ZOOMLEVEL" : self.zoomLevel }
        if c.has_linear_ring:
            self.kmlShapes[ c.name ] = { "NAME" : c.name, "ZOOMLEVEL" : self.zoomLevel, "POINTS" : c.linear_ring.points }
  # end loadKML

  def drawLatLonLine( self, latA, lonA, latB, lonB, x, y, z ):
    resA = self.tileUtils.latlon2pixel( "A", latA, lonA, self.sizeX, self.sizeY, x, y, z )
    resB = self.tileUtils.latlon2pixel( "B", latB, lonB, self.sizeX, self.sizeY, x, y, z )
    self.drawLine( resA[1], resA[0], resB[1], resB[0], '.', x, y, z )    
  # end drawLatLonLine

  def drawLines( self, x, y, z ):
    for shape in self.kmlShapes.items():
      shape = shape[1]
      points = shape["POINTS"]
      last_point = points[0]
      for point in shape["POINTS"][1:]:
        self.drawLatLonLine( last_point.lat,last_point.lon,point.lat,point.lon, x, y, z );
        last_point = point
  #end showLine

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

  def pixelIsShown( self, px, py ):
    self.mainWinMaxY, self.mainWinMaxX = self.mainWin.getmaxyx()
    if px > 0 and px < self.mainWinMaxX and py > 0 and py < self.mainWinMaxY:
      return true
    return false;
  # end pixelIsShown


# end class KMLTileMap

if __name__=="__main__":
  #def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl ):
  T = KMLTileLoader((55,55),  "us_states.kml", "test_cache", 0 )
  print T.getTile( 1,2,3 )
