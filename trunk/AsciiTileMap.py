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

false = 0
true = 1

class AsciiTileMap:
  def __init__(self, (x,y,z), (sizeX, sizeY), url, cacheUrl ):
    self.tileStr      = None
    self.baseUrl      = url
    self.cacheUrl     = cacheUrl
    self.loadedTiles  = {}
    self.x            = x 
    self.y            = y
    self.z            = z
    self.isLoaded     = 0
    self.sizeX        = sizeX
    self.sizeY        = sizeY
    self.curMap       = ""
    # For coordinate conversions
    self.tileSize = 256
    self.originShift = 2 * math.pi * 6378137 / 2.0
    self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
    self.mapLoaded    = false #TODO how do I use this effectively?
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

  def getEmptyTile( self ):
    return "." * ( ( self.sizeX ) * ( self.sizeY ) )
  # end getMepthTile

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

  def isShown( self, lat, lon, z ):
    """ Returns true if this lat/lon point is in the current map """
    x,y = self.LatLonToTile( lat, lon, z )
    if x == self.x or x == self.x+1:
      if y == self.y or y == self.y+1:
        return 1
    return 0
  # end isShown

  def latlon2pixel( self, name, lat_deg, lon_deg, z ):
    #f = open( "debug.txt", "a" )
    if not self.isShown( lat_deg, lon_deg, z ):
      return None

    #M = globalmaptiles.GlobalMercator()
    meters_x, meters_y = self.LatLonToMeters( lat_deg, lon_deg )
    # BTH: It appears that this function is busted - meters_x,meters_y agrees with test code...
    pixels_x, pixels_y = self.MetersToPixels( meters_x, meters_y, z ) # how can this be bigger than 512?
    tile_x, tile_y     = self.PixelsToTile( pixels_x, pixels_y )

    # NOTE: pixels are counted from [0,0] = bottom left - 
    #       therefore, y has to be refigured out


    pixels_x_scaled = ( pixels_x  * (self.sizeX) / 256 ) # scale
    pixels_y_scaled = ( pixels_y  * (self.sizeY) / 256 ) # scale

    total_pixels_y  = self.sizeY * ( 2 << (z-1) ) 
    pixels_y_inv    = total_pixels_y - pixels_y_scaled 

    pixels_x_r = int( pixels_x_scaled - (self.x*self.sizeX)  )
    pixels_y_r = int( pixels_y_inv - (self.y*self.sizeY)  )

    #f.write( "--- %s ----\n" % name )
    #f.write( "zoom: %s\n" % z )
    #f.write( "lat: %s, lon: %s (lat=y)\n" % ( lat_deg, lon_deg) )
    #f.write( "meters_x: %s, meters_y: %s\n" % ( meters_x, meters_y ) )
    #f.write( "pixels_x: %s, pixels_y: %s\n" % ( pixels_x, pixels_y ) )
    #f.write( "total_pixels_y: %s, pixels_y_inv: %s\n" % ( total_pixels_y, pixels_y_inv ) )
    #f.write( "self.x: %s, self.y: %s\n" % ( self.x, self.y )         )
    #f.write( "self.sizeX: %s, self.sizeY: %s\n" % (self.sizeX, self.sizeY ) )
    #f.write( "tile_x: %s, tile_y: %s\n" % ( tile_x, tile_y )         )
    #f.write( "pixels_x_scaled: %s, pixels_y_scaled: %s\n" % ( pixels_x_scaled, pixels_y_scaled  ) )
    #f.write( "pixels_x_r: %s, pixels_y_r: %s\n" % ( pixels_x_r, pixels_y_r ) )
    #f.close()
    return int(pixels_x_r), int(pixels_y_r)
    
  # end latlon2pixel
    

  def old_latlon2pixel( self,name,lat_deg, lon_deg, z ):
    """ For a given zoom level, return tile x,y and pixel x,y """
    #f = open( "debug.txt", "a" )
    if self.isShown( lat_deg, lon_deg, z ):
      # 1. Get tile boundary information
      x, y       = self.LatLonToTile( lat_deg, lon_deg, z ) 
      north, south, east, west = self.TileToBoundingBox( x,y,z )
      north_span = north - south 
      east_span  = east - west 
      pct_lon = (lon_deg - west) / ( east_span * 1.0 )
      pct_lat = -1 * (lat_deg - north ) / ( north_span * 1.0 )
      # 2. Get the actual pixel - remember, we always show four tiles
      #       on screen
      xOffset = self.sizeX * (x - self.x ) # adds one tile width if needed
      yOffset = self.sizeY * (y - self.y ) # adds one tile height if needed
      
      pixY        = yOffset + int( pct_lat * self.sizeY )
      pixX        = xOffset + int( pct_lon * self.sizeX )
      #f.write( "--------------\n" )
      #f.write( "self.sizeX = %s, self.sizeY=%s\n" % ( self.sizeX, self.sizeY) )
      #f.write( "self.x=%s, self.y=%s, self.z=%s, x=%s, y=%s, z=%s\n" % (self.x, self.y, self.z, x, y, z) ) 
      #f.write( "lat_deg=%s, lon_deg=%s, north=%s, south=%s, east=%s, west=%s\n" % ( lat_deg, lon_deg, north, south, east, west) )
      #f.write( "north_span=%s, east_span=%s, pct_lat=%s, pct_lon=%s, pixX=%s, pixY=%s\n" % ( north_span,east_span,pct_lat, pct_lon, pixX, pixY ) )
      #f.close()
      return pixX, pixY 
    else:
      #f.close()
      return None
  # end old_latlon2pixel


  def getMapTile( self, (x,y,z) ):
    regenerate_map = 0
    # 1. See if the map is in memory
    if self.loadedTiles.has_key( (x,y,z) ):
      return
    # 2. If the map isn't in memory, see if there's a text file __of the right size__
    else:
      txtFile = self.cacheUrl + "/%s/%s/%s.txt" % ( z,x,y )
      # check if the next file exists
      if os.access( txtFile, os.R_OK ):
        f = open( txtFile, "r"  )
        mapstring = [ string.strip( line) for line in f.readlines() ]
        f.close()
        # need to regenerate text file because it's not the right size
        if len( mapstring ) !=  self.sizeY :
          regenerate_map = 1
        if len( mapstring[0] ) != self.sizeX :
          regenerate_map = 1

        # it's a good text file, just use it
        else:
          self.loadedTiles [ (x,y,z) ] = mapstring
      # text file doesn't exist or we can't read it
      else:
        regenerate_map = 1
        pngFile = self.cacheUrl + "/%s/%s/%s.png" % ( z,x,y )
        jpgFile = self.cacheUrl + "/%s/%s/%s.jpg" % ( z,x,y )
        # if the jpgFile doesn't exist, check if the png does
        if not os.access( jpgFile , os.R_OK ):
          if not os.access( pngFile, os.R_OK ) :
            # png doesn't exist, try to download it
            url = self.baseUrl + "/%s/%s/%s.png" % ( z,x,y )
            os.popen( "wget -q -x --timeout=2 %s" % url ) 
          if not os.access( pngFile, os.R_OK ):
            # no png after wget
            regenerate_map = 0
            self.loadedTiles[ (x,y,z) ] = self.getEmptyTile()
            return
          # now try to convert it
          os.popen( "convert %s %s" % ( pngFile, jpgFile ) )
      if regenerate_map: 
        jpgFile = self.cacheUrl + "/%s/%s/%s.jpg" % ( z,x,y )
        cmd = """jp2a --size=%sx%s --chars="....,;clodxkO.XNOM" %s > %s""" % ( self.sizeX, self.sizeY, jpgFile, txtFile )
        os.popen( cmd )
        f = open( txtFile, "r" )
        self.loadedTiles[ (x,y,z) ] = [ string.strip(line) for line in f.readlines() ]
        f.close()
  #end getMap

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

# end class AsciiTileMap
