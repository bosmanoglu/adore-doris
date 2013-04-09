#!/bin/bash
nargs=$#
if [ ${nargs} -lt 4 ]
then 
cat<<_EOF
USAGE: 
  modifyRes.sh resultFile dorisStep parameter newValue

INPUT:
  resultFile: is the DORIS result file (*.res)
  dorisStep: is the processing step to look for the parameter.
  parameter: field to be read in the result file. The column character should not be included.
  	i.e. "Last_pixel (w.r.t. original_image)" is valid 
  	     "Last_pixel (w.r.t. original_image):" is not valid.
  newValue: modified setting for the field

OUTPUT: 
  Edits the original file. Replacement might not match the original line in terms of whitespace. This is not a problem for doris.

LIMITATIONS:

EXAMPLE:
  modifyRes.sh "11331_09828/11331.res" crop 'First_line (w.r.t. original_image)' 11733
 
_EOF
exit 1
fi
#Input:
# readres.sh "inputfile" "section" "parameter"

inputFile=${1}
section=${2}
parameter=${3}
newValue=${4}
startline=`grep -n _Start_${section} ${inputFile} | cut -f1 -d":"`
endline=`grep -n End_${section} ${inputFile} | cut -f1 -d":"`
#echo $startline
#echo $endline

length=`echo ${endline} - ${startline} |bc`
resultPos=`grep -n -A ${length} "_Start_${section}" ${inputFile} | grep "${parameter}" |head -n1| cut -f1 -d"-"`
sed -i ${resultPos}c\ "${parameter}: ${newValue}" ${inputFile}
##echo $resultPos
#count=1 #counting lines from 1
#cat ${inputFile} | while read line; do
#	if [[ $count -eq $resultPos ]]; then
#		echo "${parameter}: ${newValue}"
#	else
#		echo "${line}"
#	fi
#	let count=${count}+1
#done
exit 0

#echo "$startline $endline $length $parameter_length"
#echo "$parameter"
