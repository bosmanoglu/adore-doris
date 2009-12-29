#!/bin/bash
###############################################
###############################################
# dumpbaseline.sh
# Part of Adore Project
# Batuhan Osmanoglu, Aug 2007 CSTARS, Miami
#
#
# This function reads the *.par files and 
# renames the data folder with Orbit Numbers.
#
# Requires: (Run in data folder)
#	- *.par pattern
# Provides:
#	- Renames data folders
#
###############################################
###############################################

### Handle input
if [ $# != 1 ]; then
	echo " Usage: $0 project_inputfile"
	exit 127
fi

Pattern=$1

ls ${Pattern} > scratchfilelist

for ParFile in `cat scratchfilelist`
do
	OrbitNr=`grep OrbitNr ${ParFile} | grep -v Date| head -n1 |tr -d "\n" | cut -f2 -d: | tr -d [:blank:]`
	#grep OrbitNr ${ParFile} | grep -v Date| head -n1| tr -d "\n" | cut -f2 -d:
	FolderName=`dirname ${ParFile}`
	echo "mv ${FolderName} ${OrbitNr}"
	mv ${FolderName} ${OrbitNr}
done
rm scratchfilelist