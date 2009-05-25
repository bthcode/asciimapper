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

import sys, os, string, urllib2, getopt
import pprint

false = 0
true = 1

usage=\
"""
Startup:
  -V,  --version           display the version of Wget and exit.
  -h,  --help              print this help.

Logging and input file:
  -o,  --output-file=FILE    log messages to FILE.
  -d,  --debug               print lots of debugging information.
  -v,  --verbose             be verbose (this is the default).
  -x,  --force-directories        force creation of directories.
"""



def wget( opts ):

  version           = 0.1
  output_file       = sys.stdout
  debug             = false
  verbose           = false
  force_directories = false
  has_output_file   = false
  output_file_name  = "stdout"

  try:
    optlist, args = getopt.getopt( opts, 'Vhadqvixo:', ["version", "help", "output-file", "debug", "verbose", "force-directories"] )
  except getopt.GetoptError, e:
    print "Error: " + str(e)
    print usage
    return
  
  for o,a in optlist:
    if o in ['-V', "--version"]:
      print "wget.py version %s" % version
      return
    elif o in [ '-h', "--help" ]:
      print usage
      return
    elif o in [ '-d', "--debug" ]:
      debug=true
    elif o in [ '-v', "--verbose" ]:
      verbose=true
    elif o in [ '-x', "--force-directories" ]:
      if has_output_file:
        print "Select either -o OR -x"
        print usage
        return
      force_directories=true
    elif o in [ '-o', "--output-file" ]:
      if force_directories:
        print "Select either -o OR -x"
        print usage
        return
      has_output_file = true;
      if a == '':
        print "Please specify an output file\n\n" + usage
        return
      try:
        output_file_name = a
        output_file = open( a, "w" )
      except:
        print "Couldn't open output_file " + a
        return

  # end command line handling

  url = args[0]

  # begin getting the url
  if debug:
    print "Opening URL %s" % url

  try:
    handle = urllib2.urlopen( url )
  except:
    print "Problems opening %s" % url
    return

  if debug:
    print "Retreived %s" % url

  if force_directories:
    urlparts = string.split( url, "/" )
    dirparts = urlparts[2:-1]
    fname    = urlparts[-1]
    if debug: 
      print "Directories: " + pprint.pformat(dirparts)
      print "Filename: " + fname
    curdir='./'
    nextdir=''
    for dirname in dirparts:
      if nextdir == '':
        nextdir = dirname
      else:
        nextdir=nextdir+os.sep+dirname

      if dirname not in os.listdir(curdir):
        if debug:
          print "trying to make " + nextdir
        try:
          os.mkdir(nextdir)
        except:
          print "Couldn't make directory %s" % nextdir
          return
      curdir = nextdir

    try:
      output_file_name = curdir + os.sep + fname
      output_file = open( output_file_name, "w" )
    except:
      print "Couldn't open file %s" % output_file_name

    if debug:
      print "Writing to file %s" % output_file_name

    output_file.write( handle.read() )
    

  
      
# end wget function
  
if __name__=="__main__":
  wget( sys.argv[1:] )
