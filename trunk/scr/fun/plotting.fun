#!/bin/bash

function gnuplot_baseline(){
#  local parameterR
#  echo "Generating ${1}.ps"
#  parameterR=`minmax -I100/400 ${1}`
#  psxy -JX6.5i -R${parameterR} -Bg200a200:"Btemp [days]":/g200a200:"Bperp [m]":WSne:."Baselines": -K >  ${1}.ps  
#  cat ${1} | while read x y label
#  do
#    psxy -J -R -Sc0.125i -G0/0/0 -P -B -K < $x $y > ${1}.ps
#  done

#get x-range y-range
local xRange=`minmax -C ${1} | awk '{printf "%d:%d", $1-100, $2+100};'`
[ $? -ne 0 ] && return 1 
local yRange=`minmax -C ${1} | awk '{printf "%d:%d", $3-100, $4+100};'`
[ $? -ne 0 ] && return 1
local fonts="arial,20"
#DOWNLOADED FROM http://ilab.cs.byu.edu/cs360/ by Prof. Daniel Zappala
gnuplot <<_ENDOFSCRIPT
set title ""
set xlabel "Temporal Baseline [days]" font "arial,24"
set ylabel "Perpendicular Baseline [m]" font "arial,24"
##### output to a grayscale EPS file
set term postscript eps size 6,6 "Arial" 24
set output "${1}.eps"

##### output to a color EPS file
# set term postscript color eps
# set output "${1}.eps"

###### output to a PNG file:
# set term png
# set output "${1}.png"

###### output to a SVG file:
# set term svg
# set output "${1}.svg"

##### output to a PNG file with a white background, black for borders, dark
##### gray for axes, and a gray-scale for the six plotting colors.
# set terminal png enhanced xffffff x000000 x202020 x404040 x606060 \
#                           x808080 xA0A0A0 xC0C0C0 xE0E0E0
# set output "${1}.png"

##### set the x range
set xrange [${xRange}]
set yrange [${yRange}]

##### turn off the key
set nokey

# plot "${1}" using 1:2 with points

##### change the title
#plot "${1}" using 1:2:3 with labels title "Baseline Plot"

##### change the font size
plot "${1}" using 1:2:3 with labels rotate center font "${fonts}" title "Baseline Plot"

##### change the point type
#plot "${1}" using 1:2:3 with points pt 12 title "Baseline Plot"

##### change the point color
#plot "${1}" using 1:2 with points pt 12 lc 3 title "Baseline Plot"

##### change the point size
# plot "${1}" using 1:2 with points pt 12 ps 0.5 title "Baseline Plot"
_ENDOFSCRIPT
                            
}
