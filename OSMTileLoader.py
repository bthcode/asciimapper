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

false = 0
true = 1

class OSMTileLoader( TileLoader):
  def __init__(self, (sizeX, sizeY), url, cacheUrl ):
    TileLoader.__init__( self, (sizeX, sizeY), cacheUrl )
    self.baseUrl      = url
    self.mapChars     = "....,;clodxkO.XNOM"
  # end __init__

  def fetchTile( self, x, y, z ): 
    regenerate_map = 1
    pngFile = self.cacheUrl + "/%s/%s/%s.png" % ( z,x,y )
    jpgFile = self.cacheUrl + "/%s/%s/%s.jpg" % ( z,x,y )
    # if the jpgFile doesn't exist, check if the png does
    if not os.access( jpgFile , os.R_OK ):
        if not os.access( pngFile, os.R_OK ) :
            # png doesn't exist, try to download it
            url = self.baseUrl + "/%s/%s/%s.png" % ( z,x,y )
            #os.popen( "wget -q -x --timeout=2 %s" % url ) 
            args = [ '-x', url ]
            wget( args )
        if not os.access( pngFile, os.R_OK ):
            # no png after wget
            regenerate_map = 0
            self.loadedTiles[ (x,y,z) ] = self.getEmptyTile()
            return
        # now try to convert it
        os.popen( "convert %s %s" % ( pngFile, jpgFile ) )

    if regenerate_map: 
        txtFile = self.cacheUrl + "/%s/%s/%s.txt" % ( z,x,y )
        jpgFile = self.cacheUrl + "/%s/%s/%s.jpg" % ( z,x,y )
        cmd = """jp2a --size=%sx%s --chars="%s" %s > %s""" % (self.sizeX, self.sizeY, self.mapChars, jpgFile, txtFile )
        os.popen( cmd )
        f = open( txtFile, "r" )
        self.loadedTiles[ (x,y,z) ] = [ string.strip(line) for line in f.readlines() ]
        f.close()
  #end getMap

# end class OSMTileLoader

if __name__=="__main__":
  #def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl ):
  T = OSMTileLoader((55,55),  "http://tile.openstreetmap.org", "tile.openstreetmap.org" )
  print T.getTile( 0,0,1 )
