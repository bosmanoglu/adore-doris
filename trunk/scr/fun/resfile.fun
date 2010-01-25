#!/bin/bash

dorisProcess2OutputFile_outputs=(filename resfile format numpixels numlines);
function dorisProcess2OutputFile(){
# Usage:
#  dorisProcess2OutputFile dorisStep [searchparameter]
# ex:
#  call (filename resfile format numpixels numlines)=dorisProcess2OutputFile subttrefpha 
#  call (filename resfile format numpixels numlines)=dorisProcess2OutputFile geocode Data_output_file_hei
  dorisStep=${1}
  parameter=${2:-Data_output_file} #search parameter
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
    resultFile=${m_resfile};
  elif [[ -n "${grepS}" ]]; then
    resultFile=${s_resfile};
  elif [[ -n "${grepI}" ]]; then 
    resultFile=${i_resfile};
  else
    echo "I couldn't find that step in the resultfiles. Please check your master and slave settings are correct."
    return;
  fi

  echo "Reading file information from: ${resultFile}"
  # get nr of lines
  firstPixel=`readRes.sh ${resultFile} ${dorisStep} First_pixel`
  lastPixel=`readRes.sh ${resultFile} ${dorisStep} Last_pixel`
  numPixels=$((${lastPixel}-${firstPixel}+1));
  # get nr of lines
  firstLine=`readRes.sh ${resultFile} ${dorisStep} First_line`
  lastLine=`readRes.sh ${resultFile} ${dorisStep} Last_line`
  numLines=$((${lastLine}-${firstLine}+1));
  
  #readRes.sh ${resultFile} ${dorisStep} Data_output_file notify
  ##########################TO DO - REFER TO READRES INSTEAD OF COPY PASTING IT HERE#########
  inputfile=${resultFile}
  section=${dorisStep}
  notify=notify
  grepStart=`grep -n Start_${section} ${inputfile} | cut -f1 -d":"`
  grepEnd=`grep -n End_${section} ${inputfile} | cut -f1 -d":"`

  grepLength=`echo ${grepEnd} - ${grepStart} |bc`
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
        return -1; 
      else
        #get the format
        format=`grep -A ${grepLength} Start_${section} ${inputfile} | grep "Data_output_format" |awk "NR==${line2Read}"`
        format=${format##*:}    #Get the part after the LAST column
      fi
    else
      result=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}`
      format=`readRes.sh ${resultFile} ${dorisStep} Data_output_format`
    fi
  else
    result=`grep -A ${grepLength} Start_${section} ${inputfile} | grep ${parameter}`
    format=`readRes.sh ${resultFile} ${dorisStep} Data_output_format`
  fi
  result=${result##*:} 	#Get the part after the LAST column 
  result=${result%%//*}	# Remove the part after // (trailing comment)
  #echo "$startline $endline $length $parameter_length"
  #echo "$parameter"
  #echo $result

  fileName=${result}
  ########################## END OF READRES.
}