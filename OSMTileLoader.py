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
from Wget import *
from TileMap import TileMap
from TileLoader import TileLoader
import img_to_aa

false = 0
true = 1

class OSMTileLoader( TileLoader):
  def __init__(self, (sizeX, sizeY), url, cacheUrl ):
    TileLoader.__init__( self, (sizeX, sizeY), cacheUrl )
    self.baseUrl      = url
    self.mapChars     = "....,;clodxkO.XNOM"
  # end __init__

  def fetchTile( self, x, y, z ): 
    tileArr = self.getEmptyTile()
    pngFile = self.cacheUrl + "/%s/%s/%s.png" % ( z,x,y )
    url = self.baseUrl + "/%s/%s/%s.png" % ( z,x,y )
    args = [ '-x', url ]
    wget( args )

    # convert to ascii
    row_ctr = 0
    col_ctr = 0
    img_text = img_to_aa.load_and_scale_image( pngFile, self.mapChars, width=self.sizeX, height=self.sizeY, grayscale=True ) 
    for line in img_text:
        for c in line:
            tileArr[ row_ctr ][ col_ctr ] = c
            col_ctr = col_ctr+1
        row_ctr = row_ctr + 1
        col_ctr = 0
    return tileArr
  #end getMap

# end class OSMTileLoader

if __name__=="__main__":
  #def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl ):
  T = OSMTileLoader((55,55),  "http://tile.openstreetmap.org", "tile.openstreetmap.org" )
  print T.getTile( 0,0,1 )
