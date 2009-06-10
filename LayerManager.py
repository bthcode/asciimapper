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

import sys, os, string, random, math
import pprint

from TileLoader import TileLoader
from OSMTileLoader import OSMTileLoader
from KMLTileLoader import KMLTileLoader
from TileUtils import TileUtils

false = 0
true = 1

class LayerManager:
  def __init__(self, (x,y,z), (sizeX, sizeY) ):
    self.tileStr      = None
    self.x            = x 
    self.y            = y
    self.z            = z
    self.isLoaded     = 0
    self.sizeX        = sizeX
    self.sizeY        = sizeY
    self.curMap       = ""
    # These get you the tile maps
    self.tileMaps     = {}
  # end __init__
   
  def zoomIn( self ):
    new_x, new_y, new_z = self.TileZoomedIn( (self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end zoomIn

  def zoomOut( self ):
    new_x, new_y, new_z = self.TileZoomedOut( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    # we have to have room to the east and south
    new_x2, new_y2, new_z2 = self.TileToEast( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.TileToWest( (new_x, new_y, new_z) )
    new_x2, new_y2, new_z2 = self.TileToSouth( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.TileToNorth( ( new_x, new_y, new_z ) )
      
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end zoomOut

  def moveEast( self ):
    new_x, new_y, new_z = self.TileToEast( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    new_x2, new_y2, new_z2 = self.TileToEast( (new_x, new_y, new_z) )
    if ( new_x2, new_y2, new_z2 ) == (new_x, new_y, new_z):
      return
    else:
      self.x = new_x
      self.y = new_y
      self.z = new_z
  # end moveEast

  def moveWest( self ):
    new_x, new_y, new_z = self.TileToWest( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
    pass
  # end moveWest

  def moveNorth( self ):
    new_x, new_y, new_z = self.TileToNorth( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end moveNorth

  def moveSouth( self ):
    new_x, new_y, new_z = self.TileToSouth( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    new_x2, new_y2, new_z2 = self.TileToSouth( (new_x, new_y, new_z) )
    if ( new_x2, new_y2, new_z2 ) == (new_x, new_y, new_z):
      return
    else:
      self.x = new_x
      self.y = new_y
      self.z = new_z
  # end moveNorth

  def moveToPoint( self, lat, lon, zoom ):
    if zoom < 1 or zoom > 18:
      return
    if lat < -85 or lat > 85:
      return
    if lon < -180 or lon > 180:
      return
    new_x, new_y = self.LatLonToTile( lat, lon, zoom)
    new_z = zoom
    # we have to have room to the east and south
    new_x2, new_y2, new_z2 = self.TileToEast( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.TileToWest( (new_x, new_y, new_z) )
    new_x2, new_y2, new_z2 = self.TileToSouth( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.TileToNorth( ( new_x, new_y, new_z ) )
      
    self.x = new_x
    self.y = new_y
    self.z = new_z

  # end moveToPoint

  def getMap( self ):
    """ Get four tiles - x,y,z points to north west corner of north west tile """
    if self.mapLoaded:
      return self.curMap

    x = self.x
    y = self.y
    z = self.z

    self.curMap = ""

    # 1. Figure out which tiles we want
    topLeft     = ( (x,y,z) )
    topRight    = self.TileToEast( topLeft )
    bottomLeft  = self.TileToSouth( topLeft )
    bottomRight = self.TileToEast( bottomLeft )

    # 2. Load them into memory if they're not already there
    self.getMapTile( topLeft )
    self.getMapTile( topRight )
    self.getMapTile( bottomLeft )
    self.getMapTile( bottomRight )


    topLeft_map     = self.loadedTiles[ topLeft     ]
    topRight_map    = self.loadedTiles[ topRight    ]
    bottomLeft_map  = self.loadedTiles[ bottomLeft  ]
    bottomRight_map = self.loadedTiles[ bottomRight ]

    # 3. now put them together
    for i in range( len( topLeft_map ) ):
        self.curMap = self.curMap + topLeft_map[i] + topRight_map[i] + "\n"
    for i in range( len( bottomLeft_map ) ):
        self.curMap = self.curMap + bottomLeft_map[i] + bottomRight_map[i] + "\n"

    return self.curMap
  #end getMap

############# Tile Loader Registration ####################
  def addTileLoader( self, name, loader ):
    pass
  # end addTileLoader

  def delTileLoader( self, name ):
    pass
  # end delTileLoader

  def activateTileLoader( self, name ):
    pass
  # end activateTileLoader

  def deActivateTileLoader( self, name ):
    pass
  # end deActivateTileLoader
############# Tile Loader Registration ####################

# end class TileMap

if __name__=="__main__":
	L = LayerManager( (0,0,0), (56,56) )
