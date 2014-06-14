#!/bin/bash
# USAGE: 
#  copyRes.sh fromResultFile fromDorisStep [toResultFile toDorisStep]
#
# INPUT:
#  fromResultFile: is the input DORIS result file (*.res). fromDorisStep will be
#  	read from this file.
#  fromDorisStep: is the processing step to copy.
#
#  OPTIONAL INPUT:  	
#  toResultFile: is the output DORIS result file (*.res). toDorisStep will be
#  	written to this file. If omitted same as fromResultFile.
#  toDorisStep: can be omitted if same as fromDorisStep.
#  
# OUTPUT: 
#  New step in toResultFile.
#
# LIMITATIONS:
#  If toDorisStep already exists in toResultFile, no action is taken.
#  Even if the output parameter=value structure is different between fromDorisStep 
#  and toDorisStep, copy is made as is.
#  
# EXAMPLE:
#  copyRes.sh "11331_09828/11331.res" crop resample
#
function usage(){
 sed -n -e '/^# USAGE:/,/^$/ s/^# \?//p' < `which ${0}`
}

function funCopyRes(){
  local fResFile fSection tResFile tSection
  fResFile="${1}"
  fSection="${2}"
  if [ $# -eq 4 ]; then
    tResFile="${3}"
    tSection="${4}"
  elif [ $# -eq 3 ]; then
    if [ -e "${3}" ]; then
      tResFile="${3}"
      tSection="${fSection}"
    else
      tSection="${3}"
      tResFile="${fResFile}"
    fi
  fi
  echo "running with options: " ${fResFile} ${fSection} ${tResFile} ${tSection}
  
  local status
  
  status=`readRes.sh ${tResFile} "process_control" ${tSection}`
  if [ $? -eq 0 ] && [ ${status} -eq 0 ]; then
    sed -i -e "/^${tSection}/s/0/1/g" ${tResFile}
    echo "*******************************************************************" >> ${tResFile}
    echo "*_Start_${tSection}:                   " >> ${tResFile}
    sed -n "/_Start_${fSection}/,/End_${fSection}/p" ${fResFile} | sed -n '/\*\*\*\*\*\*/,/\*\*\*\*\*\*/p'  >> ${tResFile}
    echo "* End_${tSection}:_NORMAL" >> ${tResFile}
    echo "*******************************************************************" >> ${tResFile}
    echo "Process ${fSection} from ${fResFile} was copied to ${tResFile} as ${tSection} successfully."
  else
    echo "Process already in result file. Please remove ${tSection} from ${tResFile} first."
  fi
}

### MAIN
nargs=$#
if [ ${nargs} -lt 3 ]
then 
  usage
  exit 1
fi

funCopyRes "${@}"
