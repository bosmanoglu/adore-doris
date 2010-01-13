#!/bin/bash
function getLastProcess {
	resfile=${1}
	#echo ${resfile}
	startLine=`grep -n "Start_process_control" ${resfile} | cut -d: -f1`		
	#echo ${startLine}
	endLine=`grep -n "End_process_control" ${resfile} | cut -d: -f1`
	#echo ${endLine}
	if [ "${endline}" != "${startLine}" ]; then	
		length=`echo ${endLine} - ${startLine} | bc`
		#echo inside
		#echo ${length}
		lastProcess=`grep -A${length} Start_process_control ${resfile}| grep 1| tail -n 1| cut -d: -f1`
	fi
}	
if [ $# -eq 1 ]; then
	i_resfile=${1}
fi
#echo ${i_resfile}

#check if interfero started
if [ -e ${i_resfile} ]; then
	getLastProcess ${i_resfile}
fi
#echo $lastProcess
[ -n "${lastProcess}" ] && echo ${lastProcess}; exit 0
#check if slave is there
if [ -e ${s_resfile} ]; then
	getLastProcess ${s_resfile}
fi
[ -n "${lastProcess}" ] && echo ${lastProcess}; exit 0
#check if master is there
if [ -e ${m_resfile} ]; then
	getLastProcess ${m_resfile}
fi
