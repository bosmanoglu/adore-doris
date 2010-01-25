#!/bin/bash

dorisProcess2OutputFile_outputs=(_filename _resfile _format _numpixels _numlines);
function dorisProcess2OutputFile(){
# Usage:
#  dorisProcess2OutputFile dorisStep [searchparameter]
# ex:
#  call (filename resfile format numpixels numlines)=dorisProcess2OutputFile subttrefpha 
#  call (filename resfile format numpixels numlines)=dorisProcess2OutputFile geocode Data_output_file_hei
  local dorisStep=${1}
  local parameter=${2:-Data_output_file} #search parameter
  local grepM grepS grepI resfile firstPixel lastPixel numpixels multilookfactorPixels
  local firstLine lastLine numlines multilookfactorLines inputfile section notify grepStart grepEnd grepLength
  local numHits matchingLine result format filename
  #find which resfile to read.
  if [[ ${dorisStep} == m_* ]]; then
    dorisStep=`pn2rs ${dorisStep}`
    grepM=`grep ${dorisStep} ${m_resfile}`
  elif [[ ${dorisStep} == s_* ]]; then
    dorisStep=`pn2rs ${dorisStep}`
    grepS=`grep ${dorisStep} ${s_resfile}`
  else
    #find which result file has info
    # resample is a interfero step but outputs to s etc.
    dorisStep=`pn2rs ${dorisStep}`
    grepM=`grep ${dorisStep} ${m_resfile}`
    grepS=`grep ${dorisStep} ${s_resfile}`
    grepI=`grep ${dorisStep} ${i_resfile}`
  fi

  if [[ -n "${grepM}" ]]; then
    resfile=${m_resfile};
  elif [[ -n "${grepS}" ]]; then
    resfile=${s_resfile};
  elif [[ -n "${grepI}" ]]; then 
    resfile=${i_resfile};
  else
    echo "I couldn't find that step in the resultfiles. Please check your master and slave settings are correct."
    return;
  fi

  echo "Reading ${dorisStep} information from: ${resfile}"
  # get nr of lines
  firstPixel=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} First_pixel`
  lastPixel=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} Last_pixel`  
  numpixels=$((${lastPixel}-${firstPixel}+1));
  multilookfactorPixels=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} Multilookfactor_range_direction`
  [ "${multilookfactorPixels}" -gt 1 ] && numpixels=`echo ${numpixels} ${multilookfactorPixels} | awk '{printf "%d", $1/$2};'`
  # get nr of lines
  firstLine=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} First_line`
  lastLine=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} Last_line`
  numlines=$((${lastLine}-${firstLine}+1)); 
  multilookfactorLines=`${ADORESCR}/readRes.sh ${resfile} ${dorisStep} Multilookfactor_azimuth_direction`
  [ "${multilookfactorLines}" -gt 1 ] && numlines=`echo ${numlines} ${multilookfactorLines} | awk '{printf "%d", $1/$2};'`
  #readRes.sh ${resfile} ${dorisStep} Data_output_file notify
  ##########################TO DO - REFER TO READRES INSTEAD OF COPY PASTING IT HERE#########
  inputfile=${resfile}
  section=${dorisStep}
  notify=notify
  grepStart=`grep -n Start_${section} ${inputfile} | cut -f1 -d":"`
  grepEnd=`grep -n End_${section} ${inputfile} | cut -f1 -d":"`

  grepLength=$((${grepEnd}-${grepStart}));
  if [[ "${notify}" == "notify" ]]; then
    #get number of hits
    numHits=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}|wc -l`    
    if [[ ${numHits} -gt 1 ]]; then
      echo " "
      echo "I found more than 1 match for your selection."    
      echo "Please enter the selection you want me to use."
      for (( c=1; c<=${numHits}; c++ ))
      do
        matchingLine=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}|awk "NR==${c}"`
        echo $c : ${matchingLine}      
      done
      read -p "Please enter number between 1 and $((${c} -1)): " -e line2Read
      result=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}|awk "NR==${line2Read}"`    	    
      if [ -z "${result}" ]; then
        echo "Something went wrong."
        echo "Exiting..."
        return; 
      else
        #get the format
        format=`grep -A ${grepLength} Start_${section} ${inputfile} | grep "Data_output_format" |awk "NR==${line2Read}"`
        format=${format##*:}    #Get the part after the LAST column
      fi
    else
      result=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}`
      format=`readRes.sh ${resfile} ${dorisStep} Data_output_format`
    fi
  else
    result=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}`
    format=`readRes.sh ${resfile} ${dorisStep} Data_output_format`
  fi
  result=${result##*:} 	#Get the part after the LAST column 
  result=${result%%//*}	# Remove the part after // (trailing comment)
  #echo "$startline $endline $length $parameter_length"
  #echo "$parameter"
  #echo $result

  filename=${result//[[:space:]]}
  ########################## END OF READRES.
  [ "${format//[[:space:]]}" == "complex_real4" ] && format="cr4";
  [ "${format//[[:space:]]}" == "complex_short" ] && format="ci2";
  [ "${format//[[:space:]]}" == "real4" ] && format="r4";
  [ "${format//[[:space:]]}" == "short" ] && format="i2";
  
  _filename=${filename};_resfile=${resfile};_format=${format};_numpixels=${numpixels};_numlines=${numlines}
}

