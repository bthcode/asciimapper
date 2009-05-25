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


What the?
--------

MapViewer is a curses based TMS tile viewer.  Think about that for
 a minute.  

Why?  Because it was there.

Where do you get your tiles?  The default is openstreetmap.org.  
  (It's hardcoded in AsciiMapTiler.py - replace the baseUrl to go to
   a different TMS server)

License:
-------

BSD - Have fun with it.  Let me know if you do something cool.

Requirements:
------------

1. Python
2. jp2a
3. Imagemagick convert

 Your distro should have come with python.  The others you may have to 
  install:

 Getting the requirements on RPM based distros:
  sudo yum install jp2a
  sudo yum install imagemagick

 Getting the requirements on Debian / Ubuntu:
  sudo apt-get install jp2a
  sudo apt-get install imagemagick

 Getting the requirements on Windows:
  I have no idea.  Seems hard to me.

Running it:
----------

python MapViewer.py
