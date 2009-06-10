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
from TileUtils import TileUtils

debug  = 1
false  = 0
true   = 1

class TileLoader:
  def __init__(self, (sizeX, sizeY), cacheUrl ):
    self.cacheUrl    = cacheUrl
    self.sizeX       = sizeX
    self.sizeY       = sizeY
    self.isActive    = true
    self.loadedTiles = {}
    self.tileUtils    = TileUtils()
  # end __init__

  def activate( self ):
    self.isActive = true
  # end activate

  def deactivate( self ):
    self.isActive = false
  # end deactivate

  def loadTileFromDisk( self, x,y,z ):
    fname = self.getFileName( x,y,z )
    lines = [ string.strip( line ) for line in open( fname, "r" ).readlines()  ]
    tile = []
    for line in lines:
      arr = []
      for c in line:
        arr.append( c )
      tile.append( arr )  
    return tile
  # end loadTileFromDisk

  def writeTileToDisk( self, x,y,z ):
    """ Write a tile to the correct place in cache """
    tileArr = self.loadedTiles[ (x,y,z) ]
    self.createDir( x,y,z )
    fname = self.getFileName( x,y,z )
    fhandle = open( fname, "w" )
    for row_num in range( self.sizeY ):
      fhandle.write( string.join( tileArr[row_num],"" ) )
      fhandle.write( "\n" )
    fhandle.close()
  # end writeTileToDisk 

  def getTile( self, x,y,z ):
    if not self.isActive:
      return
    if self.loadedTiles.has_key( (x,y,z) ):
      if debug: print "found tile in memory"
      return self.loadedTiles[ (x,y,z) ]
    elif self.tileExists( x,y,z ) and self.tileIsCorrectSize( x,y,z ):
      if debug: print "tile exists and is correct size"
      self.loadedTiles[ (x,y,z) ] = self.loadTileFromDisk( x,y,z )
    else:
      if debug: print "generating tile"
      self.loadedTiles[ ( x,y,z) ] = self.fetchTile( x,y,z )
      self.writeTileToDisk( x,y,z )
  # end getTile

  def addTextToTile( self,pixX, pixY, text, tileArr ):
    #pos = self.sizeX * pixY + pixX
    pos = pixX - len( text )/2
    if debug:
      print "pixX = %s, len(text) = %s, pos = %s" % (pixX, len(text), pos)
    if pos < 0:
      pos = 0
    for c in text:
      tileArr[pixY][pos] = c
      pos = pos + 1
    return tileArr
  # end addTextToTile


  def fetchTile( self, x, y, z ): 
    """ This method must be implemented by the subclass - gets the tile from wherever it gets it """
    return self.getEmptyTile()
  #end getMap

  def tileExists( self, x, y, z ):
    fname = self.getFileName( x,y,z)
    if os.access( fname, os.R_OK ):
      return true
    else:
      if debug: print "tile does not exist"
      return false
  # end tileExists

  def tileIsCorrectSize( self, x, y, z ):
    fname = self.getFileName( x,y,z )
    lines = open( fname, "r" ).readlines()
    if len(lines) == self.sizeY and len( lines[0] ) == self.sizeX +1:
      return true
    else:
      if debug: print "tile is incorrect size"
      return false
  # end tileIsCorrectSize

  def getEmptyTile( self ):
    arr = []
    for y in range(self.sizeY):
        arr.append( [" "] * self.sizeX )	
    return arr
  # end getMepthTile

  def getFileName( self, x, y, z ):
    fname = self.cacheUrl + os.sep + str(z) + os.sep + str(x) + os.sep + str(y) + ".txt"
    return fname
  # end getFileName

  def createDir( self, x,y,z ):
    """ Creates directory if it doesn't exist """
    fname = self.getFileName( x,y,z)
    dirParts = string.split( fname, os.sep )[:-1]

    # relative v. absolute
    if fname[0] == os.sep:
      curdir   = os.sep
      dirParts = dirParts[1:]
    else:
      curdir = '.' + os.sep

    # recurse
    nextdir=''
    for dirname in dirParts:
      if nextdir == '':
        nextdir = curdir + dirname
      else:
        nextdir=nextdir+os.sep+dirname

      if debug:
        print "trying to make " + nextdir

      if dirname not in os.listdir(curdir):
        try:
          os.mkdir(nextdir)
        except:
          print "Couldn't make directory %s" % nextdir
          return
      curdir = nextdir
  # end createDir

# end class TileLoader

if __name__=="__main__":
	a = TileLoader( (24,24), "def" )
        a.getTile( 1,1,0 )
        a.getTile( 1,1,0 )
