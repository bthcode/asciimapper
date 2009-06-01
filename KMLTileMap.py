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
  def __init__(self, (x,y,z), (sizeX, sizeY), kmlFile, cacheUrl ):
    TileMap.__init__( self, (x,y,z), (sizeX, sizeY), cacheUrl )
    self.kmlFile      = kmlFile
  # end __init__

  def getTile( self, x, y, z ):
    pass
  # end getTile

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
  # end loadKML


# end class KMLTileMap
