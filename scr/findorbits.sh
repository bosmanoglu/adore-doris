#!/bin/bash

nargs=$#
if [ $nargs -ne 2 ]
then
   echo " "
   echo " findorbits.sh - Part of ADORE package"
   echo " Batuhan Osmanoglu - CSTARS 2005"
   echo " Usage: "
   echo "        findorbits.sh ResFile OrbitRoot"
   echo " ResFile - Doris result file after successful M_READ"
   echo " OrbitRoot - Root directory with all orbit folders in it. Orbits should be organized by satellite name."
   echo " i.e. Ers1, Ers2, Rsat1"
   echo " "
   exit 1
fi

SLCFile=$1
OrbitRoot=$2
Platform=`grep Volume_identifier $SLCFile | cut -d: -f2 | tr -d [:blank:]`
t=`grep "Volume_set_identifier" $SLCFile | cut -d: -f2 | tr -d [:blank:] |cut -c1-14`

if [[ ${Platform} == ERS1* ]]; then
	OrbitPlatformRoot=${OrbitRoot}/ODR.ERS-1
elif [[ ${Platform} == ERS2* ]]; then
	OrbitPlatformRoot=${OrbitRoot}/ODR.ERS-2
elif [[ ${Platform} == dummy ]]; then
	OrbitPlatformRoot=${OrbitRoot}/ODR.ENVISAT1
else
	echo "Undefined Platform. Using Delft Orbits with Radarsat or Alos?" >&2
	OrbitPlatformRoot=${OrbitRoot}
fi
ls -F $OrbitPlatformRoot | grep "/" |tr -d "/" > scratchorbitfolders

echo "DEBUG: Platform: ${Platform}" >&2

for OrbitFolder in `cat scratchorbitfolders`
do
	result=`getorb t=$t ${OrbitPlatformRoot}/${OrbitFolder}`
	if [ ${#result} -gt 1 ]; then
		echo ${OrbitPlatformRoot}/${OrbitFolder}
		rm -rf scratchorbitfolders
		exit 0
	fi
	
done
exit 1

