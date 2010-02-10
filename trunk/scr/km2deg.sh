#!/bin/bash
args=$#
if [ ${args} -lt 3 ] 
then
	echo " USAGE: ${0} lat lon dist [dist2]"
	echo " "
	echo " lat: Decimal Degree Latitude of center coordinate"
	echo " lon: Decimal Degree Longitude of center coordinate"
	echo " dist: Distance in [km] to be converted to decimal degrees"
	echo " dist2: Optional parameter. If present instead of using dist for both east-west and north-south"
	echo "        dist is used for north-south (latitudal) distance."
	echo "        dist2 is used for east-west (longitudal) distance."
	echo " "
	echo " Example:"
	echo " ${0} 19.5803 -98.8733 15"
	echo ".1351 .1815"
	echo " ${0} 19.5803 -98.8733 15 15"
	echo ".1351 .1815"
	exit 1
fi

lat_center=${1}
lon_center=${2}
dist=${3}

### Calculate distance in degrees
#Ndeg=`echo "scale=4; ${dist} / 111" | bc -l`
Ndeg=`echo "${dist}"| awk '{printf "%0.6f", $1/111};'`

if [ ${args} -eq 4 ]  
then
	dist2=${4}
	#Edeg=`echo "scale=4; 360 * ${dist2} / (2*3.1415*6356.750*c(${lat_center}))" | bc -l`
	Edeg=`echo "${dist2} ${lat_center}" | awk '{PI=3.14159;printf "%0.6f", 360*$1/(2*PI*6356.750*cos($2/180*PI))};'`
else
	#Edeg=`echo "scale=4; 360 * ${dist} / (2*3.1415*6356.750*c(${lat_center}))" | bc -l`	
	Edeg=`echo "${dist} ${lat_center}" | awk '{PI=3.14159;printf "%0.6f", 360*$1/(2*PI*6356.750*cos($2/180*PI))};'`
fi


### Print results
echo ${Ndeg} ${Edeg}