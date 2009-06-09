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

debug  = 1
false  = 0
true   = 1

class TileLoader:
  def __init__(self, (sizeX, sizeY), url, cacheUrl ):
    self.cacheUrl = cacheUrl
    self.sizeX    = sizeX
    self.sizeY    = sizeY
    self.baseUrl  = url
    self.isActive = true
  # end __init__

  def activate( self ):
    self.isActive = true
  # end activate

  def deactivate( self ):
    self.isActive = false
  # end deactivate

  def fetchTile( self, x, y, z ): 
    pass
  #end getMap

  def tileExists( self, x, y, z ):
    pass
  # end tileExists

  def tileIsCorrectSize( self, x, y, z ):
    pass
  # end tileExists

  def cacheTile( self, x, y, z ):
    pass
  # end cacheTile

  def createDir( self, dirStr ):
    """ Creates directory if it doesn't exist """
    fname = dirStr
    dirParts = string.split( fname, os.sep )

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
	a = TileLoader( (24,24), "abc", "def" )
        a.createDir( "a/b/c")
        a.createDir( "/tmp/a/b/c" )
