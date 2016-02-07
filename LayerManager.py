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
debug = 0

class LayerManager:
  ''' Holds all sub-layers, handles movement commands '''
  def __init__(self, (x,y,z), (sizeX, sizeY), grid_x ):
    self.grid_x       = grid_x
    self.tileStr      = None
    self.x            = x 
    self.y            = y
    self.z            = z
    self.isLoaded     = 0
    self.sizeX        = sizeX
    self.sizeY        = sizeY
    self.curMap       = ""
    self.mapLoaded    = false
    # Utils for finding tiles
    self.tileUtils    = TileUtils()
    # These get you the tile maps
    self.tileLoaders  = {}
    # Store the hybrid tiles in memory
    self.loadedTiles  = {}
  # end __init__
   
  def zoomIn( self ):
    new_x, new_y, new_z = self.tileUtils.TileZoomedIn( (self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end zoomIn

  def zoomOut( self ):
    new_x, new_y, new_z = self.tileUtils.TileZoomedOut( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    # we have to have room to the east and south
    new_x2, new_y2, new_z2 = self.tileUtils.TileToEast( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.tileUtils.TileToWest( (new_x, new_y, new_z) )
    new_x2, new_y2, new_z2 = self.tileUtils.TileToSouth( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.tileUtils.TileToNorth( ( new_x, new_y, new_z ) )
      
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end zoomOut

  def moveEast( self ):
    new_x, new_y, new_z = self.tileUtils.TileToEast( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    new_x2, new_y2, new_z2 = self.tileUtils.TileToEast( (new_x, new_y, new_z) )
    if ( new_x2, new_y2, new_z2 ) == (new_x, new_y, new_z):
      return
    else:
      self.x = new_x
      self.y = new_y
      self.z = new_z
  # end moveEast

  def moveWest( self ):
    new_x, new_y, new_z = self.tileUtils.TileToWest( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
    pass
  # end moveWest

  def moveNorth( self ):
    new_x, new_y, new_z = self.tileUtils.TileToNorth( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    self.x = new_x
    self.y = new_y
    self.z = new_z
  # end moveNorth

  def moveSouth( self ):
    new_x, new_y, new_z = self.tileUtils.TileToSouth( ( self.x, self.y, self.z) )
    if ( new_x, new_y, new_z ) != (self.x, self.y, self.z):
      self.mapLoaded = false  
    new_x2, new_y2, new_z2 = self.tileUtils.TileToSouth( (new_x, new_y, new_z) )
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
    new_x2, new_y2, new_z2 = self.tileUtils.TileToEast( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.tileUtils.TileToWest( (new_x, new_y, new_z) )
    new_x2, new_y2, new_z2 = self.tileUtils.TileToSouth( ( new_x, new_y, new_z) )
    if ( new_x, new_y, new_z) == ( new_x2, new_y2, new_z2 ):
      new_x, new_y, new_z = self.tileUtils.TileToNorth( ( new_x, new_y, new_z ) )
      
    self.x = new_x
    self.y = new_y
    self.z = new_z

  # end moveToPoint

  def getMap_orig( self ):
    """ Get four tiles - x,y,z points to north west corner of north west tile """
    if self.mapLoaded:
      return self.curMap

    x = self.x
    y = self.y
    z = self.z

    self.curMap = ''

    # 1. Figure out which tiles we want
    topLeft     = ( (x,y,z) )
    topRight    = self.tileUtils.TileToEast( topLeft )
    bottomLeft  = self.tileUtils.TileToSouth( topLeft )
    bottomRight = self.tileUtils.TileToEast( bottomLeft )

    # 2. Load the hybrid into memory if they're not already there
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
        self.curMap = self.curMap + string.join(topLeft_map[i],"") + string.join(topRight_map[i], "") + "\n"
    for i in range( len( bottomLeft_map ) ):
        self.curMap = self.curMap + string.join(bottomLeft_map[i],"") + string.join(bottomRight_map[i],"") + "\n"

    return self.curMap
  #end getMap

  def getMap( self ):
    """ Get four tiles - x,y,z points to north west corner of north west tile """
    if self.mapLoaded:
      return self.curMap

    x = self.x
    y = self.y
    z = self.z

    grid_x = self.grid_x

    self.curMap = ""

    topLeft     = ( (x,y,z) )
    prev = topLeft
    self.cur_tiles = [ [topLeft] ]
    for i in range( grid_x ):
        for j in range( grid_x ):
            nextTile = self.tileUtils.TileToEast( prev )
            self.cur_tiles[-1].append( nextTile )
            prev = nextTile
        nextTile = self.tileUtils.TileToSouth( self.cur_tiles[-1][0] )
        self.cur_tiles.append( [nextTile] )
        prev = nextTile
            
             

    # 1. Figure out which tiles we want
    for i in range( grid_x ):
        for j in range( grid_x ):
            self.getMapTile( self.cur_tiles[i][j] )


    self.cur_map_tiles = []
    for i in range( grid_x ):
        self.cur_map_tiles.append( [] )
        for j in range( grid_x ):
            self.cur_map_tiles[-1].append( self.loadedTiles[ self.cur_tiles[i][j] ] )


    for j in range( grid_x ):
        start_map = self.cur_map_tiles[j][0]
        for i in range( len( start_map ) ):
            line = ''
            for y in range( grid_x ):
                tmp_tile = self.cur_map_tiles[j][y]
                row = tmp_tile[i]
                line = line + string.join(row, '' )
 
            self.curMap = self.curMap + line + "\n"


    return self.curMap
  #end getMap

  def getEmptyTile( self, sizeX, sizeY ):
    arr = []
    for y in range(sizeY):
        arr.append( [" "] * sizeX )	
    return arr
  # end getEmptyTile

  def getMapTile( self, (x,y,z) ):
    if debug: print "getTileMap getting %s,%s,%s" % ( x,y,z )
    tile = self.getEmptyTile(self.sizeX, self.sizeY)
    keys = self.tileLoaders.keys()
    keys.sort()
    # 1. Iterate through higher layers adding non-transparent pixels
    for key in keys:
      if self.tileLoaders[ key ].isActive():
        tile_arr = self.tileLoaders[ key ].getTile( x,y,z )
        for row_num in range( len(tile_arr) ):
          for col_num in range( len(tile_arr[row_num]) ):
            c = tile_arr[ row_num ][ col_num ]
            if c != " ":
              tile[ row_num ][ col_num ] = c
    self.loadedTiles[ (x,y,z) ] = tile
  # end getMapTile
        
############# Tile Loader Registration ####################
  def addTileLoader( self, level, loader ):
    self.tileLoaders[ level ] = loader
  # end addTileLoader

  def delTileLoader( self, level ):
    self.tileLoaders.pop( level )
  # end delTileLoader

  def activateTileLoader( self, level ):
    self.tileLoaders[ level ].activate
  # end activateTileLoader

  def deActivateTileLoader( self, level ):
    self.tileLoaders[ level ].deactivate
  # end deActivateTileLoader
############# Tile Loader Registration ####################

# end class TileMap

if __name__=="__main__":
  L = LayerManager( (0,0,1), (56,56) )
  T = KMLTileLoader((56,56),  "us_states.kml", "test_cache", 0 )
  L.addTileLoader( 20, T )
  O = OSMTileLoader( (56,56), "http://tile.openstreetmap.org", "tile.openstreetmap.org" )
  L.addTileLoader( 10, O )
  t = L.getMap()
  print( t )
