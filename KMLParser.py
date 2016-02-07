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

""" Simple kml parser.  Pulls Placemarks with Point data out of a KML file """

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import string, sys, StringIO

class Point:
  """ Data Holder for a point """
  def __init__( self ):
    self.lat = None
    self.lon = None
  # end __init__

  def __repr__( self ):
    return "lat: %s, lon: %s" % ( self.lat, self.lon )
  # end __repr__

# end class Point

class LinearRing:
  """ Data Holder for a Linear Ring """
  def __init__( self ):
    self.points = []
  # end __init__

  def addPoint( self, lat, lon ):
    p = Point()
    p.lat = lat
    p.lon = lon
    self.points.append( p )
  # end addPoint

  def __repr__( self ):
    s = ""
    for p in self.points:
      s = s + "%s\n" % p
    return s
# end class Linear Ring

class Placemark:
  """ Data Holder for a Placemark """
  def __init__( self ):
    self.name            = ""
    self.description     = ""
    self.point           = None
    self.linear_ring     = None
    self.has_point       = 0
    self.has_linear_ring = 0
  # end __init__

  def setPoint( self, lat, lon ):
    self.point = Point()
    self.point.lat = lat
    self.point.lon = lon
    self.has_point = 1
  # end setCoordinates

  def addLinearRingPoint( self, lat, lon ):
    if not self.linear_ring:
      self.linear_ring = LinearRing()
      self.has_linear_ring = 1
    self.linear_ring.addPoint( lat, lon )
  # end addLinearRingPoint

  def __repr__( self ):
    return "name: %s, desc: %s, point: %s, linear_ring: %s" % ( self.name, self.description, self.point, self.linear_ring )
# end Placemark

class KML_Handler(ContentHandler):
    """ SAX Parser for getting placemark data (point only) out of a KML File """
    def __init__ (self):
        self.Placemarks                = []
        self.isPointCoordsElement      = 0
        self.isLinearRingCoordsElement = 0
        self.isPlacemarkElement        = 0
        self.isDescriptionElement      = 0
        self.isNameElement             = 0
        self.isPointElement            = 0
        self.isLinearRingElement       = 0
        self.currentPlacemark          = None
        self.isSchemaElement           = 0
    # end __init__
   
    def startElement(self, name , attrs):
        name = name.upper()
        if name == "SCHEMA":
            self.isSchemaElement    = 1
        if name == 'PLACEMARK':
            self.isPlacemarkElement = 1
            self.currentPlacemark = Placemark()
        else: 
            if self.isPlacemarkElement == 1:
                if name == 'DESCRIPTION':
                    self.isDescriptionElement = 1
                    self.description = ""
                elif name == 'NAME':
                    self.isNameElement = 1
                    self.name = ""
                elif name == "POINT":
                    self.isPointElement = 1
                elif name == "LINEARRING":
                    self.isLinearRingElement = 1
                elif name == 'COORDINATES':
                    if self.isPointElement == 1: 
                        self.isPointCoordsElement = 1
                        self.point_coordinates = ""
                    elif self.isLinearRingElement == 1:
                        self.isLinearRingCoordsElement = 1
                        self.linear_ring_coordinates = ""
    # end startElement

    def characters (self, ch):
        if self.isPlacemarkElement == 1:
          if self.isDescriptionElement == 1:
              self.description = ch
          elif self.isNameElement == 1:
              self.name = ch
          elif self.isPointCoordsElement == 1: # only true if it's also a point element
              self.point_coordinates = self.point_coordinates + ch
          elif self.isLinearRingCoordsElement == 1: # only true if it's also a linear ring element
              self.linear_ring_coordinates = self.linear_ring_coordinates + ch
        else:
          pass
    # end characters

    def endElement(self, name):
        name = name.upper()
        if name == "PLACEMARK":
            self.isPlacemarkElement = 0
            self.Placemarks.append( self.currentPlacemark )
            self.currentPlacemark = None
        elif name == "SCHEMA":
            self.isSchemaElement = 0
        if self.isPlacemarkElement:
            if name == 'DESCRIPTION':
                self.isDescriptionElement = 0
                self.currentPlacemark.description = self.description 
                self.description = ""
            elif name == 'NAME':
                self.isNameElement = 0
                self.currentPlacemark.name = self.name
                self.name = ""
            elif name == 'COORDINATES':
                if self.isPointCoordsElement == 1:
                    self.isPointCoordsElement = 0
                    coords = [ float(x) for x in string.split ( string.lstrip( string.strip( self.point_coordinates)), "," ) ]
                    self.currentPlacemark.setPoint( coords[1], coords[0] )
                    self.point_coordinates = ""
                elif self.isLinearRingElement == 1:
                    self.isLinearRingElement = 0
                    reader = StringIO.StringIO( self.linear_ring_coordinates )
                    coords = []
                    for line in reader.readlines():
                        line = string.strip( line )
                        if len(line):
                          coords = [ float(x) for x in string.split ( string.lstrip(  line ), "," ) ]
                          self.currentPlacemark.addLinearRingPoint( coords[1], coords[0] )
                    self.linear_ring_coordinates = ""
            elif name == "POINT":
                self.isPointElement = 0
            elif name == "LINEARRING":
                self.isLinearRingElement = 0
            else:
                 pass
    # end endElement
        
# end KML_Handler


class kmlReader:
  """ Class to read and provide access to data  in a kml file """
  def __init__( self, fname ):
    self.filename = fname
    self.parser = make_parser()   
    self.parser.setContentHandler(KML_Handler())
    self.parser.parse(fname)
  # end __init__

  def getCoordinates( self ):
    """ Get a vector of Placemark structures from a kml file """
    return self.parser.getContentHandler().Placemarks
  # end getPlacemarks

# end class kmlReader

if __name__=="__main__":
  import argparse
  parser = argparse.ArgumentParser('')
  parser.add_argument('filename')
  args = parser.parse_args()
  fname = args.filename
  reader = kmlReader( fname )
  for c in reader.getCoordinates():
    #print c.name, c.point.lat, c.point.lon
    print c
