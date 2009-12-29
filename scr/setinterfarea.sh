#!/bin/bash
###############################################
###############################################
# setinterfarea.sh
# Part of Adore Project
# Batuhan Osmanoglu, Aug 2007 CSTARS, Miami
#
#
# This function reads the master.res file and 
# dumps first-last line, first last pixel.
#
# Calculation is simply done by:
# LINELO = FirstLine + Line Margin
# LINEHI = LastLine - Line Margin
# ... and so on.
#
# Requires:
#	- Master.res file location
#	- Line Margin
#	- Pixel Margin
# Provides:
#	- LINELO LINEHI PIXELLO PIXELHI
#
###############################################
###############################################

MasterRes=$1
LineMargin=$2
PixelMargin=$3

LINELO=`echo $(($(grep "First_line" ${MasterRes}   |grep -v "^#" |tail -n1 | cut -f2 -d: | tr -d [:blank:]) + ${LineMargin}))`
LINEHI=`echo $(($(grep "Last_line" ${MasterRes}    |grep -v "^#" |tail -n1 | cut -f2 -d: | tr -d [:blank:])  - ${LineMargin}))`
PIXELLO=`echo $(($(grep "First_pixel" ${MasterRes} |grep -v "^#" |tail -n1 | cut -f2 -d: | tr -d [:blank:]) + ${PixelMargin}))`
PIXELHI=`echo $(($(grep "Last_pixel" ${MasterRes}  |grep -v "^#" |tail -n1 | cut -f2 -d: | tr -d [:blank:])  - ${PixelMargin}))`

echo $LINELO $LINEHI $PIXELLO $PIXELHI
