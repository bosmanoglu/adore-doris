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
	echo "        dist is used for north-south (latitudal) distance(height)"
	echo "        dist2 is used for east-west (longitudal) distance(width)"
	echo " "
	echo " Output:"
	echo " Decimal Degrees with the following order: (For makedem.pl)"
	echo " West East South North "
	echo " "
	echo " Example:"
	echo " ${0} 19.5803 -98.8733 15"
	echo "-98.9640 -98.7826 19.5128 19.6478"
	echo " ${0} 19.5803 -98.8733 15 15"
	echo "-98.9640 -98.7826 19.5128 19.6478"
	exit 1
fi

lat_center=${1}
lon_center=${2}
dist=${3}

### Calculate distance in degrees
Ndeg=`echo "scale=4; ${dist} / 111" | bc -l`


#echo args..${args}..
if [ ${args} -eq 4 ]  
then
	dist2=${4}
	Edeg=`echo "scale=4; 360 * ${dist2} / sqrt( (2*3.1415*6356.750*c(${lat_center}))^2 )" | bc -l`
	Edeg=`echo "scale=4;pi=3.1415;360*${dist2}/(2*3.1415*6356.750*sqrt(c(${lat_center}/180*pi)^2))" |bc -l`
	#echo "scale=4; 360 * ${dist2} / sqrt( (2*3.1415*6356.750*c(${lat_center}))^2 )"
else
	Edeg=`echo "scale=4;pi=3.1415; 360 * ${dist}/(2*3.1415*6356.750*sqrt(c(${lat_center}/180*pi)^2)) " | bc -l`	
fi
#echo ..dN..${Ndeg}..
#echo ..dE..${Edeg}..
South=`echo "scale=4; ${lat_center}-(${Ndeg}/2)"|bc -l `
North=`echo "scale=4; ${lat_center}+(${Ndeg}/2)"|bc -l `
East=`echo "scale=4; ${lon_center}+(${Edeg}/2)" |bc -l `
West=`echo "scale=4; ${lon_center}-(${Edeg}/2)" |bc -l `
### Print results
echo ${West} ${East} ${South} ${North}