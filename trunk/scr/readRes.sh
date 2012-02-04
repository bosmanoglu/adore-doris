#!/bin/bash
nargs=$#
if [ ${nargs} -lt 3 ]
then 
cat<<_EOF
USAGE: readRes.sh resultFile dorisStep parameter [notify]

INPUT:
  resultFile: is the DORIS result file (*.res)
  dorisStep: is the processing step to look for the parameter.
  parameter: field to be read in the result file. If the parameter includes a column(:) character
   	     value of the parameter is returned. (See last example.)
  notify:    Default is "off". If "on", will warn user in case multiple lines matched the search parameter.
  
OUTPUT: 
  parameter value from the result file. 

LIMITATIONS:
If the value of the parameter has ":" character the returned field might be wrong.

EXAMPLE:
  $> readRes.sh  /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/09828.res readfiles RADAR_FREQUENCY
    5331004416.000000
  $> readRes.sh /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/09828.res readfiles First_pixel_azimuth_time
    31.238
  $> grep First_pixel_azimuth_time /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/09828.res 
    First_pixel_azimuth_time (UTC):                 16-JAN-2004 16:36:31.238
  $> readRes.sh /RAID1/batu/adore_MexicoCity2/process/20by20/crops/09828/09828.res readfiles "First_pixel_azimuth_time (UTC):"
    22-Jan-2005 16:45:5.449159
_EOF
exit 1
fi
#Input:
# readres.sh "inputfile" "section" "parameter"

inputfile=${1}
section=${2}
parameter=${3}
notify=${4:-off}
startline=`grep -n Start_${section} ${inputfile} | cut -f1 -d":"`
endline=`grep -n End_${section} ${inputfile} | cut -f1 -d":"`
length=`echo ${endline} - ${startline} |bc`

[ -z "${length}" ] && echo -e "ERROR: Can not find section." >&2 && return; #If can not determine section, no need to run further.

if [[ "${notify}" == "notify" ]]; then
  #get number of hits
  numHits=`grep -A ${length} Start_${section} ${inputfile} | grep "${parameter}"|wc -l`
  if [[ ${numHits} -gt 1 ]]; then
    echo " "
    echo "I found more than 1 match for your selection."    
    echo "Please enter the selection you want me to use."
    for (( c=1; c<=${numHits}; c++ ))
    do
      matchingLine=`grep -A ${length} Start_${section} ${inputfile} | grep "${parameter}"|awk "NR==${c}"`
      echo $c : ${matchingLine}      
    done
    read -p "Please enter number between 1 and $((${c} -1)): " -e line2Read
    result=`grep -A ${length} Start_${section} ${inputfile} | grep "${parameter}"|awk "NR==${line2Read}"`    
    if [ -z "${result}" ]; then
      echo "Something went wrong."
      echo "Exiting..."
      return; 
    fi
  fi
else
  result=`grep -A ${length} Start_${section} ${inputfile} | grep "${parameter}"`
fi

if [[ ${parameter} == *:* ]]; then
  result=${result//${parameter}};
else
  result=${result##*:} 	#Get the part after the LAST column 
fi
result=${result%%//*}   #delete everything after //

#echo "$startline $endline $length $parameter_length"
#echo "$parameter"
echo $result
