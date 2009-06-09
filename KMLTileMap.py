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
from TileMap import TileMap
import KMLParser

false = 0
true = 1

class KMLTileMap( TileMap ):
  def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl, zoomlevel ):
    TileMap.__init__( self, (x,y,z), (sizeX, sizeY), cacheUrl )
    self.zoomLevel    = zoomlevel # minzoomlevel
    self.kmlFile      = kmlFile
    self.kmlPoints    = {}
    self.kmlShapes    = {}
    self.initKML()
  # end __init__

  def getTile( self, x, y, z ):
    pass
  # end getTile

  def createTile( self, x, y, z ):
    tileStr = self.getEmptyTile()
    for key, value in self.kmlPoints.items():
      lat = float( value[ "LAT" ] )
      lon = float( value[ "LON" ] )
      # returns None if point does not intersect
      res = self.latlon2pixel( value["NAME" ], lat, lon, z )

      # TODO: This logic relies on error handling to determine whether
      #       a point is "onscreen" - do something better
      if res != None:
          pixX, pixY = res[0], res[1]
          tileStr = self.addTextToTile( pixX, pixY, value[ "NAME" ], tileStr )
    self.saveTileToCache( x, y, z, tileStr )
  # end createTile

  def addTextToTile( self,pixX, pixY, text, tileStr ):
    pos = self.sizeX * pixY + pixX
    for c in text:
      tileStr[pos] = c
    return text
  # end addTextToTile

  def getEmptyTile( self ):
    return [" "] * ( ( self.sizeX ) * ( self.sizeY ) )
  # end getMepthTile

  def saveTileToCache( self, x, y, z, tileStr ):
    fname = self.cacheUrl+ "/%s/%s/%s.txt" % ( z,x,y )
    f = open( fname, "w" )
    f.write( tileStr ) # BTH - not right
    f.close() 
  # end saveTileToCache

  def loadTileFromCache( self ):
    pass
  # end loadTileFromCache

  def makeFakeTile( self, fname ):
    a = open( fname, "w" )
    for i in range ( self.sizeY ):
      s = [ " " ] * self.sizeX
      for j in range( self.sizeX ):
        if j%5 == 0:
          s[j] = "x"
      a.write( string.join( s, "" ) )
      a.write( "\n" )
    a.close()
  # end makeFakeFile

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


# end class KMLTileMap

if __name__=="__main__":
  #def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl ):
  T = KMLTileMap((1,1,0), (256,256),  "us_states.kml", "test_cache", 0 )
  T.createTile( 0,0,1 )
