#!/usr/bin/env python3
################################################################################
# processSST.py
# Mark Setchell
#
# Process UK Met Office Hadley Centre Sea Surface Temperature datasets
# https://www.metoffice.gov.uk/hadobs/hadisst/data/download.html
#
# Usage:
#    processSST.py filename
#
# The main objectibve is to read the data into a Python dictionary, with the 
# month as the key and the data being a Numpy array 180x360 of uint16 data.
#
# For added fun, the data are also saved (uninterpreted) as a signed 16-bit
# TIFF file and as a colour-interpreted PNG file.
################################################################################

import sys
import numpy as np

if __name__ == '__main__':

    # Check user has specified a file
    if len(sys.argv) != 2:
        sys.exit("Usage: processSST.py file")

    # Open file and read header line and data
    filename = sys.argv[1]

    # Create dict of each month's data, keyed by month number
    months = {}
    with open(filename,'r') as f:
        while True:
            line = f.readline()
            length = len(line)
            if length <1:
                # Break on empty line
                break
            elif length < 50:
                # Assume short lines are DMY header lines
                (D, M, Y, *_) = line.split()
                DMY = D + '-' + M + '-' + Y
                print(f'Date: {DMY}')
                # Create Numpy array to hold this month's data
                na = np.zeros((180,360), dtype=np.int16)
                months[M] = na
                r = 0
            else:
                # Assume normal, long data line
                for c in range(360):
                    months[M][r,c]  = int(line[6*c:6*c+6])
                r += 1

    # Rest of file generates images
    # If unwanted, comment out by placing triple quotes on next line and last line of file
    # The raw TIFF is directly comparable to the input data and stored in an int16 greyscale TIFF
    # The RGB image is interpreted as follows:
    #    -32768 = black (land)
    #    -1000  = white (ice)
    #    -500..3000 (-5 to +30 degrees) is mapped to a blue-red linear gradient

    from tifffile import imsave
    from PIL import Image

    # Create palette, 0=black, 1=white, 2-255 vary from blue to red
    palette = [0,0,0, 255,255,255]
    for e in range(2,256):
       palette.append(e)     # red
       palette.append(0)     # green
       palette.append(255-e) # blue

    # Iterate, by month, over the data we found
    for month, na in months.items():
        # Pad month to 2 digits
        if len(month) < 2:
            month = '0' + month
        DMY = '01-' + month + '-' + Y
        rawname = DMY + '-raw.tif'
        rgbname = DMY + '-RGB.png'
        print(f'Saving: {rawname} and {rgbname}')

        # Save greyscale TIFF with identical values to the data in file
        imsave(rawname, na, photometric='minisblack')

        # Make a palettised PIL image from the Numpy array
        copy = na.copy().astype(np.float)/100.00
        copy += 5
        copy *= 253.0/35.00
        copy += 2             # because palette entries 0 and 1 are black and white
        copy  = np.clip(copy,2,255).astype(np.uint8)
        copy[na==-32768] = 0  # Make land black by setting index=0
        copy[na==-1000]  = 1  # Make ice white by setting index=1
        im = Image.fromarray(copy, mode='P')
        im.putpalette(palette)
        im.save(rgbname)


