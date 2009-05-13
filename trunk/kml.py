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
import string, sys

class Placemark:
  """ Data Holder for a Placemark """
  def __init__( self ):
    self.name = ""
    self.description = ""
    self.lat = None
    self.lon = None
  # end __init__

  def __repr__( self ):
    return "name: %s, desc: %s, coords: %s" % ( self.name, self.description, self.coords )
# end Placemark

class KML_Handler(ContentHandler):
    """ SAX Parser for getting placemark data (point only) out of a KML File """
    def __init__ (self):
        self.Placemarks           = []
        self.isCoordinatesElement = 0
        self.isPlacemarkElement   = 0
        self.isDescriptionElement = 0
        self.isNameElement        = 0
        self.isPointElement       = 0
        self.currentPlacemark     = None
    # end __init__
   
    def startElement(self, name , attrs):
        name = name.upper()
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
                elif name == 'COORDINATES':
                    if self.isPointElement == 1: 
                        self.isCoordinatesElement = 1
                        self.coordinates = ""
    # end startElement

    def characters (self, ch):
        if self.isPlacemarkElement == 1:
          if self.isDescriptionElement == 1:
              self.description = ch
          elif self.isNameElement == 1:
              self.name = ch
          elif self.isCoordinatesElement == 1: # only true if it's also a point element
              self.coordinates = self.coordinates + ch
        else:
          pass
    # end characters

    def endElement(self, name):
        name = name.upper()
        if name == "PLACEMARK":
            self.isPlacemarkElement = 0
            self.Placemarks.append( self.currentPlacemark )
            self.currentPlacemark = None
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
                if self.isCoordinatesElement == 1:
                    self.isCoordinatesElement = 0
                    coords = [ float(x) for x in string.split ( string.lstrip( string.strip( self.coordinates)), "," ) ]
                    self.currentPlacemark.lon = coords[0]
                    self.currentPlacemark.lat = coords[1]
                    self.coordinates = ""
            elif name == "POINT":
                self.isPointElement = 0
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
  fname = sys.argv[1]
  reader = kmlReader( fname )
  for c in reader.getCoordinates():
    print c.coords
