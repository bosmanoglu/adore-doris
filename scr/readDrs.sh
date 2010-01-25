#!/bin/bash
nargs=$#
if [ ${nargs} -lt 2 ]
then 
cat<<_EOF
USAGE: readDrs.sh drsFile parameter

INPUT:
  drsFile: is the DORIS input file (*.drs)
  parameter: field to be read in the file. 

OUTPUT: 
  parameter value

LIMITATIONS:
If the value of the parameter has ":" character the returned field might be wrong.

EXAMPLE:
	$> ./readDrs.sh /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/readfiles.drs M_IN_DAT
	/data/batu/adore_MexicoCity2/data/09828/dat.040116_ENVISAT1_163630.001_SLC
	$> ./readDrs.sh /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/readfiles.drs LOGFILE
	/data/batu/adore_MexicoCity2/process/20by20/crops/09828/log.out
	$> ./readDrs.sh /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/crop.drs DUMPBASELINE
	15 10
_EOF
exit 1
fi
#Input:
# readDrs.sh "inputfile" "parameter"

inputfile=${1}
parameter=${2}

result=`grep ${parameter} ${inputfile} `
#echo $result
result=`echo $result | tr -s " "`
#echo $result
result=`echo $result | cut -f2- --delimiter=" "`
#echo $result
#I don't know why this was here... but removes last zero removed 20100124. #result=${result%%\0}
#echo $result 
result2=`echo $result | awk -F" // " '{print $1}' `
#echo $result2
#echo RESULT IS:
if [ -z "$result2" ]
then
	echo $result
else
	echo $result2
fi

