#!/usr/bin/python

from PIL import Image
import sys
import logging
import string
 
def calc_rgb( redweight=0.2989, greenweight=0.5866, blueweight=0.1145):
    RED   = []
    GREEN = []
    BLUE  = []
    GRAY  = []
    for n in range(256):
		RED.append(float (n) * redweight)
		GREEN.append(float (n) * greenweight)
		BLUE.append(float (n) * blueweight)
		GRAY.append(float (n))
    return RED, GREEN, BLUE, GRAY
# end calc_rgb
 
def load_and_scale_image( url, ascii_chars,  width=None, height=None, grayscale=False ):
    ''' url : file to load
        width : target width 
        height : target height
        grayscale : convert to grayscale true/false
        [ return ] : image buffer
    '''

    # 0. Create jp2a palette
    RED, GREEN, BLUE, GRAY = calc_rgb()
    lx = len( ascii_chars ) -1
    flt_len = float( lx )
    lum_palette = []
    MAXJSAMPLE=255.
    for n in range(256):
		lum_palette.append( ascii_chars[int(round( flt_len * float(n) / float(MAXJSAMPLE)))] )

    # 1. Try to load the image
    try:
        img  = Image.open( url )
    except:
        logging.warn("Can't open image {0}".format( url ) )
        return None

    # 2. Calculate scaling
    output_width, output_height  = img.size

    logging.info("Image width = {0}, target height = {1}".format( output_width, output_height ))
    
    if width == None and height == None:
        # use image native width and height
        pass
    elif width == None and height != None:
        # scale using just height
        scale_factor = float(height) / output_height 
        output_width = int( output_width * scale_factor ) 
        output_height = height
    elif width != None and height == None:
        # scaling using just width
        scale_factor = float(width) / output_width
        output_height = int( output_height * scale_factor )
        output_width = width
        pass
    else:
        # scale using width and height
        output_height = height
        output_width  = width

    logging.info("Output width = {0}, target height = {1}".format( output_width, output_height ))

    # 3. Perform Re-scale
    new_image = img.resize((output_width, output_height))
    
	    # 4. Go to grayscale if desired

    if grayscale:
        logging.info( "Grayscale selected" )
        if new_image.mode != 'L':
            logging.info( "..converting to grayscale" )
            new_image = new_image.convert("L") # convert to grayscale
    else:
        logging.info ( "Grayscale not selected" )
        if new_image.mode != 'RGB':
            logging.info ( "..converting image to rgb" )
            new_image.convert( "RGB" ) 


    if grayscale:
        # 5A. Grayscale Loop
        image_as_ascii = []
        all_pixels = list(new_image.getdata())
        min_val    = 0
        max_val    = MAXJSAMPLE
        step       = float( max_val - min_val ) / float( len( ascii_chars )  )
        #logging.info( "min_val = {0}, max_val = {1}, step = {2}".format( min_val, max_val, step ) )

        
        for pixel_value in all_pixels:
            offset = pixel_value - min_val
            index  = int(offset / step)
            if index >= len( ascii_chars ):
                index = len(ascii_chars) - 1
            c = ascii_chars[index]
            #r, g, b, a = pixel_value
            #image_as_ascii.append( lum_palette[ int(RED[r] + GREEN[g] + BLUE[b])] )
            image_as_ascii.append(c)
    else:   
        # 5B. Color Loop
        print "color not implemented"

    # 6. Prepare output
    outstr = []
    for c in range(0, len(image_as_ascii), output_width):
        t = string.join(image_as_ascii[c:c+output_width], "" )
        outstr.extend([t])
    return outstr


# end load_and_scale_image
 
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser( 'JP2A in Python' )
    parser.add_argument( '--chars', action='store', help='Select characters to paint', default= '#A@%S+<*:,.' )
    parser.add_argument( '--colors', action='store_true', help='Use ANSI colors',  default=False )
    parser.add_argument( '--height', action='store', default=None, type=int )
    parser.add_argument( '--width', action='store', default=80, type=int )
    parser.add_argument( '--debug', action='store_true', help='Turn on more logging', default=False )
    parser.add_argument( 'url', action='store', help='url of image', default=None )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(filename='yy.log',level=logging.INFO)
        logging.info('Starting jp2a run' )


    grayscale = True
    if args.colors:
        grayscale = False

    outstr = load_and_scale_image( args.url, args.chars, width=args.width, height=args.height, grayscale=grayscale )
    
    for row in outstr:
        print row


