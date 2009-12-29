#!/bin/bash
###############################################
###############################################
# dumpbaseline.sh
# Part of Adore Project
# Batuhan Osmanoglu, Aug 2007 CSTARS, Miami
#
#
# This function reads the *.res files and dumps
# the perpendicular and temporal baselines as
# well as the doppler center freq, linear and 
# quadratic rates from doris files.
#
# Requires:
#	( In the FUTURE- Adore project_input_file (project.set))
#	- FORNOW it is the baseline.drs pattern
# Provides:
#	- ProjectFolder/temp/bl_list.txt
#
###############################################
###############################################

### Handle input
if [ $# != 1 ]; then
	echo " Usage: $0 project_inputfile"
	exit 127
fi


CropsFolder=${1}

ls -F ${CropsFolder}  > scratchfolderlist

for SLCFolder in `cat scratchfolderlist`
do
	SlaveResFile=`grep S_RESFILE ${SLCFolder} | tr -d " "`
	length=${#SlaveResFile}
	let length-=9 
	SlaveResFile=${SlaveResFile:9:length}
	#echo $SlaveResFile
	BaselineResFile=`grep I_RESFILE ${SLCFolder} | tr -d " "`
	length=${#BaselineResFile}
	let length-=9 
	BaselineResFile=${BaselineResFile:9:length}

	BTemp=`grep "Btemp" ${BaselineResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "btemp: ${BTemp}"
	BPerp=`grep "Bperp" ${BaselineResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "bPerp: ${BPerp}"
	BPar=`grep "Bpar" ${BaselineResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "bpar: ${BPar}"
	DC=`grep "Xtrack_f_DC_constant" ${SlaveResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "DC: ${DC}"
	DC_v=`grep "Xtrack_f_DC_linear"  ${SlaveResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "DC_v: ${DC_v}"
	DC_a=`grep "Xtrack_f_DC_quadratic" ${SlaveResFile} | cut -f2 -d: | cut -f1 -d/ | tr -d [:blank:]`
	#echo "DC_a: ${DC_a}"
		
	#line=$(printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" $SLCFolder $BTemp $BPerp $BPar $DC $DC_v $DC_a $SLCFolder )
	line=$(printf "%s\t%s\t%s\t%s\t%s\t%s" $SLCFolder $BTemp $BPerp $BPar $DC $SLCFolder )
#	echo $line
        echo $line >> baselines.txt

done

