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

false = 0
true = 1

class TileUtils:
  def __init__(self):
    # For coordinate conversions
    self.mapLoaded    = false
    self.tileSize     = 256
    self.originShift  = 2 * math.pi * 6378137 / 2.0
    self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
    self.tileLoaders  = []
  # end __init__

  #### Begin borrowed from maptiler ###

  def LatLonToMeters(self, lat, lon ):
    "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"

    mx = lon * self.originShift / 180.0
    my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)

    my = my * self.originShift / 180.0
    return mx, my
  # end LatLonToMeters

  def PixelsToMeters(self, px, py, zoom):
    "Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"

    res = self.Resolution( zoom )
    mx = px * res - self.originShift
    my = py * res - self.originShift
    return mx, my
  # end PixelsToMeters
    
  def MetersToPixels(self, mx, my, zoom):
    "Converts EPSG:900913 to pyramid pixel coordinates in given zoom level"
        
    res = self.Resolution( zoom )
    # orig:
    px = (mx + self.originShift) / res
    py = (my + self.originShift) / res
    return px, py
  # end MetersToPixels
  
  def Resolution(self, zoom ):
    "Resolution (meters/pixel) for given zoom level (measured at Equator)"
    
    # return (2 * math.pi * 6378137) / (self.tileSize * 2**zoom)
    return self.initialResolution / (2**zoom)
  # end Resolution

  def PixelsToTile(self, px, py):
    "Returns a tile covering region in given pixel coordinates"

    tx = int( math.ceil( px / float(self.tileSize) ) - 1 )
    ty = int( math.ceil( py / float(self.tileSize) ) - 1 )
    return tx, ty
  # end PixelsToTile


  #### End borrowed from maptiler ###

  def TileToWest( self, (x,y,z)  ):
    "Returns a tile west of the tile specified by x,y,z"
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    north_resolution = abs( abs( north ) - abs( south ) )
    east_resolution = abs( abs( east ) - abs( west ) )
    # don't go west past the end of the map
    if ( west - ( east_resolution/2 ) ) < -189:
      return x,y,z
    newx, newy = self.LatLonToTile( (north+south)/2, west - ( east_resolution/2 ) , z )
    return newx, newy, z
  # end TileToWEst
  
  def TileToEast( self, (x,y,z) ):
    "Returns a tile east of the tile specified by x,y,z"
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    north_resolution = abs( abs( north ) - abs( south ) )
    east_resolution = abs( abs( east ) - abs( west ) )
    # don't go east past end of map
    if ( east + ( east_resolution/2 ) ) > 189:
      return x,y,z
    newx, newy = self.LatLonToTile( (north+south)/2, east + (east_resolution/2 ), z )
    return (newx, newy, z)
  # end TileToEast
  
  def TileToNorth( self, (x,y,z) ):
    "Returns a tile north of the tile specified by x,y,z"
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    north_resolution = north - south 
    east_resolution =  east - west 
    # don't go past the north pole
    new_north = north + north_resolution/2
    if ( new_north ) > 86:
      new_north = 85
    newx, newy = self.LatLonToTile( new_north, (east+west)/2, z )
    return (newx, newy,z)
  # end TileToNorth
  
  def TileToSouth( self, (x,y,z) ):
    "Returns a tile west of the tile specified by x,y,z"
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    north_resolution = abs( abs( north ) - abs( south ) )
    east_resolution = abs( abs( east ) - abs( west ) )
    # don't go past the north pole
    new_south = south - north_resolution/2
    if ( new_south ) < -85:
      new_south = -85
    newx, newy = self.LatLonToTile( new_south, (east+west)/2, z )
    return (newx, newy,z)
  # end TileToSouth
  
  def TileZoomedOut( self, (x,y,z) ):
    "Returns a tile west of the tile specified by x,y,z"
    if z <= 1:
      return x,y,z 
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    # 1. Expand, but check for boundary conditions
    z = z-1
    newx, newy = self.LatLonToTile( north , west, z )
    return newx, newy, z
  # end TileUp
  
  def TileZoomedIn( self, (x,y,z) ):
    "Returns a tile west of the tile specified by x,y,z"
    if z >= 18:
      return x,y,z
    north, south, east, west  = self.TileToBoundingBox(x, y, z)
    z = z+1
    tl_x, tl_y = self.LatLonToTile( north , west, z )
    (newx, newy, z) = self.TileToSouth( self.TileToEast( (tl_x, tl_y, z) ) )
    return (newx, newy,z)
  # end TileDown

  def LatLonToTile(self, lat_deg, lon_deg, zoom):
    lat_rad = lat_deg * math.pi / 180.0
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return(xtile, ytile)
  # end LatLonToTile
  
  def TileToLatLon(self, xtile, ytile, zoom):
    n = 2.0 ** zoom
    min_lon_deg = xtile / n * 360.0 - 180.0
    min_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    min_lat_deg = min_lat_rad * 180.0 / math.pi
  
    max_lon_deg = (xtile+1) / n * 360.0 - 180.0
    max_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (ytile+1) / n)))
    max_lat_deg = max_lat_rad * 180.0 / math.pi
    return(lat_deg, lon_deg)
  # end TileToLatLon
  
  def TileToBoundingBox(self, x, y, z):
    north = self.tile2lat(y, z)
    south = self.tile2lat(y + 1, z)
    west = self.tile2lon(x, z)
    east = self.tile2lon(x + 1, z)
    return (north,south,east,west)
  # end tile2boundingbox
  
  def tile2lon(self, x, z):
    return ( (x / math.pow(2.0, z) * 360.0) - 180 )
  # end tile2lon
  
  def tile2lat(self, y, z):
    n = math.pi - ((2.0 * math.pi * y) / math.pow(2.0, z));
    return ( 180.0 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n))) )
  # end tile2lat

  def latlon2pixel( self, name, lat_deg, lon_deg, sizeX, sizeY, x,y,z ):
    meters_x, meters_y = self.LatLonToMeters( lat_deg, lon_deg )
    pixels_x, pixels_y = self.MetersToPixels( meters_x, meters_y, z )
    tile_x, tile_y     = self.PixelsToTile( pixels_x, pixels_y )

    # NOTE: pixels are counted from [0,0] = bottom left - 
    #       therefore, y has to be refigured out

    pixels_x_scaled = ( pixels_x  * (sizeX) / 256 ) # scale
    pixels_y_scaled = ( pixels_y  * (sizeY) / 256 ) # scale

    total_pixels_y  = sizeY * ( 2 << (z-1) ) 
    pixels_y_inv    = total_pixels_y - pixels_y_scaled 

    pixels_x_r = int( pixels_x_scaled - (x*sizeX)  )
    pixels_y_r = int( pixels_y_inv - (y*sizeY)  )

    return int(pixels_x_r), int(pixels_y_r)
  # end latlon2pixel
    

# end class TileMap
