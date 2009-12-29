#!/bin/bash
#Input:
# readres.sh "inputfile" "section" "parameter"

inputfile=${1}
section=${2}
parameter=${3}
startline=`grep -n _Start_${section} ${inputfile} | cut -f1 -d":"`
endline=`grep -n End_${section} ${inputfile} | cut -f1 -d":"`

length=`echo ${endline} - ${startline} |bc`
result=`grep -A ${length} _Start_${section} ${inputfile} | grep ${parameter}`
#echo $result

result=${result##*:} 	#Get the part after the LAST column 

#echo "$startline $endline $length $parameter_length"
#echo "$parameter"
echo $result
