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

false = 0
true = 1

class AsciiTileMap( TileMap ):
  def __init__(self, (x,y,z), (sizeX, sizeY), url, cacheUrl ):
    TileMap.__init__( self, (x,y,z), (sizeX, sizeY), cacheUrl )
    self.baseUrl      = url
    self.mapChars     = "....,;clodxkO.XNOM"
  # end __init__

  def getTile( self, x, y, z ): 
        txtFile = self.cacheUrl + "/%s/%s/%s.txt" % ( z,x,y )
        jpgFile = self.cacheUrl + "/%s/%s/%s.jpg" % ( z,x,y )
        cmd = """jp2a --size=%sx%s --chars="%s" %s > %s""" % (self.sizeX, self.sizeY, self.mapChars, jpgFile, txtFile )
        os.popen( cmd )
        f = open( txtFile, "r" )
        self.loadedTiles[ (x,y,z) ] = [ string.strip(line) for line in f.readlines() ]
        f.close()
  #end getMap

# end class AsciiTileMap
